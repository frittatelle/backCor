class Data():
    def __init__(self,pointsPerSpectrum,ramanShift,spectraData):
        self.pointsPerSpectrum = pointsPerSpectrum
        self.ramanShift = ramanShift
        self.spectraData = spectraData

        if spectraData is not None:
            if len(spectraData) == self.pointsPerSpectrum:
                self.nSpectra = 1
            else:
                self.nSpectra = len(spectraData)        
