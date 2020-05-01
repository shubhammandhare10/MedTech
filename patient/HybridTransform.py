import numpy as np
import cv2
import math
from decimal import Decimal
from scipy.fftpack import dct
import pywt
import sys
import pandas as pd

np.set_printoptions(suppress=False, linewidth=9999)

def haar(n):
	haar_ini = np.matrix('1 1; 1 -1', dtype=np.float64)
	upperMat = np.kron(haar_ini, np.matrix('1 1'))
	lowerMat = np.kron(np.identity(2), np.matrix('1 -1'))
	haarMat = np.concatenate((upperMat, lowerMat))
	haarMat = haarMat + 0

	if n == 2:
		return haar_ini

	n = n/2

	i = 2
	while i != n:
		haar_ini = haarMat
		upperMat = np.kron(haar_ini, np.matrix('1 1'))
		lowerMat = np.kron(np.identity(2*i), np.matrix('1 -1'))
		haarMat = np.concatenate((upperMat, lowerMat))
		haarMat = haarMat + 0
		i = i*2

	return haarMat

# mat1 size should be greater than mat2 size
def hybridTransform(mat1, mat2):
	print(mat1.shape[0], mat2.shape[0])
	origMat1Size = mat1.shape[0]
	origMat2Size = mat2.shape[0]

	if origMat2Size > origMat1Size:
		temp = mat2
		mat2 = mat1
		mat1 = temp

	print(mat1.shape[0], mat2.shape[0])

	mat1Rows = mat1.shape[0]
	mat1Cols = mat1.shape[1]
	mat2Rows = mat2.shape[0]
	mat2Cols = mat2.shape[1]

	resCols = mat2Cols*mat1Rows
	resLowerRows = int(resCols/mat1Cols)

	resUpper = np.zeros((mat2Rows, resCols))

	l = []

	for i in range(mat2Cols):
		for j in range(mat1Rows):
			l.append(mat1[0,j] * mat2[:,i])

	l = np.asarray(l)

	if origMat2Size > origMat1Size:
		for i in range(resCols):
			resUpper[:,[i]] = l[i]

	else:
		for i in range(resCols):
			resUpper[:,i] = l[i]


	resLowerList = []
	for matRow in range(mat1Rows-1):
		resLower = np.zeros((resLowerRows, resCols))
		for i in range(resLowerRows):
			resLower[i][mat1Cols*(i):mat1Cols*(i+1)] = mat1[matRow+1]
		resLowerList.append(resLower)

	resLowerFinal = np.concatenate(resLowerList, axis=0)

	res = np.concatenate((resUpper, resLowerFinal), axis=0)

	return res

def hybridTransformation(imgResize, hybridTransformMat):
	blue, green, red = cv2.split(imgResize)

	imgSize = int(imgResize.shape[0])

	for idx, val in enumerate([blue, green, red]):
		res1 = np.matmul(hybridTransformMat, val)
		imgTransformed = np.matmul(res1, hybridTransformMat.transpose())
		imgTransformedScaleAbs = cv2.convertScaleAbs(imgTransformed)

		'''cv2.imshow("Scaled Transformed Image", imgTransformedScaleAbs)
		cv2.waitKey(100)'''

		if idx==0:
			blueTransformed = imgTransformedScaleAbs
		elif idx==1:
			greenTransformed = imgTransformedScaleAbs
		elif idx==2:
			redTransformed = imgTransformedScaleAbs

	imgSize_8 = int(imgSize/8)
	imgSize_16 = int(imgSize/16)
	imgSize_64 = int(imgSize_16/4)

	blueFeatures64 = blueTransformed[:imgSize_8,:imgSize_8]
	greenFeatures64 = greenTransformed[:imgSize_8,:imgSize_8]
	redFeatures64 = redTransformed[:imgSize_8,:imgSize_8]

	blueFeatures32 = blueTransformed[:imgSize_16,:imgSize_16]
	greenFeatures32 = greenTransformed[:imgSize_16,:imgSize_16]
	redFeatures32 = redTransformed[:imgSize_16,:imgSize_16]

	blueFeatures64 = blueFeatures64.flatten('C')
	greenFeatures64 = greenFeatures64.flatten('C')
	redFeatures64 = redFeatures64.flatten('C')

	blueFeatures32 = blueFeatures32.flatten('C')
	greenFeatures32 = greenFeatures32.flatten('C')
	redFeatures32 = redFeatures32.flatten('C')

	blueFeatures8 = blueTransformed[:imgSize_64,:imgSize_64]
	greenFeatures8 = greenTransformed[:imgSize_64,:imgSize_64]
	redFeatures8 = redTransformed[:imgSize_64,:imgSize_64]

	blueFeatures8 = blueFeatures8.flatten('C')
	greenFeatures8 = greenFeatures8.flatten('C')
	redFeatures8 = redFeatures8.flatten('C')

	return blueFeatures64, greenFeatures64, redFeatures64, blueFeatures32, greenFeatures32, redFeatures32, blueFeatures8, greenFeatures8, redFeatures8

def main():
	haarSize = 128
	haarMat = haar(haarSize)

	for i in range(haarSize):
		haarMat[i] = haarMat[i]/math.sqrt(abs(haarMat[i]).sum())

	haarMatTranspose = haarMat.transpose()

	dctMat = dct(np.eye(4), norm='ortho')
	dctMatTranspose = dctMat.transpose()

	#HaarMat to be passed first
	hybridTransformMat = hybridTransform(haarMat, dctMatTranspose)

	print("Hybrid Normal Check\n", hybridTransformMat @ hybridTransformMat.transpose())

	start = int(sys.argv[1])
	end = int(sys.argv[2])
	print(start, end)

	if start == None:
		print("Start not specified, setting to 1")
		start = 1

	if end == None:
		print("End not specified, setting to 5")
		end = 5

	if start > end:
		print("Start > End")
		sys.exit(0)

	for x in ("Benign", "Malignant"):
		print(x)
		if x == "Benign":
			fName = "B_"
		if x == "Malignant":
			fName = "M_"

		for f in range(start, end+1):
			print(x + str(f))
			img = cv2.imread("/home/gaurav/BE Project/ISIC Complete/" +  x + "/Images/" + fName + str(f) + ".jpg")
			imgResize = cv2.resize(img, (512, 512), interpolation = cv2.INTER_AREA)

			bFeatures64, gFeatures64, rFeatures64, bFeatures32, gFeatures32, rFeatures32, bFeatures8, gFeatures8, rFeatures8 = hybridTransformation(imgResize, hybridTransformMat)

			bFeatures64 = bFeatures64.reshape((1,bFeatures64.shape[0]))
			gFeatures64 = gFeatures64.reshape((1,gFeatures64.shape[0]))
			rFeatures64 = rFeatures64.reshape((1,rFeatures64.shape[0]))

			bFeatures32 = bFeatures32.reshape((1,bFeatures32.shape[0]))
			gFeatures32 = gFeatures32.reshape((1,gFeatures32.shape[0]))
			rFeatures32 = rFeatures32.reshape((1,rFeatures32.shape[0]))

			diagnosisMat = np.full((1,1), x)

			features64 = np.concatenate((bFeatures64,gFeatures64,rFeatures64,diagnosisMat), axis=1)

			features32 = np.concatenate((bFeatures32,gFeatures32,rFeatures32,diagnosisMat), axis=1)

			bFeatures8 = bFeatures8.reshape((1,bFeatures8.shape[0]))
			gFeatures8 = gFeatures8.reshape((1,gFeatures8.shape[0]))
			rFeatures8 = rFeatures8.reshape((1,rFeatures8.shape[0]))

			features8 = np.concatenate((bFeatures8,gFeatures8,rFeatures8,diagnosisMat), axis=1)

			if fName+str(f) == "B_1":
				headerVal = True
			else:
				headerVal = False

			pd.DataFrame(features64).to_csv("HybridTransformFeatures64-Haar"+str(haarSize)+
				"DCT"+str(dctMat.shape[0])+".csv", header=headerVal, mode='a', index=False)

			#pd.DataFrame(features32).to_csv("HybridTransformFeatures32-Haar"+str(haarSize)+
			#	"DCT"+str(dctMat.shape[0])+".csv", header=headerVal, mode='a', index=False)

			#pd.DataFrame(features8).to_csv("HybridTransformFeatures8-Haar"+str(haarSize)+
			#	"DCT"+str(dctMat.shape[0])+".csv", header=headerVal, mode='a', index=False)


	'''imgTransformedScaleAbs = cv2.convertScaleAbs(imgTransformed)

	cv2.imshow('Hybrid Transformed Image Scaled', imgTransformedScaleAbs)
	cv2.waitKey(20000)

	imgInverseTransformedScaleAbs = cv2.convertScaleAbs(imgInverseTransformed)
	cv2.imshow('Hybrid Inverse Transformed Image Scaled', imgInverseTransformedScaleAbs)
	cv2.waitKey(20000)

	fName = "HybridTransformed.png"
	cv2.imwrite(fName, imgTransformed)

	fName = "HybridInverseTransformed.png"
	cv2.imwrite(fName, imgInverseTransformed)

	count = 0
	for i in range(512):
		for j in range(512):
			if imgInverseTransformed[i][j].round(3) != blue[i][j].round(3):
				print(imgInverseTransformed[i][j], blue[i][j])
				count+=1

	print(count)'''

if __name__ == '__main__':
	main()
