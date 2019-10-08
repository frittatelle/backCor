
# matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

# functools
from functools import partial

# subprocess
from subprocess import call

# winFonts
from winFonts.winFonts import loadfont

#tkinter
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

#dataReader
from dataReader.dataReader import DataReader

# Data
from dataBlock.dataBlock import Data

# polyApprox
from polyApprox.polyApprox import PolyApprox,PolyApproxIdx

# settingsReader
from settingsReader.settingsReader import SettingsReader

#numpy
import numpy as np

#os
import os as os




###############################################################################

# BackCor
class BackCor(tk.Tk):

    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent

        # Settings
        settings = SettingsReader()
        self.setStyle(settings)         # Style
        self.setWindowInfo(settings)    # Window

        # Data container
        data = Data(None,None,None)
        cleanData = Data(None,None,None)

        # MenuBar
        menuBar = MenuBar(self,data,settings)

        # PlotFrame
        pFrame = PlotFrame(self)
        self.pFrame = pFrame

        # ControlsFrame
        cFrame = ControlsFrame(self,data,cleanData,settings)
        self.cFrame = cFrame



    # Set style
    def setStyle(self,settings):
        s = ThemedStyle()

        # Loading custom font
        # Se non trova Poppins/Custom font mette il default
        if settings.fontFamily == "Poppins":
            fontPath = os.path.join(settings.basePath,"fonts\\Poppins-Regular.ttf")
            loadfont(fontPath,private = True)

        s.configure('TFrame',background = settings.tFrameBg)
        s.configure('controls.TFrame',background = settings.controlsTFrameBg)
        s.configure('TLabel',background = settings.tLabelBg,foreground = settings.tLabelFg,font = (settings.fontFamily,settings.fontSize))
        s.configure('TButton',font = (settings.fontFamily,settings.fontSize))


    # Setting finestra
    def setWindowInfo(self,settings):
        # Icon
        iconPath = os.path.join(settings.basePath,"img\\ico\\backCor_BB.ico")
        self.iconbitmap(iconPath)
        # Dimensioni finestra
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        # self.geometry("%dx%d+0+0" % (width,heigth))
        self.geometry("%dx%d+0+0" % (width/2,height/2))
        # minimum size
        self.minsize(int(width/2),int(height/2))
        #Title
        self.title("backCor")


        for i in range(0,100):
            self.rowconfigure(i, weight = 1)
            self.columnconfigure(i, weight = 1)



###############################################################################


# MenuBar
class MenuBar(tk.Menu):
    def __init__(self,parent,data,settings):
        tk.Menu.__init__(self,parent)
        self.parent = parent
        # Setting menubar as window menu
        parent.config(menu = self)

        # File
        fileMenu = tk.Menu(self,tearoff = 0)
        fileMenu.add_command(label = "Open",command = partial(self.openFile,data,self.parent,settings))
        fileMenu.add_separator()
        fileMenu.add_command(label = "Exit",command = parent.destroy)
        self.add_cascade(label = "File", menu = fileMenu)

        # Edit
        editMenu = tk.Menu(self, tearoff = 0)
        editMenu.add_command(label = "Settings",command = partial(self.openSettings,settings))
        self.add_cascade(label="Edit", menu = editMenu)



    def openSettings(self,settings):
        if os.path.isfile(settings.settingsFilePath):
            call(["notepad.exe",settings.settingsFilePath])
            tk.messagebox.showwarning(title="Warning",message="Riavvia backCor per rendere effettive le modifiche")
        else:
            tk.messagebox.showerror(title="Loading error",message="Settings file non trovato - (data/userData/settings.json)")



    def openFile(self,data,parent,settings):

        # Browse file dialog

        f = self.browseFile(settings)

        # Lettura del file
        try:
            dataR = DataReader(fileName = f)

            if dataR is None:
                tk.messagebox.showerror(title="Reading error",message="Il file non e' stato letto correttamente")
            else:
                data.pointsPerSpectrum = dataR.pointsPerSpectrum
                data.ramanShift = dataR.ramanShift
                data.spectraData = dataR.spectraData
                if len(dataR.spectraData) == dataR.pointsPerSpectrum:
                    data.nSpectra = 1
                else:
                    data.nSpectra = len(dataR.spectraData)

                # Load data
                self.loadData(data,f,settings)

        except:
            pass





    def browseFile(self,settings):
        f = tk.filedialog.askopenfilename(
            parent = self.parent,
            initialdir = settings.favFolderPath,title = 'Choose file',
            filetype = [('data files','.wdf .txt')]
            )
        return f

    def loadData(self,data,f,settings):
        # pframe
        ax = self.parent.pFrame.ax
        fig = self.parent.pFrame.fig
        canvas = self.parent.pFrame.canvas

        # cframe
        nSpectra = self.parent.cFrame.nSpectra
        minIdxEntry = self.parent.cFrame.minIdxEntry
        maxIdxEntry = self.parent.cFrame.maxIdxEntry
        minIdxSpectra = self.parent.cFrame.minIdxSpectra
        maxIdxSpectra = self.parent.cFrame.maxIdxSpectra
        costFunMenu = self.parent.cFrame.costFunMenu
        thrSlider = self.parent.cFrame.thrSlider
        polyOrdSlider = self.parent.cFrame.polyOrdSlider
        cntSlider = self.parent.cFrame.cntSlider
        subButton = self.parent.cFrame.subButton
        backButton = self.parent.cFrame.backButton
        exportButton = self.parent.cFrame.exportButton
        selectedIdxSlider = self.parent.cFrame.selectedIdxSlider


        # data
        pointsPerSpectrum = data.pointsPerSpectrum
        ramanShift = data.ramanShift
        spectraData = data.spectraData

        res = False
        # message box chiudi finestra si/no
        # se non ci sono plot plotta, se ci sono plot chiedi
        if ax.lines:
            res = tk.messagebox.askyesno("Chiudere la finestra?","Sei sicuro di voler chiudere questa finestra?")

            if res:
                ax.cla()
                ax.tick_params(axis='both', colors='white',labelsize = 12)
                ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
                ax.set_ylabel("Counts",fontsize = 15,color = "white")
            else:
                pass

        if not ax.lines or res:

            # Setting titolo
            fileName = os.path.basename(f)
            self.parent.title("backCor - " + fileName)

            # Check sul numero degli spettri (caso spettro singolo)
            spectraCheck = data.nSpectra
            if spectraCheck == 1:
                ax.plot(ramanShift,spectraData,settings.plotColor)
                # setta a 1 il numero max di spettri
                maxIdxSpectra.set(1)
                # setta a 1 il numero di spettro
                self.parent.cFrame.nSpectra.set(1)
                #disbilita le entry
                minIdxEntry.configure(state = tk.DISABLED)
                maxIdxEntry.configure(state = tk.DISABLED)
                # buttons
                subButton.configure(state = tk.NORMAL)
                backButton.configure(state = tk.DISABLED)
                exportButton.configure(state = tk.DISABLED)
                # abilita cost function
                costFunMenu.configure(state = tk.NORMAL)
                #  abilita polyOrd
                polyOrdSlider.configure(state = tk.NORMAL)
                # abilita threshold
                thrSlider.configure(state = tk.NORMAL)
                # abilita counts adjust
                cntSlider.configure(state = tk.NORMAL)
                # disabilita selectedIdx
                selectedIdxSlider.configure(state = tk.DISABLED)

            else:
                #setta la label del numero di spettri
                nSpectra.set(data.nSpectra)
                # abilita le entry
                minIdxEntry.configure(state = tk.NORMAL)
                maxIdxEntry.configure(state = tk.NORMAL)
                # disabilita buttons
                subButton.configure(state = tk.DISABLED)
                backButton.configure(state = tk.DISABLED)
                exportButton.configure(state = tk.DISABLED)
                # disabilita cost function
                costFunMenu.configure(state = tk.DISABLED)
                #  disabilita polyOrd
                polyOrdSlider.configure(state = tk.DISABLED)
                # disabilita threshold
                thrSlider.configure(state = tk.DISABLED)
                # disabilita idxsel
                selectedIdxSlider.configure(state = tk.DISABLED)
                # disabilita cntSlider
                cntSlider.configure(state = tk.DISABLED)



                # setta i default delle entry
                minIdxSpectra.set(0)
                maxIdxSpectra.set(data.nSpectra - 1)
                #plot spettri
                for spectrum in spectraData:
                    ax.plot(ramanShift,spectrum)


            # setting plot limits
            l = ramanShift[0]
            r = ramanShift[-1]
            ax.set_xlim(l,r)

            canvas.draw()


###############################################################################

#PlotFrame
class PlotFrame(ttk.Frame):

    def __init__(self,parent):
        ttk.Frame.__init__(self,parent)
        self.parent = parent

        self.grid(row = 0, column = 0, columnspan = 90,rowspan = 100,sticky = "news")
        self.columnconfigure(0,weight = 1)
        self.rowconfigure(0,weight = 1)

        fig = Figure(figsize=(4,4),dpi=70,constrained_layout=True)
        fig.patch.set_facecolor('#21252b')

        ax = fig.add_subplot(111)
        ax.tick_params(axis='both', colors='white',labelsize = 12)
        ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        ax.set_ylabel("Counts",fontsize = 15,color = "white")


        canvas = FigureCanvasTkAgg(fig, master = self)
        canvas.get_tk_widget().grid(row = 0, column = 0,sticky = 'news',padx = 40, pady = 40)
        canvas.draw()


        self.canvas = canvas
        self.ax = ax
        self.fig = fig


###############################################################################

#ControlsFrame
class ControlsFrame(ttk.Frame):

    def __init__(self,parent,data,cleanData,settings):
        ttk.Frame.__init__(self,parent)
        self.parent = parent

        self.grid(row = 0,column = 90, columnspan = 10, rowspan = 100, sticky = "news")
        self.configure(style = 'controls.TFrame')
        self.ax = self.parent.pFrame.ax
        self.canvas = self.parent.pFrame.canvas

        self.nsLimit = settings.nsLimit
        self.plotColor = settings.plotColor
        self.plotSelectedColor = settings.plotSelectedColor
        self.plotApproxColor = settings.plotApproxColor
        self.exportPath = settings.exportPath



        # Labels
        self.nSpectra = tk.IntVar()
        nSpectraTextLabel = ttk.Label(master = self, text = "N° Spettri : ")
        nSpectraLabel = ttk.Label(master = self, textvariable = self.nSpectra)
        minIdxLabel = ttk.Label(self,text = "Min Idx: ")
        maxIdxLabel = ttk.Label(self,text = "Max Idx: ")
        ghostLabel = ttk.Label(self,text = "          ")



        # Entries
        self.minIdxSpectra = tk.IntVar()
        self.maxIdxSpectra = tk.IntVar()
        minIdxValidate = self.register(self.validateMinIdx)
        maxIdxValidate = self.register(partial(self.validateMaxIdx,data))
        self.minIdxEntry = ttk.Entry(master = self, textvariable = self.minIdxSpectra)
        self.maxIdxEntry = ttk.Entry(master = self, textvariable = self.maxIdxSpectra)
        self.minIdxEntry.configure(validate = "key", validatecommand = (minIdxValidate,"%P"))
        self.maxIdxEntry.configure(validate = "key", validatecommand = (maxIdxValidate,"%P"))
        self.minIdxEntry.configure(state = tk.DISABLED)
        self.maxIdxEntry.configure(state = tk.DISABLED)
        self.minIdxEntry.bind('<Key-Return>',partial(self.checkPlotInput,data))
        self.maxIdxEntry.bind('<Key-Return>',partial(self.checkPlotInput,data))



        # idx slider
        self.selectedIdx = tk.IntVar()
        selectedIdxTextLabel = ttk.Label(self,text = "Selected Idx:")
        selectedIdxLabel = ttk.Label(self,textvariable = self.selectedIdx)
        self.selectedIdxSlider = ttk.Scale(self,orient = tk.HORIZONTAL,command = partial(self.selUpdate,data))
        self.selectedIdxSlider.configure(state = tk.DISABLED)



        # cost function - dropdown menu
        self.costFunVal = tk.StringVar()
        self.costFunVal.set("Symmetric Huber function")
        costFunLabel = ttk.Label(self,text = "Cost Function:")
        self.costFunOptions = {"","Symmetric Huber function","Asymmetric Huber function","Symmetric truncated quadratic","Asymmetric truncated quadratic"}
        self.costFunMenu = ttk.OptionMenu(self, self.costFunVal,*self.costFunOptions,command = partial(self.costFunUpdate,data))
        self.costFunMenu.configure(state = tk.DISABLED)



        # poly order
        self.polyOrdVal = tk.IntVar()
        self.polyOrdVal.set(settings.minPolyOrd)
        polyOrdTextLabel = ttk.Label(self,text = "Polynomial Order:")
        polyOrdLabel = ttk.Label(self,textvariable = self.polyOrdVal)
        self.polyOrdSlider = ttk.Scale(self,from_ = settings.minPolyOrd,to = settings.maxPolyOrd,orient = tk.HORIZONTAL,command = partial(self.polyUpdate,data))
        self.polyOrdSlider.configure(state = tk.DISABLED)



        # threshold
        self.thrVal = tk.DoubleVar()
        self.thrVal.set(settings.minThrVal)
        thrTextLabel = ttk.Label(self,text = "Threshold:")
        thrLabel = ttk.Label(self,textvariable = self.thrVal)
        self.thrSlider = ttk.Scale(self,from_ = settings.minThrVal,to = settings.maxThrVal,orient = tk.HORIZONTAL,command = partial(self.thrUpdate,data))
        self.thrSlider.configure(state = tk.DISABLED)



        # cntVal
        self.cntVal = tk.DoubleVar()
        self.cntVal.set(0)
        cntTextLabel = ttk.Label(self,text = "Counts Adjust:")
        cntLabel = ttk.Label(self,textvariable = self.cntVal)
        self.cntSlider = ttk.Scale(self,from_ = settings.minCntsAdj,to = settings.maxCntsAdj,orient = tk.HORIZONTAL,command = partial(self.cntUpdate,data))
        self.cntSlider.configure(state = tk.DISABLED)



        # Sub Button
        self.subButton = ttk.Button(self,text = "Subtract",command = partial(self.polySub,data,cleanData))
        self.subButton.configure(state = tk.DISABLED)



        # Back Button
        self.backButton = ttk.Button(self,text = "Back",command = partial(self.goBack,data,cleanData))
        self.backButton.configure(state = tk.DISABLED)



        # Export Button
        self.exportButton = ttk.Button(self,text = "Export",command = partial(self.exportData,cleanData))
        self.exportButton.configure(state = tk.DISABLED)




        # Gridding
        for i in range(0,100):
            self.rowconfigure(i, weight = 1)
            self.columnconfigure(i, weight = 1)
        ghostLabel.grid(row = 3,column = 9,columnspan = 2)
        ghostLabel.configure(width = 18)
        nSpectraTextLabel.grid(row = 4, column = 10, columnspan = 3,sticky = 'news')
        nSpectraLabel.grid(row = 4, column = 11, columnspan = 3,sticky = 'news')

        minIdxLabel.grid(row = 8, column = 10, columnspan = 1,sticky = 'news')
        self.minIdxEntry.grid(row = 8, column = 11 ,sticky = 'ew')
        maxIdxLabel.grid(row = 9, column = 10, columnspan = 1,sticky = 'news')
        self.maxIdxEntry.grid(row = 9, column = 11 ,sticky = 'ew')

        selectedIdxTextLabel.grid(row = 12, column = 10, columnspan = 1,sticky = 'news')
        selectedIdxLabel.grid(row = 12,column = 11,columnspan = 1, sticky = 'news')
        self.selectedIdxSlider.grid(row = 13,column = 10,columnspan = 4,sticky = 'ew')

        costFunLabel.grid(row = 21,column = 10,columnspan = 4,sticky = 'ew')
        self.costFunMenu.grid(row = 22,column = 10,columnspan = 4,sticky = 'ew')
        self.costFunMenu.configure(width = 27)

        polyOrdTextLabel.grid(row = 34, column = 10, columnspan = 1,sticky = 'news')
        polyOrdLabel.grid(row = 34,column = 11,columnspan = 1, sticky = 'news')
        self.polyOrdSlider.grid(row = 35,column = 10,columnspan = 4,sticky = 'ew')

        thrTextLabel.grid(row = 47, column = 10, columnspan = 1,sticky = 'news')
        thrLabel.grid(row = 47,column = 11,columnspan = 1, sticky = 'news')
        self.thrSlider.grid(row = 48,column = 10,columnspan = 4,sticky = 'ew')

        cntTextLabel.grid(row = 59, column = 10, columnspan = 1,sticky = 'news')
        cntLabel.grid(row = 59,column = 11,columnspan = 1, sticky = 'news')
        self.cntSlider.grid(row = 60,column = 10,columnspan = 4,sticky = 'ew')



        self.subButton.grid(row = 76,column = 10,columnspan = 1,sticky = 'ew')
        self.backButton.grid(row = 77,column = 10,columnspan = 1,sticky = 'ew')

        self.exportButton.grid(row = 89,column = 10,columnspan = 1,sticky = 'ew')




    # Check / validations
    def validateMinIdx(self,val):
        # valido se e' un numero
        valid = val.isdigit()

        if valid:
            try:
                max = self.maxIdxSpectra.get()
            except:
                max = 1
            valid = int(val) < max

        # rimozione 0 iniziale
        if not val:
            valid = True
        return valid

    def validateMaxIdx(self,data,val):
        # valido se e' un numero
        valid = val.isdigit()

        if valid:
            valid = int(val) < data.nSpectra

        # rimozione 0 iniziale
        if not val:
            valid = True
        return valid

    def checkPlotInput(self,data,event):

        #
        try:
            min = self.minIdxSpectra.get()
        except:
            min = 0

        try:
            max = self.maxIdxSpectra.get()
        except:
            max = 1

        valid = min < max

        if max - min < self.nsLimit+1:
            self.selectedIdxSlider.configure(state = tk.NORMAL,from_ = min,to = max - 1)
            self.selectedIdxSlider.set(min)
            self.costFunMenu.configure(state = tk.NORMAL)
            self.polyOrdSlider.configure(state = tk.NORMAL)
            self.thrSlider.configure(state = tk.NORMAL)
            self.cntSlider.configure(state = tk.NORMAL)
            self.subButton.configure(state = tk.NORMAL)
            self.backButton.configure(state = tk.DISABLED)
            self.exportButton.configure(state = tk.DISABLED)
        else:
            self.selectedIdxSlider.configure(state = tk.DISABLED)
            self.costFunMenu.configure(state = tk.DISABLED)
            self.polyOrdSlider.configure(state = tk.DISABLED)
            self.thrSlider.configure(state = tk.DISABLED)
            self.cntSlider.configure(state = tk.DISABLED)
            self.subButton.configure(state = tk.DISABLED)
            self.backButton.configure(state = tk.DISABLED)
            self.exportButton.configure(state = tk.DISABLED)


        #  if valid plot
        if valid:
            if max - min < self.nsLimit:
                self.polyApx(data,self.cntVal.get())
            else:
                self.plotNSpectra(data,None)
                self.canvas.draw()
        else:
            tk.messagebox.showerror(title="Plot error",message="Inserisci dei valori di range validi")


    # Upddate selected idx
    def selUpdate(self,data,val):
        idx = int(float(val))
        self.selectedIdx.set(idx)
        # self.plotNSpectra(data,self.plotColor)
        # self.canvas.draw()
        self.polyApx(data,self.cntVal.get())
    # Upddate cost function
    def costFunUpdate(self,data,val):
        self.costFunVal.set(val)
        self.polyApx(data,self.cntVal.get())
    # Update polynomial oreder
    def polyUpdate(self,data,val):
        idx = int(float(val))
        self.polyOrdVal.set(idx)
        self.polyApx(data,self.cntVal.get())
    # Update threshold
    def thrUpdate(self,data,val):
        idx = float(val)
        idx = round(idx,2)
        self.thrVal.set(idx)
        self.polyApx(data,self.cntVal.get())
    # Update counts adjust
    def cntUpdate(self,data,val):
        idx = float(val)
        idx = round(idx,2)
        self.cntVal.set(idx)
        self.polyApx(data,self.cntVal.get())


    #  Approssimazione polinomiale con shift
    def polyApx(self,data,shift):
        if data.nSpectra == 1:
            polyApprox = PolyApprox(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get())
        else:
            polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.selectedIdx.get())
        polyApprox.approx()
        polyApprox.spectraApprox = polyApprox.spectraApprox + shift
        self.polyPlot(data,polyApprox)


    # Subtract poly
    def polySub(self,data,cleanData):
        # Creazione oggetto clean data
        cleanData.pointsPerSpectrum = data.pointsPerSpectrum
        cleanData.ramanShift = data.ramanShift
        # 1 or more spectra
        if data.nSpectra == 1:
            polyApprox = PolyApprox(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get())
            polyApprox.approx()
            cleanData.spectraData = data.spectraData- polyApprox.spectraApprox
        else:
            polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.selectedIdx.get())
            polyApprox.approx()
            cleanData.spectraData = data.spectraData[self.selectedIdx.get()] - polyApprox.spectraApprox

        self.easyPlot(cleanData,self.plotColor)
        self.canvas.draw()


        # Disable / Enable
        self.selectedIdxSlider.configure(state = tk.DISABLED)
        self.costFunMenu.configure(state = tk.DISABLED)
        self.polyOrdSlider.configure(state = tk.DISABLED)
        self.thrSlider.configure(state = tk.DISABLED)
        self.cntSlider.configure(state = tk.DISABLED)
        self.subButton.configure(state = tk.DISABLED)
        self.backButton.configure(state = tk.NORMAL)
        self.exportButton.configure(state = tk.NORMAL)
        self.minIdxEntry.configure(state = tk.DISABLED)
        self.maxIdxEntry.configure(state = tk.DISABLED)



    # Plot approssimazione polinomiale + data
    def polyPlot(self,data,polyApprox):
        if data.nSpectra == 1:
            self.easyPlot(data,self.plotColor)
        else:
            self.plotNSpectra(data,self.plotColor)
        self.ax.plot(data.ramanShift,polyApprox.spectraApprox,self.plotApproxColor)
        self.canvas.draw()

    # EasyPlot
    def easyPlot(self,data,color):
        self.ax.cla()
        self.ax.tick_params(axis='both', colors='white',labelsize = 12)
        self.ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        self.ax.set_ylabel("Counts",fontsize = 15,color = "white")

        if color is None:
            self.ax.plot(data.ramanShift,data.spectraData)
        else:
            self.ax.plot(data.ramanShift,data.spectraData,color)

        l = data.ramanShift[0]
        r = data.ramanShift[-1]
        self.ax.set_xlim(l,r)

    # Plot multispettrale
    def plotNSpectra(self,data,color):

        # se non ci sono dati da plottare ritorna true
        if data.ramanShift is None:
            return True

        self.ax.cla()
        self.ax.tick_params(axis='both', colors='white',labelsize = 12)
        self.ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        self.ax.set_ylabel("Counts",fontsize = 15,color = "white")

        # Se non ci sono valori asseganti al range usa quelli di default
        try:
            rangeMin = self.minIdxSpectra.get()
        except:
            rangeMin = 0
        try:
            rangeMax = self.maxIdxSpectra.get()
        except:
            rangeMax = 1

        # plot degli spettri nel range indicato
        if not self.ax.lines:
            for i in range(rangeMin,rangeMax):
                try:
                    # Se sono in fase di selezione o visualizzazione
                    if color is None:
                        self.ax.plot(data.ramanShift,data.spectraData[i])
                    else:
                        # Se lo spettro da plottare e' quello selezionato, plotta in colore selezione
                        if i == self.selectedIdx.get():
                            self.ax.plot(data.ramanShift,data.spectraData[i],self.plotSelectedColor)
                        else:
                            self.ax.plot(data.ramanShift,data.spectraData[i],color)
                except:
                    return True

                # setting plot limits
                l = data.ramanShift[0]
                r = data.ramanShift[-1]
                self.ax.set_xlim(l,r)


    # Back
    def goBack(self,data,cleanData):
        # Reset cleanData
        cleanData.spectraData = None
        cleanData.nSpectra = None

        # Approssima e plotta (back)
        self.polyApx(data,self.cntVal.get())

        # Reset controlli
        self.selectedIdxSlider.configure(state = tk.NORMAL)
        self.costFunMenu.configure(state = tk.NORMAL)
        self.polyOrdSlider.configure(state = tk.NORMAL)
        self.thrSlider.configure(state = tk.NORMAL)
        self.cntSlider.configure(state = tk.NORMAL)
        self.subButton.configure(state = tk.NORMAL)
        self.backButton.configure(state = tk.DISABLED)
        self.exportButton.configure(state = tk.DISABLED)
        if data.nSpectra == 1:
            self.minIdxEntry.configure(state = tk.DISABLED)
            self.maxIdxEntry.configure(state = tk.DISABLED)
            self.selectedIdxSlider.configure(state = tk.DISABLED)
        else:
            self.minIdxEntry.configure(state = tk.NORMAL)
            self.maxIdxEntry.configure(state = tk.NORMAL)

    # Export
    def exportData(self,cleanData):
        try:
            f = tk.filedialog.asksaveasfile(mode = "w",
                parent = self.parent,
                defaultextension=".txt",
                initialdir = self.exportPath,title = 'Save file',
                filetypes = [('text files','*.txt')])
            f.write("Raman Shift [1/cm]    Counts\n")
            np.savetxt(f,np.c_[cleanData.ramanShift,cleanData.spectraData],fmt="%f")

            tk.messagebox.showinfo("Salvataggio completato","File salvato correttamente")
        except:
            pass

###############################################################################

# Run backCor

app = BackCor(None)
app.mainloop()
