import os as os
import json
import numpy as np
from matplotlib.colors import is_color_like

class UserSettingsReader():

    def __init__(self):

        # Base path e Settings path
        basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.basePath = basePath
        settingsFilePath = os.path.join(basePath,"data\\userData\\settings.json")
        self.settingsFilePath = settingsFilePath

        self.positiveInt = ["nsLimit","minPolyOrd","maxPolyOrd"]
        self.negativeInt = ["minCntsAdj","maxCntsAdj"]
        self.positiveFloat = ["minThrVal","maxThrVal"]
        self.colors = ["plotColor","plotSelectedColor",
                  "plotApproxColor","tFrameBg","controlsTFrameBg",
                  "tLabelBg","tLabelFg"]
        self.other = ["skin"]


        # Setting valori di default
        self.setDefault()

        # Lettura settings.json
        j = self.readJson(settingsFilePath)

        # Check e loading user settings
        try:
            self.editSettings(j)
        except:
            pass


    def printSettings(self):
        for attr,val in self.__dict__.items():
            print(attr,": ",val)


    def editSettings(self,j):
        for attr,val in self.__dict__.items():
            if self.checkVal(attr,j):
                setattr(self,attr,j[attr])


    def checkVal(self,attr,j):
        f = False

        if attr in self.positiveInt:
            if j[attr] > 0: f = True
        elif attr in self.negativeInt:
            f = True
        elif attr in self.positiveFloat:
            if 0.01 <= j[attr] <= 0.1: f = True
        elif attr in self.colors:
            if is_color_like(j[attr]): f = True
        elif attr in self.other:
            skins = ["dark","white"]
            if j[attr] in skins:
                f = True

        return f


    def readJson(self,settingsFilePath):
        # Lettura seettings.json e aggiornamento settings se i valori sono validi
        j = {}
        try:
            with open(settingsFilePath) as f:
                data = json.load(f)

                # Controls
                j["nsLimit"] = data['settings']['controls']['nsLimit']
                j["minPolyOrd"] = data['settings']['controls']['polyOrd']['min']
                j["maxPolyOrd"] = data['settings']['controls']['polyOrd']['max']
                j["minThrVal"] = data['settings']['controls']['thrVal']['min']
                j["maxThrVal"] = data['settings']['controls']['thrVal']['max']
                j["minCntsAdj"] = data['settings']['controls']['cntsAdj']['min']
                j["maxCntsAdj"] = data['settings']['controls']['cntsAdj']['max']

                # Style
                # -- Plot
                j["plotColor"] = data['settings']['style']['plot']['plotColor']
                j["plotSelectedColor"] = data['settings']['style']['plot']['plotSelectedColor']
                j["plotApproxColor"] = data['settings']['style']['plot']['plotApproxColor']
                # -- Appearance
                j["tFrameBg"] = data['settings']['style']['appearance']['tFrame']['bg']
                j["controlsTFrameBg"] = data['settings']['style']['appearance']['controlsTFrame']['bg']
                j["tLabelBg"] = data['settings']['style']['appearance']['tLabel']['bg']
                j["tLabelFg"] = data['settings']['style']['appearance']['tLabel']['fg']
                j["skin"] = data['settings']['style']['savePlot']['skin']
        except:
            pass

        return j

    def setDefault(self):

        # Paths
        self.favFolderPath = self.basePath
        self.exportPath = self.basePath

        # Default settings
        self.nsLimit = 5
        self.minPolyOrd = 1
        self.maxPolyOrd = 15
        self.minThrVal = 0.01
        self.maxThrVal = 0.1
        self.minCntsAdj = -100
        self.maxCntsAdj = 0

        # Style
        # -- Font
        self.fontFamily = "Poppins"
        self.fontSize = 11
        self.fontColor = "white"
        # -- Plot
        self.plotColor = "#4169e1"
        self.plotSelectedColor = "mediumspringgreen"
        self.plotApproxColor = "deeppink"
        # -- Appearance
        self.tFrameBg = "#21252b"
        self.controlsTFrameBg = "#282c34"
        self.tLabelBg = "#282c34"
        self.tLabelFg = "white"
        #  -- savePlotSkin
        self.skin = "dark"

class ControlsSettingsReader():
    def __init__(self,fileName,settings):

        self.costFunctions = ["Symmetric Huber function",
                              "Asymmetric Huber function",
                              "Symmetric truncated quadratic",
                              "Asymmetric truncated quadratic"]

        self.valid = {}
        self.override = {}

        self.valid["OriginalFileName"] = True
        self.override["OriginalFileName"] = True
        self.valid["CostFunction"] = False
        self.override["CostFunction"] = False
        self.valid["polyOrd"] = False
        self.override["polyOrd"] = False
        self.valid["thrVal"] = False
        self.override["thrVal"] = False
        self.valid["cntsAdj"] = False
        self.override["cntsAdj"] = False


        txtr = np.loadtxt(fileName,dtype="str",skiprows = 1,unpack=True,delimiter=" | ")
        if txtr is not None:

            self.originalFileName = txtr[0]
            self.costFunVal = txtr[1]
            self.polyOrd = txtr[2]
            self.thrVal = txtr[3]
            self.cntsAdj = txtr[4]





            # Cost function
            if self.costFunVal not in self.costFunctions:
                self.valid["CostFunction"] = False
                self.override["CostFunction"] = False
            else:
                self.valid["CostFunction"] = True
                self.override["CostFunction"] = True


            #  Polynomial Order
            try:
                self.polyOrd = int(self.polyOrd)
            except:
                self.valid["polyOrd"] = False


            if isinstance(self.polyOrd,int) and self.polyOrd > 0:
                self.valid["polyOrd"] = True
                if settings.minPolyOrd <= self.polyOrd <= settings.maxPolyOrd:
                    self.override["polyOrd"] = True


            # Threshold
            try:
                self.thrVal = float(self.thrVal)
            except:
                self.valid["thrVal"] = False
            if isinstance(self.thrVal,float) and 0.01 <= self.thrVal <= 0.1:
                self.valid["thrVal"] = True
                if settings.minThrVal <= self.thrVal <= settings.maxThrVal:
                    self.override["thrVal"] = True


            # CountsAdjust
            try:
                self.cntsAdj = float(self.cntsAdj)
                self.valid["cntsAdj"] = True
            except:
                self.valid["cntsAdj"] = False
            if self.valid["cntsAdj"] :
                if isinstance(self.cntsAdj,float) and settings.minCntsAdj <= self.cntsAdj <= settings.maxCntsAdj:
                    self.override["cntsAdj"] = True


        else:
            return None
