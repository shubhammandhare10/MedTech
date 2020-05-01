from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import PatientInfoForm
from .models import Patient
from django.contrib.auth.decorators import login_required
from cryptography.fernet import Fernet

import weka.core.jvm as JVM
from weka.classifiers import Classifier, Kernel
from weka.core.converters import Loader, Saver
from patient import HybridTransform as Hybrid
from scipy.fftpack import dct
import numpy as np
import math
import cv2
import pandas as pd
# Create your views here.

def home(request):
    return render(request, 'patient/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request,'patient/signupuser.html',{'form':UserCreationForm()})
    else:
        #POST - Create a new User
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currentinfo')
            except IntegrityError:
                return render(request,'patient/signupuser.html',{'form':UserCreationForm(), 'error':"That Username is taken already, please choose a new username"})
        else:
            #Tell user passwords didnt match
            return render(request,'patient/signupuser.html',{'form':UserCreationForm(), 'error':"Passwords Didnt Match"})

def loginuser(request):
    if request.method == 'GET':
        return render(request,'patient/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'] ,password=request.POST['password'])
        if user is None:
            return render(request,'patient/loginuser.html',{'form':AuthenticationForm(),'error':'Username and password didnt match'})
        else:
            login(request, user)
            return redirect('currentinfo')

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

@login_required
def createpatientinfo(request):
    if request.method == 'POST':
        try:
            form = PatientInfoForm(request.POST, request.FILES)
            newPatientInfo = form.save(commit=False)
            newPatientInfo.user = request.user
            image = request.FILES['Skin_image'].name
            print("*******************",image)

            newPatientInfo.image_name = image

            newPatientInfo.save()



# ******************************************** ENCRYPTION CODE ************************************************
            key = Fernet.generate_key()
            key = key.decode('utf-8')

            newPatientInfo.image_key = key
            newPatientInfo.save(update_fields=['image_key'])

            input_file = "media/patient/images/" + image
            encrypted_file = "encryptedImages/" + image

            with open(input_file, 'rb') as f:
                data = f.read()

            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)

            with open(encrypted_file, 'wb') as f:
                f.write(encrypted)


    # ***************************************************  DECRYPTION CODE ************************************************
            image = newPatientInfo.image_name
            input_file = encrypted_file
            decrypted_file = "decryptedImages/" + image
            key = newPatientInfo.image_key
            # print("************************************************",key)

            with open(input_file, 'rb') as f:
                data = f.read()

            fernet = Fernet(key)
            encrypted = fernet.decrypt(data)

            with open(decrypted_file, 'wb') as f:
                f.write(encrypted)

# -----------------------------------------------------  WEKA CODE  ---------------------------------------------------
            JVM.start(max_heap_size="4000m")

            clsfr,_ = Classifier.deserialize(r"patient\static\patient\Melanoma_Best_Performing_Weka3.8.model")
            haarSize = 8
            dctMat = dct(np.eye(64), norm='ortho')
            haarMat = Hybrid.haar(haarSize)

            for i in range(haarSize):
            	haarMat[i] = haarMat[i]/math.sqrt(abs(haarMat[i]).sum())

            hybridTransformMat = Hybrid.hybridTransform(haarMat, dctMat.transpose())

            fPath = "decryptedImages/"
            fName = image

            img = cv2.imread(fPath + fName)
            imgResize = cv2.resize(img, (512, 512), interpolation = cv2.INTER_AREA)

            bFeatures64, gFeatures64, rFeatures64, _, _, _, _, _, _ = Hybrid.hybridTransformation(imgResize, hybridTransformMat)

            bFeatures64 = bFeatures64.reshape((1,bFeatures64.shape[0]))
            gFeatures64 = gFeatures64.reshape((1,gFeatures64.shape[0]))
            rFeatures64 = rFeatures64.reshape((1,rFeatures64.shape[0]))
            diagnosisMat = np.full((1,1), "NA")

            features64 = np.concatenate((bFeatures64,gFeatures64,rFeatures64,diagnosisMat), axis=1)

            op_file_name = "arff_csv_files/HybridTransformFeatures64-Haar"+str(haarSize)+ "DCT"+str(dctMat.shape[0])+fName
            pd.DataFrame(features64).to_csv(op_file_name + ".csv", header=True, mode='a', index=False)

            csvLoader = Loader(classname="weka.core.converters.CSVLoader")
            data = csvLoader.load_file(op_file_name+".csv")

            arffSaver = Saver(classname="weka.core.converters.ArffSaver")
            arffSaver.save_file(data, op_file_name+".arff")

            arffLoader = Loader(classname="weka.core.converters.ArffLoader")
            arff_data = arffLoader.load_file(op_file_name+".arff")
            arff_data.class_is_last()

            diagnosis = ""
            for index, inst in enumerate(arff_data):
            	pred = clsfr.classify_instance(inst)
            	print(pred)
            	dist = clsfr.distribution_for_instance(inst)
            	print(dist)

            	if pred==1.0:
            		diagnosis = "Malignant"
            	else:
            		diagnosis = "Benign"

            print("Final Diagnosis: ***************************************************", diagnosis)
            JVM.stop()
# -----------------------------------------------------  WEKA CODE END ---------------------------------------------------


            newPatientInfo.result = diagnosis
            newPatientInfo.save(update_fields=['result'])

            return redirect('currentinfo')
        except ValueError:
            return render(request,'patient/createpatientinfo.html',{'form':PatientInfoForm(),"error":"Bad data passed in!"})
    else:
        return render(request,'patient/createpatientinfo.html',{'form':PatientInfoForm()})

@login_required
def currentinfo(request):
    patientsInfo = Patient.objects.filter(user=request.user).order_by('-created')
    return render(request,'patient/currentinfo.html',{'patientsInfo':patientsInfo})

@login_required
def viewpatientinfo(request,patient_pk):
    patientInfo = get_object_or_404(Patient, pk=patient_pk, user = request.user)

    # image = patientInfo.image_name
    # print("**********************************",image)
    #
    # key = patientInfo.image_key
    # print("----------------------------------",key)

    return render(request, 'patient/viewpatientinfo.html',{'patientInfo':patientInfo})


@login_required
def deletepatientinfo(request,patient_pk):
    deletePatientInfo = get_object_or_404(Patient, pk=patient_pk, user=request.user)
    if request.method == "GET":
        return render(request, "patient/deletepatientinfo.html",{'deletePatientInfo':deletePatientInfo})
    else:
        deletePatientInfo.delete()
        return redirect('currentinfo')
