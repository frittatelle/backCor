import wdfReader.wdfReader as wdfReader
import numpy as np


class DataReader():

    def __init__(self, fileName):

        if fileName.endswith(".wdf"):
            # Wdf reader
            wdfr = wdfReader.wdfReader(file_name = fileName)
            if wdfr is not None:
                self.pointsPerSpectrum = wdfr.point_per_spectrum            # N campioni per spettro
                self.spectraData = self.processSpectra(wdfr)
                self.ramanShift = self.processramanShift(wdfr)

                # nSpectra
                if len(self.spectraData) == self.pointsPerSpectrum:
                    nSpectra = 1
                else:
                    nSpectra = len(self.spectraData)

                # Mantiene un ordine corretto (alcuni file hanno lo shift al contrario)
                if self.ramanShift[1] < self.ramanShift[0]:
                    self.ramanShift = np.flipud(self.ramanShift)

                    if nSpectra == 1:
                        self.spectraData = np.flipud(self.spectraData)
                    else:
                        self.spectraData = np.fliplr(self.spectraData)


        elif fileName.endswith(".txt") or fileName.endswith(".dat"):

            # Se c`e' la virgola al posto del punto swap
            with open(fileName, 'r+') as f:
                text = f.read()
                f.seek(0)
                f.truncate()
                f.write(text.replace(",","."))


            # Txt reader
            txtr = np.loadtxt(fileName, dtype = "float",skiprows = 1, unpack=True)
            if txtr is not None:

                # Lettura dati
                self.ramanShift = txtr[0]
                self.pointsPerSpectrum = len(txtr[0])
                if len(txtr) == 2:
                    self.spectraData = txtr[1]
                else:
                    self.spectraData = txtr[1:]

                # nSpectra
                if len(self.spectraData) == self.pointsPerSpectrum:
                    nSpectra = 1
                else:
                    nSpectra = len(self.spectraData)

                # Mantiene un ordine corretto (alcuni file hanno lo shift al contrario)
                if self.ramanShift[1] < self.ramanShift[0]:
                    self.ramanShift = np.flipud(self.ramanShift)

                    if nSpectra == 1:
                        self.spectraData = np.flipud(self.spectraData)
                    else:
                        self.spectraData = np.fliplr(self.spectraData)


        else:
            return None

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
