import wdfReader.wdfReader as wdfReader
import numpy as np


class DataReader():

    def __init__(self, fileName):

        # Wdf reader
        wdfr = wdfReader.wdfReader(file_name = fileName)

        self.pointsPerSpectrum = wdfr.point_per_spectrum            # N campioni per spettro
        self.spectraData = self.processSpectra(wdfr)
        self.ramanShift = self.processramanShift(wdfr)

    # Spectra
    def processSpectra(self,wdfr):
        spectraData = wdfr.get_spectra()                            # get spectraData (Array n-dimensionale di tutti gli spettri)
        nSpectra = int(len(spectraData)/self.pointsPerSpectrum)     # N spettri considerati
        spectraData = np.split(spectraData,nSpectra)                # divisione spectraData in nSpectra spettri
        spectraData = np.fliplr(spectraData)                        # reverse spectraData

        if nSpectra == 1:
            spectraData = spectraData[0]

        return spectraData

    # ramanShift
    def processramanShift(self,wdfr):
        ramanShift = wdfr.get_xdata()
        ramanShift = np.flipud(ramanShift)                            # reverse ramanShift
        ramanShift = list(ramanShift)

        return ramanShift
