from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import PatientInfoForm
from .models import Patient
from django.contrib.auth.decorators import login_required


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
            newPatientInfo.save()

# ENCRYPTION CODE
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            input_file = "media/patient/images/" + image
            encrypted_file = "encryptedImages/" + image

            with open(input_file, 'rb') as f:
                data = f.read()

            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)

            with open(encrypted_file, 'wb') as f:
                f.write(encrypted)
#
# # WEKA CODE
#
# #DECRYPTION CODE
            input_file = encrypted_file
            decrypted_file = "decryptedImages/" + image

            with open(input_file, 'rb') as f:
                data = f.read()

            fernet = Fernet(key)
            encrypted = fernet.decrypt(data)

            with open(decrypted_file, 'wb') as f:
                f.write(encrypted)

            newPatientInfo.result = 'Benign'
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
    return render(request, 'patient/viewpatientinfo.html',{'patientInfo':patientInfo})


@login_required
def deletepatientinfo(request,patient_pk):
    deletePatientInfo = get_object_or_404(Patient, pk=patient_pk, user=request.user)
    if request.method == "GET":
        return render(request, "patient/deletepatientinfo.html",{'deletePatientInfo':deletePatientInfo})
    else:
        deletePatientInfo.delete()
        return redirect('currentinfo')
