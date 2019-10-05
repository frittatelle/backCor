import os as os
import json

class SettingsReader():

    def __init__(self):

        basePath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.basePath = basePath
        settingsFilePath = os.path.join(basePath,"data\\userData\\settings.json")
        self.settingsFilePath = settingsFilePath

        try:
            with open(settingsFilePath) as f:
                data = json.load(f)

                # Data paths
                self.favFolderPath = self.basePath
                self.exportPath = self.basePath

                # Controls
                self.nsLimit = data['settings']['controls']['nsLimit']
                self.minPolyOrd = data['settings']['controls']['polyOrd']['min']
                self.maxPolyOrd = data['settings']['controls']['polyOrd']['max']
                self.minThrVal = data['settings']['controls']['thrVal']['min']
                self.maxThrVal = data['settings']['controls']['thrVal']['max']
                self.minCntsAdj = data['settings']['controls']['cntsAdj']['min']
                self.maxCntsAdj = data['settings']['controls']['cntsAdj']['max']

                # Style
                # -- Font
                self.fontFamily = data['settings']['style']['font']['fontFamily']
                self.fontSize = data['settings']['style']['font']['fontSize']
                self.fontColor = data['settings']['style']['font']['fontColor']
                # -- Plot
                self.plotColor = data['settings']['style']['plot']['plotColor']
                self.plotSelectedColor = data['settings']['style']['plot']['plotSelectedColor']
                self.plotApproxColor = data['settings']['style']['plot']['plotApproxColor']
                # -- Appearance
                self.tFrameBg = data['settings']['style']['appearance']['tFrame']['bg']
                self.controlsTFrameBg = data['settings']['style']['appearance']['controlsTFrame']['bg']
                self.tLabelBg = data['settings']['style']['appearance']['tLabel']['bg']
                self.tLabelFg = data['settings']['style']['appearance']['tLabel']['fg']

                # Check se ogni impostazione ha un valore corretto
                counter = 0
                for attr, value in self.__dict__.items():
                    if value is None:
                        counter += 1

                if counter > 0 : self.setDefault()



        except :
            self.setDefault()



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
