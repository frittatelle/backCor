import os as os
import json
from matplotlib.colors import is_color_like

class SettingsReader():

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


        # Setting valori di default
        self.setDefault()

        # Lettura settings.json
        j = self.readJson(settingsFilePath)

        # Check e loading user settings
        self.editSettings(j)



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
                # -- Font
                # -- Plot
                j["plotColor"] = data['settings']['style']['plot']['plotColor']
                j["plotSelectedColor"] = data['settings']['style']['plot']['plotSelectedColor']
                j["plotApproxColor"] = data['settings']['style']['plot']['plotApproxColor']
                # -- Appearance
                j["tFrameBg"] = data['settings']['style']['appearance']['tFrame']['bg']
                j["controlsTFrameBg"] = data['settings']['style']['appearance']['controlsTFrame']['bg']
                j["tLabelBg"] = data['settings']['style']['appearance']['tLabel']['bg']
                j["tLabelFg"] = data['settings']['style']['appearance']['tLabel']['fg']
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
