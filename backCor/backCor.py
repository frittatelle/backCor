
# matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator,AutoMinorLocator
from cycler import cycler

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
from polyApprox.polyApprox import PolyApprox,PolyApproxIdx,PolyApproxMulti

# settingsReader
from settingsReader.settingsReader import UserSettingsReader,ControlsSettingsReader

#numpy
import numpy as np
import numpy.matlib as npm

# math
import math

#os
import os as os




###############################################################################

# BackCor
class BackCor(tk.Tk):

    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent

        # Settings
        settings = UserSettingsReader()
        self.setStyle(settings)         # Style
        self.setWindowInfo(settings)    # Window

        # Data container
        data = Data(None,None,None)
        cleanData = Data(None,None,None)


        # PlotFrame
        pFrame = PlotFrame(self,settings)
        self.pFrame = pFrame

        # ControlsFrame
        cFrame = ControlsFrame(self,data,cleanData,settings)
        self.cFrame = cFrame

        # MenuBar
        menuBar = MenuBar(self,data,settings)


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
        s.configure('TRadiobutton',background = settings.tLabelBg,foreground = settings.tLabelFg,font = (settings.fontFamily,settings.fontSize))
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
        self.geometry("%dx%d+0+0" % (width/1.3,height/1.3))
        # minimum size
        self.minsize(int(width/2),int(height/2))
        #Title
        self.title("backCor")


        for i in range(0,100):
            self.rowconfigure(i, weight = 1)
            self.columnconfigure(i, weight = 1)

    # Set plot style
    def setPlotStyle(self,data):
        ax = self.pFrame.ax

        # setting plot limits
        l = data.ramanShift[0]
        r = data.ramanShift[-1]
        ax.set_xlim(l,r)

        # plot grid
        maxCount = np.amax(data.spectraData)
        maxCount = int(math.ceil(maxCount / 1000.0) * 1000)
        maxShift = np.amax(data.ramanShift)
        maxShift = int(math.ceil(maxShift / 1000.0) * 1000)
        tickLocY = int(maxCount/10)
        tickLocX = int(maxShift/10)

        ax.xaxis.set_major_locator(MultipleLocator(tickLocX))
        ax.yaxis.set_major_locator(MultipleLocator(tickLocY))
        ax.xaxis.set_minor_locator(AutoMinorLocator(10))
        ax.yaxis.set_minor_locator(AutoMinorLocator(5))

        ax.grid(which='major', color='grey', linestyle='-',alpha = 0.6)
        ax.grid(which='minor', color='grey', linestyle=':',alpha = 0.8)

        # Remove plot border
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Plot background color
        ax.set_facecolor("#282c34")

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
        fileMenu.add_command(label = "Open",command = partial(self.openFile,data,settings))
        fileMenu.add_command(label = "Load controls settings",command = partial(self.loadControlsSettings,settings))
        fileMenu.add_command(label = "Save controls settings",command = partial(self.exportControlsSettings,settings))
        fileMenu.add_command(label = "Save plot",command = partial(self.savePlot,settings))
        fileMenu.add_separator()

        fileMenu.add_command(label = "Exit",command = parent.destroy)
        self.add_cascade(label = "File", menu = fileMenu)

        # Edit
        editMenu = tk.Menu(self, tearoff = 0)
        editMenu.add_command(label = "Settings",command = partial(self.openSettings,settings))
        self.add_cascade(label="Edit", menu = editMenu)


    # Open
    def openFile(self,data,settings):

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
            filetype = [('data files','.wdf .txt .dat')]
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
        selectButton = self.parent.cFrame.selectButton
        approxModeRB1 = self.parent.cFrame.approxModeRB1
        approxModeRB2 = self.parent.cFrame.approxModeRB2
        expModeRB1 = self.parent.cFrame.expModeRB1
        expModeRB2 = self.parent.cFrame.expModeRB2
        expModeRB3 = self.parent.cFrame.expModeRB3

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
                ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")
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

                selectButton.configure(state = tk.DISABLED)
                expModeRB1.configure(state = tk.NORMAL)
                expModeRB2.configure(state = tk.DISABLED)
                expModeRB3.configure(state = tk.DISABLED)
                approxModeRB1.configure(state = tk.NORMAL)
                approxModeRB2.configure(state = tk.DISABLED)


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

                selectButton.configure(state = tk.NORMAL)
                expModeRB1.configure(state = tk.DISABLED)
                expModeRB2.configure(state = tk.DISABLED)
                expModeRB3.configure(state = tk.DISABLED)
                approxModeRB1.configure(state = tk.DISABLED)
                approxModeRB2.configure(state = tk.DISABLED)

                # setta i default delle entry
                minIdxSpectra.set(1)
                maxIdxSpectra.set(data.nSpectra)

                colors = matplotlib.cm.rainbow(np.linspace(0, 1, 10))
                cy = cycler('color', colors)
                ax.set_prop_cycle(cy)

                #plot spettri
                for spectrum in spectraData:
                    ax.plot(ramanShift,spectrum,alpha = 0.7)

            self.parent.setPlotStyle(data)

            canvas.draw()

    # Load controls settings
    def loadControlsSettings(self,settings):
        f = tk.filedialog.askopenfilename(
            parent = self.parent,
            initialdir = settings.favFolderPath,title = 'Choose file',
            filetype = [('controls Settings','.txt')]
            )

        try:
            csr = ControlsSettingsReader(f,settings)
            if csr is None:
                tk.messagebox.showerror(title="Reading error",message="Il file non e' stato letto correttamente")
            else:
                invalidMsg = ""
                incompatibleMsg = ""
                invalidFlag = False in csr.valid.values()
                incompatibleFlag = False in csr.override.values()
                updateFlag = not invalidFlag and not incompatibleFlag

                if invalidFlag:
                    for attr,val in csr.valid.items():
                        if val == False:
                            invalidMsg = invalidMsg + attr + " non valido\n"
                    tk.messagebox.showerror(title="Value error",message = invalidMsg + "Impossibile caricare le impostazioni: file corrotto o illeggibile")

                else:
                    # Ciclo sugli attributi validi (compatibili e incompatibili)
                    # Stampa quelli incompatibili
                    for attr,val in csr.override.items():
                        if csr.override[attr] == False:
                            if attr == "OriginalFileName":
                                pass
                            else:
                                incompatibleMsg = self.calcIncompMsg(incompatibleMsg,csr,settings,attr)

                    # Chiede all'utente se cambiare le impostazioni accordingly
                    question = "Cambiare le impostazioni utente provvisoriamente per caricare il file?\n"
                    if incompatibleFlag:
                        res = tk.messagebox.askyesno("Warning",message = incompatibleMsg + "\n" +question)
                        if res:
                            updateFlag = True
                        else:
                            pass

                    # Se e' possibile fare l'update lo esegue
                    if updateFlag:

                        # Settings new limit if it is the case

                        # PolyOrd
                        if csr.polyOrd < settings.minPolyOrd:
                            self.parent.cFrame.polyOrdSlider.configure(from_ = csr.polyOrd)
                        elif csr.polyOrd > settings.maxPolyOrd:
                            self.parent.cFrame.polyOrdSlider.configure(to = csr.polyOrd)

                        # Threshold
                        if csr.thrVal < settings.minThrVal:
                            self.parent.cFrame.thrSlider.configure(from_ = csr.thrVal)
                        elif csr.thrVal > settings.maxThrVal:
                            self.parent.cFrame.thrSlider.configure(to = csr.thrVal)

                        # CountsAdjust
                        if csr.cntsAdj < settings.minCntsAdj:
                            self.parent.cFrame.cntSlider.configure(from_ = csr.cntsAdj)
                        elif csr.cntsAdj > settings.maxCntsAdj:
                            self.parent.cFrame.cntSlider.configure(to = csr.cntsAdj)


                        # Set values
                        self.parent.cFrame.costFunVal.set(csr.costFunVal)
                        self.parent.cFrame.polyOrdSlider.set(csr.polyOrd)
                        self.parent.cFrame.thrSlider.set(csr.thrVal)
                        self.parent.cFrame.cntSlider.set(csr.cntsAdj)
        except:
            pass

    # Elenco incompatibili
    def calcIncompMsg(self,incompatibleMsg,csr,settings,attr):
        incompatibleMsg = incompatibleMsg + attr + " non e' compatibile con le impostazioni utente correnti:\n"
        incompatibleMsg = incompatibleMsg + "File: " + str(getattr(csr,attr)) +"\n"
        if attr == "polyOrd":
            attr = attr.replace("p","P")
        elif attr == "thrVal":
            attr = attr.replace("t","T")
        elif attr == "cntsAdj":
            attr = attr.replace("c","C")
        min = "min" + attr
        max = "max" + attr

        incompatibleMsg = incompatibleMsg + "User: " +"min = "+ str(getattr(settings,min)) + "; max = "+ str(getattr(settings,max)) +"\n\n"
        return incompatibleMsg

    # Export controls settings
    def exportControlsSettings(self,settings):
        try:
            f = tk.filedialog.asksaveasfile(mode = "w",
                parent = self.parent,
                defaultextension=".txt",
                initialdir = settings.exportPath,title = 'Save Control Settings',
                filetypes = [('text files','*.txt')])
            f.write("OriginalFileName | CostFunction | PolynomialOrder | Threshold | CountsAdjust\n")

            originalFileName = self.parent.title().replace("backCor - ","")

            costFunVal = self.parent.cFrame.costFunVal.get()
            polyOrd = self.parent.cFrame.polyOrdVal.get()
            thrVal = self.parent.cFrame.thrVal.get()
            cntsAdj = self.parent.cFrame.cntVal.get()

            f.write(originalFileName + " | " +
                    costFunVal + " | " +
                    str(polyOrd) + " | " +
                    str(thrVal) + " | " +
                    str(cntsAdj))

            f.close()

            tk.messagebox.showinfo("Salvataggio completato","File salvato correttamente")
        except:
            pass

    # Save plot
    def savePlot(self,settings):

        fig = self.parent.pFrame.fig
        ax = self.parent.pFrame.ax

        try:
            f = tk.filedialog.asksaveasfile(mode = "w",
                parent = self.parent,
                defaultextension=".png",
                initialdir = settings.exportPath,title = 'Save plot',
                filetypes = [('png','*.png'),
                             ('jpg','*.jpg'),
                             ('jpeg','*.jpeg'),
                             ('pdf','*.pdf'),
                             ('svg','*.svg')]).name

            # Skins
            if settings.skin == "white":
                ax.set_facecolor("white")
                ax.tick_params(axis='both', colors=settings.tFrameBg,labelsize = 12)
                ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = settings.tFrameBg)
                ax.set_ylabel("Intensity [counts]",fontsize = 15,color = settings.tFrameBg)
                fig.savefig(f,dpi = 350,pad_inches = 0.35,bbox_inches = "tight",facecolor = "white")
            elif settings.skin == "dark":
                ax.set_facecolor(settings.tFrameBg)
                ax.tick_params(axis='both', colors="white",labelsize = 12)
                ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
                ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")
                fig.savefig(f,dpi = 350,pad_inches = 0.35,bbox_inches = "tight",facecolor = settings.tFrameBg)

            tk.messagebox.showinfo("Salvataggio completato","File salvato correttamente")

        except:
            pass

    # Settings
    def openSettings(self,settings):
        if os.path.isfile(settings.settingsFilePath):
            call(["notepad.exe",settings.settingsFilePath])
            tk.messagebox.showwarning(title="Warning",message="Riavvia backCor per rendere effettive le modifiche")
        else:
            tk.messagebox.showerror(title="Loading error",message="Settings file non trovato - (data/userData/settings.json)")

###############################################################################

#PlotFrame
class PlotFrame(ttk.Frame):

    def __init__(self,parent,settings):
        ttk.Frame.__init__(self,parent)
        self.parent = parent

        self.grid(row = 0, column = 0, columnspan = 95,rowspan = 100,sticky = "news")
        self.columnconfigure(0,weight = 1)
        self.rowconfigure(0,weight = 1)

        fig = Figure(figsize=(4,4),dpi=70,constrained_layout=True)
        fig.patch.set_facecolor('#21252b')

        ax = fig.add_subplot(111)
        ax.tick_params(axis='both', colors='white',labelsize = 12)
        ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")

        ax.grid(which='major', color='grey', linestyle=':',alpha = 0.5)
        ax.set_xticks(np.arange(0, 1050, 50))
        ax.set_yticks(np.arange(0, 1050, 50))

        # Remove plot border
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Plot background color
        ax.set_facecolor("#282c34")


        canvas = FigureCanvasTkAgg(fig, master = self)
        canvas.get_tk_widget().grid(row = 0, column = 0,sticky = 'news',padx = 20, pady = 30)
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

        self.grid(row = 0,column = 95, columnspan = 5, rowspan = 100, sticky = "news")
        self.configure(style = 'controls.TFrame')
        self.ax = self.parent.pFrame.ax
        self.canvas = self.parent.pFrame.canvas

        # Settings
        self.nsLimit = settings.nsLimit
        self.plotColor = settings.plotColor
        self.plotSelectedColor = settings.plotSelectedColor
        self.plotApproxColor = settings.plotApproxColor
        self.exportPath = settings.exportPath


        # Labels
        self.nSpectra = tk.IntVar()
        nSpectraTextLabel = ttk.Label(master = self, text = "# Spettri : ")
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


        # Select button
        self.selectButton = ttk.Button(self,text = "Select",command = partial(self.checkPlotInput,data,'<Key-Return>'))
        self.selectButton.configure(state = tk.DISABLED)


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
        self.costFunOptions = settings.costFunctions
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


        # ExportMode
        self.expMode = tk.StringVar()
        self.expMode.set("Single")
        expModeTextLabel = ttk.Label(self,text = "Export Mode:")
        self.expModeRB1 = ttk.Radiobutton(self,text = 'Single',variable = self.expMode,value = 'Single',command = partial(self.expmUpdate,data))
        self.expModeRB2 = ttk.Radiobutton(self,text = 'All',variable = self.expMode,value = 'All',command = partial(self.expmUpdate,data))
        self.expModeRB3 = ttk.Radiobutton(self,text = 'View',variable = self.expMode,value = 'View',command = partial(self.expmUpdate,data))
        self.expModeRB1.configure(state = tk.DISABLED)
        self.expModeRB2.configure(state = tk.DISABLED)
        self.expModeRB3.configure(state = tk.DISABLED)

        # ApproxMode
        self.approxMode = tk.StringVar()
        self.approxMode.set("Single")
        approxModeTextLabel = ttk.Label(self,text = "Approx Mode:")
        self.approxModeRB1 = ttk.Radiobutton(self,text = 'Single',variable = self.approxMode,value = 'Single',command = partial(self.apxmUpdate,data))
        self.approxModeRB2 = ttk.Radiobutton(self,text = 'Multiple',variable = self.approxMode,value = 'Multiple',command = partial(self.apxmUpdate,data))
        self.approxModeRB1.configure(state = tk.DISABLED)
        self.approxModeRB2.configure(state = tk.DISABLED)


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
        ghostLabel.configure(width = 20)
        nSpectraTextLabel.grid(row = 4, column = 10, columnspan = 1,sticky = 'ew')
        nSpectraLabel.grid(row = 4, column = 11, columnspan = 1,sticky = 'nsw')
        self.selectButton.grid(row = 4, column = 11, columnspan = 1,sticky = 'nse')
        self.selectButton.configure(width = 7)

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


        expModeTextLabel.grid(row = 73, column = 10, columnspan = 1,sticky = 'news')
        self.expModeRB1.grid(row = 75,column = 10,columnspan = 2,sticky = 'w')
        self.expModeRB2.grid(row = 77,column = 10,columnspan = 2,sticky = 'w')
        self.expModeRB3.grid(row = 76,column = 10,columnspan = 2,sticky = 'w')

        approxModeTextLabel.grid(row = 73, column = 11, columnspan = 1,sticky = 'news')
        self.approxModeRB1.grid(row = 75,column = 11,columnspan = 2,sticky = 'w')
        self.approxModeRB2.grid(row = 76,column = 11,columnspan = 2,sticky = 'w')


        self.subButton.grid(row = 88,column = 10,columnspan = 1,sticky = ' w')
        self.exportButton.grid(row = 88,column = 11,columnspan = 1,sticky = 'ew')
        self.backButton.grid(row = 89,column = 10,columnspan = 1,sticky = 'w')





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
            valid = int(val) <= data.nSpectra

        # rimozione 0 iniziale
        if not val:
            valid = True
        return valid

    def checkPlotInput(self,data,event):

        #
        try:
            min = self.minIdxSpectra.get()
        except:
            min = 1

        try:
            max = self.maxIdxSpectra.get()
        except:
            max = 2

        valid = min < max

        if max - min < self.nsLimit:
            self.costFunMenu.configure(state = tk.NORMAL)
            self.polyOrdSlider.configure(state = tk.NORMAL)
            self.thrSlider.configure(state = tk.NORMAL)
            self.cntSlider.configure(state = tk.NORMAL)
            self.subButton.configure(state = tk.NORMAL)
            self.backButton.configure(state = tk.DISABLED)
            self.exportButton.configure(state = tk.DISABLED)
            self.expModeRB2.configure(state = tk.NORMAL)
            self.expModeRB3.configure(state = tk.NORMAL)
            self.approxModeRB1.configure(state = tk.NORMAL)
            self.approxModeRB2.configure(state = tk.NORMAL)

            if self.approxMode.get() == "Single":
                self.expModeRB1.configure(state = tk.NORMAL)
                self.selectedIdxSlider.configure(state = tk.NORMAL,from_ = min,to = max)
                self.selectedIdxSlider.set(min)
            else:
                self.expModeRB1.configure(state = tk.DISABLED)
                self.selectedIdxSlider.configure(state = tk.DISABLED)

        else:
            self.selectedIdxSlider.configure(state = tk.DISABLED)
            self.costFunMenu.configure(state = tk.DISABLED)
            self.polyOrdSlider.configure(state = tk.DISABLED)
            self.thrSlider.configure(state = tk.DISABLED)
            self.cntSlider.configure(state = tk.DISABLED)
            self.subButton.configure(state = tk.DISABLED)
            self.backButton.configure(state = tk.DISABLED)
            self.exportButton.configure(state = tk.DISABLED)
            self.expModeRB1.configure(state = tk.DISABLED)
            self.expModeRB2.configure(state = tk.DISABLED)
            self.expModeRB3.configure(state = tk.DISABLED)
            self.approxModeRB1.configure(state = tk.DISABLED)
            self.approxModeRB2.configure(state = tk.DISABLED)


        #  if valid plot
        if valid:
            if max - min < self.nsLimit:
                self.polyApx(data)
            else:
                self.plotNSpectra(data,None)
                self.canvas.draw()
        else:
            tk.messagebox.showerror(title="Plot error",message="Inserisci dei valori di range validi")


    # Update selected idx
    def selUpdate(self,data,val):
        idx = int(float(val))
        self.selectedIdx.set(idx)
        # self.plotNSpectra(data,self.plotColor)
        # self.canvas.draw()
        self.polyApx(data)
    # Update cost function
    def costFunUpdate(self,data,val):
        self.costFunVal.set(val)
        self.polyApx(data)
    # Update polynomial oreder
    def polyUpdate(self,data,val):
        idx = int(float(val))
        self.polyOrdVal.set(idx)
        self.polyApx(data)
    # Update threshold
    def thrUpdate(self,data,val):
        idx = float(val)
        idx = round(idx,2)
        self.thrVal.set(idx)
        self.polyApx(data)
    # Update counts adjust
    def cntUpdate(self,data,val):
        idx = float(val)
        idx = round(idx,2)
        self.cntVal.set(idx)
        self.polyApx(data)
    # Update approxMode
    def apxmUpdate(self,data):
        mode = self.approxMode.get()
        if mode == "Single":
            self.selectedIdxSlider.configure(state = tk.NORMAL,from_ = self.minIdxSpectra.get(),to = self.maxIdxSpectra.get())
            self.selectedIdxSlider.set(self.minIdxSpectra.get())
            self.expModeRB1.configure(state = tk.NORMAL)
        elif mode == "Multiple":
            self.selectedIdxSlider.configure(state = tk.DISABLED)
            self.expModeRB1.configure(state = tk.DISABLED)
            self.expMode.set("View")
        self.polyApx(data)
    # Update expMode
    def expmUpdate(self,data):
        expMode = self.expMode.get()
        self.polyApx(data)


    #  Approssimazione polinomiale con shift
    def polyApx(self,data):
        mode = self.approxMode.get()
        shift = self.cntVal.get()
        # mode and nSpectra
        if data.nSpectra == 1:
            polyApprox = PolyApprox(data,self.polyOrdVal.get(),
                                    self.thrVal.get(),
                                    self.costFunVal.get())
        else:
            if mode == "Single":
                polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),
                                           self.thrVal.get(),
                                           self.costFunVal.get(),
                                           self.selectedIdx.get() - 1)
            elif mode == "Multiple":
                polyApprox = PolyApproxMulti(data,self.polyOrdVal.get(),
                                             self.thrVal.get(),
                                             self.costFunVal.get(),
                                             self.minIdxSpectra.get() - 1,
                                             self.maxIdxSpectra.get())
        polyApprox.approx()
        polyApprox.spectraApprox = polyApprox.spectraApprox + shift
        self.polyPlot(data,polyApprox)


    # Subtract poly
    def polySub(self,data,cleanData):
        # Creazione oggetto clean data
        cleanData.pointsPerSpectrum = data.pointsPerSpectrum
        cleanData.ramanShift = data.ramanShift
        cleanData.nSpectra = data.nSpectra
        expMode = self.expMode.get()
        apxMode = self.approxMode.get()
        shift = self.cntVal.get()
        # 1 or more spectra and exportMode
        if data.nSpectra == 1:
            polyApprox = PolyApprox(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get())
            polyApprox.approx()
            polyApprox.spectraApprox = polyApprox.spectraApprox + shift
            cleanData.spectraData = data.spectraData - polyApprox.spectraApprox
            self.easyPlot(cleanData,self.plotColor)
        else:
            if apxMode == "Single":
                if expMode == "Single":
                    polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.selectedIdx.get() - 1)
                    polyApprox.approx()
                    polyApprox.spectraApprox = polyApprox.spectraApprox + shift
                    cleanData.spectraData = data.spectraData[self.selectedIdx.get()] - polyApprox.spectraApprox
                    self.easyPlot(cleanData,self.plotColor)

                elif expMode == "All":
                    polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.selectedIdx.get() - 1)
                    polyApprox.approx()
                    polyApprox.spectraApprox = polyApprox.spectraApprox + shift
                    cleanData.spectraData = data.spectraData - polyApprox.spectraApprox
                    self.plotAll(cleanData,self.plotColor)

                elif expMode == "View":
                    polyApprox = PolyApproxIdx(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.selectedIdx.get() - 1)
                    polyApprox.approx()
                    polyApprox.spectraApprox = polyApprox.spectraApprox + shift
                    cleanData.spectraData = data.spectraData - polyApprox.spectraApprox
                    self.plotNSpectra(cleanData,None)

            elif apxMode == "Multiple":
                if expMode == "All":
                    polyApprox = PolyApproxMulti(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),0,data.nSpectra)
                    polyApprox.approx()
                    polyApprox.spectraApprox = polyApprox.spectraApprox + shift
                    cleanData.spectraData = data.spectraData - polyApprox.spectraApprox.T
                    self.plotAll(cleanData,self.plotColor)

                elif expMode == "View":
                    polyApprox = PolyApproxMulti(data,self.polyOrdVal.get(),self.thrVal.get(),self.costFunVal.get(),self.minIdxSpectra.get() - 1,self.maxIdxSpectra.get())
                    polyApprox.approx()
                    polyApprox.spectraApprox = polyApprox.spectraApprox + shift
                    cleanData.spectraData = data.spectraData[self.minIdxSpectra.get() - 1:self.maxIdxSpectra.get()] - polyApprox.spectraApprox.T
                    self.plotAll(cleanData,self.plotColor)

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
        self.selectButton.configure(state = tk.DISABLED)
        self.expModeRB1.configure(state = tk.DISABLED)
        self.expModeRB2.configure(state = tk.DISABLED)
        self.expModeRB3.configure(state = tk.DISABLED)
        self.approxModeRB1.configure(state = tk.DISABLED)
        self.approxModeRB2.configure(state = tk.DISABLED)


    # Plot approssimazione polinomiale + data
    def polyPlot(self,data,polyApprox):
        if data.nSpectra == 1:
            self.easyPlot(data,self.plotColor)
        else:
            self.plotNSpectra(data,self.plotColor)
        self.ax.plot(data.ramanShift,polyApprox.spectraApprox,self.plotApproxColor,linewidth = 2)
        self.canvas.draw()
    # EasyPlot
    def easyPlot(self,data,color):
        self.ax.cla()
        self.ax.tick_params(axis='both', colors='white',labelsize = 12)
        self.ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        self.ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")

        if color is None:
            self.ax.plot(data.ramanShift,data.spectraData)
        else:
            self.ax.plot(data.ramanShift,data.spectraData,color)

        self.parent.setPlotStyle(data)

    # PlotAll
    def plotAll(self,data,color):
        self.ax.cla()
        self.ax.tick_params(axis='both', colors='white',labelsize = 12)
        self.ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        self.ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")

        colors = matplotlib.cm.rainbow(np.linspace(0, 1, 10))
        cy = cycler('color', colors)
        self.ax.set_prop_cycle(cy)

        self.ax.plot(data.ramanShift,data.spectraData.T,alpha = 0.7)

        self.parent.setPlotStyle(data)
    # Plot multispettrale
    def plotNSpectra(self,data,color):

        # se non ci sono dati da plottare ritorna true
        if data.ramanShift is None:
            return True

        self.ax.cla()
        self.ax.tick_params(axis='both', colors='white',labelsize = 12)
        self.ax.set_xlabel("Raman Shift [1/cm]",fontsize = 15,color = "white")
        self.ax.set_ylabel("Intensity [counts]",fontsize = 15,color = "white")
        colors = matplotlib.cm.rainbow(np.linspace(0, 1, 10))
        cy = cycler('color', colors)
        self.ax.set_prop_cycle(cy)


        # Se non ci sono valori asseganti al range usa quelli di default
        try:
            rangeMin = self.minIdxSpectra.get()
        except:
            rangeMin = 1
        try:
            rangeMax = self.maxIdxSpectra.get()
        except:
            rangeMax = 2

        # plot degli spettri nel range indicato
        if not self.ax.lines:

            for i in range(rangeMin - 1,rangeMax):
                try:
                    # Se sono in fase di selezione o visualizzazione
                    if color is None:
                        self.ax.plot(data.ramanShift,data.spectraData[i])
                    else:
                        # Se lo spettro da plottare e' quello selezionato, plotta in colore selezione
                        if i == self.selectedIdx.get() - 1 and self.approxMode.get() == "Single":
                            self.ax.plot(data.ramanShift,data.spectraData[i],self.plotSelectedColor)
                        else:
                            self.ax.plot(data.ramanShift,data.spectraData[i],color)
                except:
                    pass


            self.parent.setPlotStyle(data)


    # Back
    def goBack(self,data,cleanData):
        # Reset cleanData
        cleanData.spectraData = None
        cleanData.nSpectra = None

        # Approssima e plotta (back)
        self.polyApx(data)

        # Reset controlli
        self.costFunMenu.configure(state = tk.NORMAL)
        self.polyOrdSlider.configure(state = tk.NORMAL)
        self.thrSlider.configure(state = tk.NORMAL)
        self.cntSlider.configure(state = tk.NORMAL)
        self.subButton.configure(state = tk.NORMAL)
        self.backButton.configure(state = tk.DISABLED)
        self.exportButton.configure(state = tk.DISABLED)
        self.expModeRB2.configure(state = tk.NORMAL)
        self.expModeRB3.configure(state = tk.NORMAL)
        self.approxModeRB1.configure(state = tk.NORMAL)
        self.approxModeRB2.configure(state = tk.NORMAL)

        if self.approxMode.get() == "Single":
            self.expModeRB1.configure(state = tk.NORMAL)
            self.selectedIdxSlider.configure(state = tk.NORMAL)
        else:
            self.expModeRB1.configure(state = tk.DISABLED)
            self.selectedIdxSlider.configure(state = tk.DISABLED)


        if data.nSpectra == 1:
            self.minIdxEntry.configure(state = tk.DISABLED)
            self.maxIdxEntry.configure(state = tk.DISABLED)
            self.selectButton.configure(state = tk.DISABLED)
            self.selectedIdxSlider.configure(state = tk.DISABLED)
            self.expModeRB2.configure(state = tk.DISABLED)
            self.expModeRB3.configure(state = tk.DISABLED)
            self.approxModeRB2.configure(state = tk.NORMAL)
            self.approxModeRB2.configure(state = tk.DISABLED)

        else:
            self.minIdxEntry.configure(state = tk.NORMAL)
            self.maxIdxEntry.configure(state = tk.NORMAL)
            self.selectButton.configure(state = tk.NORMAL)
    # Export
    def exportData(self,cleanData):
        try:
            f = tk.filedialog.asksaveasfile(mode = "w",
                parent = self.parent,
                defaultextension=".txt",
                initialdir = self.exportPath,title = 'Save file',
                filetypes = [('text files','*.txt')])
            f.write("Raman Shift [1/cm]    Intensity [counts]\n")

            if cleanData.nSpectra == 1:
                np.savetxt(f,np.c_[cleanData.ramanShift,cleanData.spectraData],fmt="%f")
            else:
                np.savetxt(f,np.c_[cleanData.ramanShift,cleanData.spectraData.T],fmt="%f")

            f.close()

            tk.messagebox.showinfo("Salvataggio completato","File salvato correttamente")
        except:
            pass

###############################################################################

# Run backCor

app = BackCor(None)
app.mainloop()
