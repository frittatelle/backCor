from dataBlock.dataBlock import Data
from dataReader.dataReader import DataReader
import numpy as np
import numpy.matlib as npm
import numpy.linalg as npl

import matplotlib
import matplotlib.pyplot as plt


class PolyApprox():
    def __init__(self,data,polyOrd,thr,costFun):
        self.pointsPerSpectrum = data.pointsPerSpectrum         # N
        self.ramanShift = data.ramanShift                       # n
        self.spectraData = data.spectraData                     # y
        self.polyOrd = polyOrd                                  # ord
        self.thr = thr                                          # s
        self.costFun = costFun                                  # fc


    def approx(self):
        # shrinking costFun
        self.costFunCode()
        # Standardize
        self.standardize()
        # Vandermonde matrix (stima matrice dei coefficienti)
        self.vandermondeMat()
        # Initialization
        self.initialize()
        # Estimation
        self.estimate()
        # Rescale
        self.rescale()

    def costFunCode(self):
        costFun = self.costFun
        if costFun == "Symmetric Huber function":
            self.costFun = "sh"
        elif costFun == "Asymmetric Huber function":
            self.costFun = "ah"
        elif costFun == "Symmetric truncated quadratic":
            self.costFun = "stq"
        elif costFun == "Asymmetric truncated quadratic":
            self.costFun = "atq"

    def standardize(self):
        maxF = np.amax(self.ramanShift)
        minF = np.amin(self.ramanShift)
        self.ramanShift = 2 * (self.ramanShift - maxF)/(maxF - minF) + 1
        self.maxD = np.amax(self.spectraData)
        self.minD = np.amin(self.spectraData)
        self.spectraData = 2 * (self.spectraData - self.maxD)/(self.maxD - self.minD) + 1

    def vandermondeMat(self):
        p = np.arange(0,self.polyOrd + 1)
        T1 = npm.repmat(self.ramanShift,self.polyOrd + 1,1)
        T1 = T1.T
        T2 = npm.repmat(p,self.pointsPerSpectrum,1)
        self.T = np.power(T1,T2)
        self.Tinv = np.dot(npl.pinv(np.dot(self.T.T,self.T)) , self.T.T)

    def initialize(self):
        # Coefficienti del polinomio approssimante
        self.polyCoeff = np.dot(self.Tinv,self.spectraData)
        # Polinomio approssimante
        self.spectraApprox = np.dot(self.T,self.polyCoeff)

        self.alpha = 0.99 * 0.5
        # Stima prior
        self.spectraApproxP = np.ones(self.pointsPerSpectrum)

    def estimate(self):
        while np.sum(np.power((self.spectraApprox - self.spectraApproxP),2)) / np.sum(np.power(self.spectraApproxP,2)) > 1e-9:

            self.spectraApproxP = self.spectraApprox       # Previous estimation
            res = self.spectraData - self.spectraApprox    # Residui
            alpha = self.alpha
            costFun = self.costFun
            thr = self.thr

            # Estiamte d
            if costFun == "sh":
                d = (res*(2*alpha-1)) * (np.abs(res)<thr) + (-alpha*2*thr-res) * (res<=-thr) + (alpha*2*thr-res) * (res>=thr);
            elif costFun == "ah":
                d = (res*(2*alpha-1)) * (res<thr) + (alpha*2*thr-res) * (res>=thr)
            elif costFun == "stq":
                d = (res*(2*alpha-1)) * (np.abs(res)<thr) - res * (np.abs(res)>=thr)
            elif costFun == "atq":
                d = (res*(2*alpha-1)) * (res<thr) - res * (res>=thr)

            # Estimate z
            self.polyCoeff = np.dot(self.Tinv,self.spectraData + d)
            self.spectraApprox = np.dot(self.T,self.polyCoeff)

    def rescale(self):
        self.spectraApprox = 0.5 * (self.maxD - self.minD) * (self.spectraApprox - 1) + self.maxD


class PolyApproxIdx(PolyApprox):
    def __init__(self,data,polyOrd,thr,costFun,idx):
        PolyApprox.__init__(self,data,polyOrd,thr,costFun)
        self.idx = idx
        self.spectraData = self.spectraData[idx]



# f = "C:/Users/Luca/Desktop/Lab/Backcor GUI/A _ Ca Apatite (variant 0) Ref.wdf"
# # f = "C:/Users/Luca/Desktop/Lab/Backcor GUI/A _ 01 176 A 18_Slice 10micron 785 1200 3sx1 MAP Step 8um_CR.wdf"
# dataR = DataReader(fileName = f)
# data = Data(dataR.pointsPerSpectrum,dataR.ramanShift,dataR.spectraData)
# polyApprox = PolyApprox(data,12,0.01,"sh")
