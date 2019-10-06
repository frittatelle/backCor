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
        for idx,attr in enumerate(self.__dict__.items()):
            #  i primi 4 attributi sono i path
            if idx > 3:
                if self.checkVal(attr[1],j[idx-4]):
                    setattr(self,attr[0],j[idx-4])

    def checkVal(self,default,value):
        f = False
        # controllo sul tipo
        if type(value) == type(default):
            # Controllo colore valido
            if type(value) is str:
                if is_color_like(value):
                    f = True
            # Controllo Float valido
            elif type(value) is float:
                if 0.01 <= value <= 0.1:
                    f = True
            # Controllo int valido
            elif type(value) is int:
                # Int pos
                if default >= 0 :
                    if value >= 0:
                        f = True
                # Int neg
                else:
                    if value < 0:
                        f = True
        return f

    def readJson(self,settingsFilePath):
        # Lettura seettings.json e aggiornamento settings se i valori sono validi
        j = []
        try:
            with open(settingsFilePath) as f:
                data = json.load(f)

                # Controls
                j.append(data['settings']['controls']['nsLimit'])
                j.append(data['settings']['controls']['polyOrd']['min'])
                j.append(data['settings']['controls']['polyOrd']['max'])
                j.append(data['settings']['controls']['thrVal']['min'])
                j.append(data['settings']['controls']['thrVal']['max'])
                j.append(data['settings']['controls']['cntsAdj']['min'])
                j.append(data['settings']['controls']['cntsAdj']['max'])

                # Style
                # -- Font
                j.append(data['settings']['style']['font']['fontFamily'])
                j.append(data['settings']['style']['font']['fontSize'])
                j.append(data['settings']['style']['font']['fontColor'])
                # -- Plot
                j.append(data['settings']['style']['plot']['plotColor'])
                j.append(data['settings']['style']['plot']['plotSelectedColor'])
                j.append(data['settings']['style']['plot']['plotApproxColor'])
                # -- Appearance
                j.append(data['settings']['style']['appearance']['tFrame']['bg'])
                j.append(data['settings']['style']['appearance']['controlsTFrame']['bg'])
                j.append(data['settings']['style']['appearance']['tLabel']['bg'])
                j.append(data['settings']['style']['appearance']['tLabel']['fg'])
        except:
            pass

        return j

    def setDefault(self):

        # Paths
        self.favFolderPath = self.basePath
        self.exportPath = self.basePath

        # Default settings
        self.nsLimit = 11
        self.minPolyOrd = 1
        self.maxPolyOrd = 15
        self.minThrVal = 0.01
        self.maxThrVal = 0.1
        self.minCntsAdj = -70
        self.maxCntsAdj = 70

        # Style
        # -- Font
        self.fontFamily = "Poppins"
        self.fontSize = 11
        self.fontColor = "white"
        # -- Plot
        self.plotColor = "#4169e1"
        self.plotSelectedColor = "#ffc445"
        self.plotApproxColor = "#ff6745"
        # -- Appearance
        self.tFrameBg = "#21252b"
        self.controlsTFrameBg = "#282c34"
        self.tLabelBg = "#282c34"
        self.tLabelFg = "white"
