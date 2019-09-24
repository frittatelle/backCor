from tkinter import *
from tkinter.font import Font

# Setting window
root = Tk()
root.title("Background Correction")
root.resizable(0,0)


# Top level menu
menuBar = Menu(root)
root.config(menu = menuBar)
# File
fileMenu = Menu(menuBar,tearoff = 0)
fileMenu.add_command(label = "Open" )
fileMenu.add_command(label = "Save")
fileMenu.add_separator()
fileMenu.add_command(label = "Settings")
fileMenu.add_separator()
fileMenu.add_command(label = "Exit")
menuBar.add_cascade(label = "File", menu = fileMenu)
# Edit
editMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="Edit", menu=editMenu)



backcorFont = Font(family = "Roboto", size = "12")

# PLOT FRAME
plotFrame = Frame(root,height = "650",width = "950",bg = 'white',bd = 0)
plotFrame.pack(side = LEFT)
plotFrame.pack_propagate(0)

# Canvas
plotCanvas = Canvas(plotFrame, bg = 'mediumseagreen')
plotCanvas.pack(fill = BOTH, expand = 1, padx = 35, pady = 35)




# CONTROLS FRAME
controlsFrame = Frame(root,height = "650",width = "350", bd = 0)
controlsFrame.pack(side = RIGHT)
controlsFrame.pack_propagate(0)


#cost function - dropdown menu
costFunLabel = Label(controlsFrame,text = "Cost Function:",anchor = "w",font = backcorFont)
costFunLabel.pack(fill = X ,padx = 50,pady = (50,10))
costFunVal = StringVar(root)     #options value
costFunOptions = {"Symmetric Huber function","Asymmetric Huber function","Symmetric truncated quadratic","Asymmetric truncated quadratic"}
costFunMenu = OptionMenu(controlsFrame, costFunVal, *costFunOptions)
costFunMenu.config(font = backcorFont)
costFunMenu['menu'].config(font=backcorFont)
costFunMenu.config(font = backcorFont)
costFunMenu.pack(fill = X,padx = 50)

#threshold - spinbox
thrLabel = Label(controlsFrame,text = "Threshold:",anchor = "w",font = backcorFont)
thrLabel.pack(fill = X ,padx = 50,pady = (50,10))
#ordine del threshold?
#slider?
thrValue = StringVar(root)      # value
thrEntry = Spinbox(controlsFrame,from_ = 0,to = 10,increment = 0.1,textvariable = thrValue,font = backcorFont)
thrEntry.pack(fill = X ,padx = 50)


#polynomial order -slider
polyOrdLabel = Label(controlsFrame,text = "Polynomial Order:",anchor = "w",font = backcorFont)
polyOrdLabel.pack(fill = X ,padx = 50,pady = (50,0))
polyOrdVal = IntVar(root)      #slider value
polyOrdSlider = Scale(controlsFrame,from_ = 1,to = 20,orient = HORIZONTAL)
polyOrdSlider.pack(fill = X ,padx = 50)



# Executing window
root.mainloop()
