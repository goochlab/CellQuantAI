"""After all the individual CSV files from the slices are merged into a large file this program
will take the detected objects and draw both a box plot and dot plot into two separate files.
Note: the string "box" needs to be set to "yes" in order to make box plots.
This MaxXY version also looks at all the coordinates to calculate the image size instead of
basing it on the numbers in the file name.  It also doesn't base the size of the image
on the filename. It instead looks to see where the dots are.
If gradi = "yes" than (this only works for plots) it will make the dots different colors
depending on the score.  Scores go from 0.0 to 1.0.  It divides it into 10 divisions with
colors going from yellow, red, organge, blue, green, purple, black, pink, cyan, magenta.

2023-06-02.  I added the ability to run a density plot where each dot is a different color
based on the density of cells around it.  You need to run DensityCSV.py first which appends
a column named Density to the CSV file.  If the Density Threshold box is empty, the program
calculate the maximum density count and use 75% as the Density threshold.  If you enter a
number, the number will be used as the Density Threshold.  Finally, for each value to the
Density column, that value will be divided by Density Threshold (DensThresh) and multiplied
by 23.  This will then be used to color the dots one of the 24 colors.  Look for the
image 'density_scores_ribbon.jpg' for the scale.


Plotv1.3 I added the option of opening a file in the Annotations folder named "ImageData.csv"
This contains information to create a png file so it perfectly aligns with actual
image.  I later modified this so that the guard, x and y information is added as a name in the
column title.  The sliced images need to have been made with 1024ImageSliceGuardv1.1.py

Plotv1.4 This now works with RemoveDuplicatesNumpyThreshv1.1.py

Plotv1.5 The aligning of plots with images removed the text in the upper left corner.  This
fixes that error.

Plot 1.5b Added more colors.

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import pandas as pd
import random
import PIL
from PIL import ImageFont
import re
from PIL import Image
from PIL import ImageDraw
import easygui
import numpy as np
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("Plotting Options")

import tkinter as tk
from tkinter import filedialog

ImgSiz = 1  # 1 is equal to 100% image size.  .25 is 25% normal size
boxy = "yes1"
ploty = "yes1"
texty = "yes1"
scory = "yes1"
direct = ""
direct2 = ""
polygony = "yes1"
gradienty = "yes1"
densityy = "yes1"
sub = 7
DensThresh = 0
Pol = "no"
gradi = "no"
Dens = "no"
thresh = 0.0
MainColor = "None"
outer = "no"
rand = "yes"
ranthresh = 90  # will randomly chose a number up to 100 and print text if over
fin = 10  # normally 1, for the gradient option, make this number higher if you want a gradient with smaller numbers


def selection():
    global boxy
    global ploty
    if var.get() == 1:
        boxy = "yes"
        ploty = "no"
        R3.config(state=tk.DISABLED)
        R4.config(state=tk.DISABLED)
        R5.config(state=tk.DISABLED)
        E1.config(state=tk.DISABLED)
    elif var.get() == 2:
        ploty = "yes"
        boxy = "no"
        R3.config(state=tk.NORMAL)
        R4.config(state=tk.NORMAL)
        R5.config(state=tk.NORMAL)
        if plot_var.get() == 3:
            E1.config(state=tk.NORMAL)


def text_selection():
    global texty
    if text_var.get() == 1:
        texty = "yes"
        C2.config(state=tk.NORMAL)
    else:
        texty = "no"
        C2.deselect()
        C2.config(state=tk.DISABLED)


# def update_DensThresh(event):
#    global DensThresh
#    try:
#        DensThresh = float(E1.get())
#    except ValueError:
#        pass
def update_DensThresh(*args):
    global DensThresh
    try:
        value = int(dens_thresh_var.get())
        DensThresh = value
    except ValueError:
        pass


def score_selection():
    global scory
    if score_var.get() == 1:
        scory = "yes"
    else:
        scory = "no"


def browse():
    global direct
    direct = filedialog.askdirectory()
    if direct:
        L2.config(text="Folder Selected")
        B2.config(state=tk.NORMAL)
    else:
        L2.config(text="No folder Selected")
        B2.config(state=tk.DISABLED)


def browse2():
    global direct2
    direct2 = filedialog.askdirectory()


def plot_selection():
    global polygony
    global gradienty
    global densityy
    global gradi
    global Dens
    global Pol
    if plot_var.get() == 1:
        polygony = "yes"
        gradienty = "no"
        densityy = "no"
        gradi = "no"
        Dens = "no"
        Pol = "yes"
        E1.config(state=tk.DISABLED)
        # Enable the "Suppress Outside" check button when "Polygon" is selected
        C3.config(state=tk.NORMAL)
    elif plot_var.get() == 2:
        gradienty = "yes"
        polygony = "no"
        densityy = "no"
        gradi = "yes"
        Dens = "no"
        Pol = "no"
        E1.config(state=tk.DISABLED)
        # Disable the "Suppress Outside" check button when "Polygon" is not selected
        C3.deselect()
        C3.config(state=tk.DISABLED)
    elif plot_var.get() == 3:
        densityy = "yes"
        polygony = "no"
        gradienty = "no"
        gradi = "no"
        Dens = "yes"
        Pol = "no"
        E1.config(state=tk.NORMAL)
        # Disable the "Suppress Outside" check button when "Polygon" is not selected
        C3.deselect()
        C3.config(state=tk.DISABLED)


def suppress_outside_selection():
    global outer
    if suppress_outside_var.get() == 1:
        outer = "yes"
    else:
        outer = "no"


def update_sub(event):
    global sub
    try:
        sub = int(E3.get())
        if sub < 0:
            sub = 0
            E3.delete(0, tk.END)
            E3.insert(0, str(sub))
    except ValueError:
        pass


def update_thresh(event):
    global thresh
    try:
        thresh = float(E2.get())
    except ValueError:
        pass


def update_color(event):
    global MainColor
    MainColor = var_color.get()


def show_instructions():
    top = tk.Toplevel(root)
    top.title("Instructions")
    msg = """Instructions. A bounding box places a rectangle around the \
   identified object. A plot places a circle centered where the \
   bounding box would be. The plots can have different colors. \
   "Suppress Outside" will work only if "Polygon Lasso.py" has been \
   run.  This will stop any objects outside of the polygon(s) from \
   being plotted.  The "Gradient" will plot objects depending on how \
   high the score is.  If only "Text" is selected, it will is the object \
   number by each object.  If "Text" and "Score" are selected it will plot \
   the score next to the object.  If you don't enter a number in Density \
   Threshold it will use 75% of the highest as the max threshold"""
    label = tk.Label(top, text=msg, justify='left', wraplength=root.winfo_width())
    label.pack()


def run():
    if not direct or not var.get():
        return
    update_thresh(None)
    root.destroy()


frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT)

frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT)

var_color = tk.StringVar(root)
var_color.set("None")

var = tk.IntVar()
R1 = tk.Radiobutton(frame_left, text="Bounding Box", variable=var, value=1, command=selection,
                    font=("Helvetica", 12, 'bold'), fg='red')
R1.pack(anchor=tk.W)

R2 = tk.Radiobutton(frame_left, text="Plot", variable=var, value=2, command=selection, font=("Helvetica", 12, 'bold'),
                    fg='red')
R2.pack(anchor=tk.W)

text_var = tk.IntVar()
C1 = tk.Checkbutton(frame_right, text="Text", variable=text_var, onvalue=1, offvalue=0, command=text_selection)
C1.pack(anchor=tk.W)

score_var = tk.IntVar()
C2 = tk.Checkbutton(frame_right, text="Score", variable=score_var, onvalue=1, offvalue=0, command=score_selection)
C2.pack(anchor=tk.W)
C2.config(state=tk.DISABLED)

# Add a check button for the "Suppress Outside" option
suppress_outside_var = tk.IntVar()
C3 = tk.Checkbutton(frame_left, text="Suppress Outside", variable=suppress_outside_var, onvalue=1, offvalue=0,
                    command=suppress_outside_selection)
C3.pack(anchor=tk.W)

L2 = tk.Label(frame_right, text='No folder Selected')
L2.pack(anchor=tk.W)

B1 = tk.Button(frame_right, text="Browse", command=browse)
B1.pack(anchor=tk.W)

L4 = tk.Label(frame_right, text='ImageData')
L4.pack(anchor=tk.W)

B3 = tk.Button(frame_right, text="Browse", command=browse2)
B3.pack(anchor=tk.W)

L5 = tk.Label(frame_right, text='Reference Images (optional)')
L5.pack(anchor=tk.W)

B4 = tk.Button(frame_right, text="?", command=show_instructions)
B4.pack(anchor=tk.W)

plot_var = tk.IntVar()
R3 = tk.Radiobutton(frame_left, text="Polygon", variable=plot_var, value=1, command=plot_selection)
R3.pack(anchor=tk.W)
R3.config(state=tk.DISABLED)

R4 = tk.Radiobutton(frame_left, text="Gradient", variable=plot_var, value=2, command=plot_selection)
R4.pack(anchor=tk.W)
R4.config(state=tk.DISABLED)

R5 = tk.Radiobutton(frame_left, text="Density", variable=plot_var, value=3, command=plot_selection)
R5.pack(anchor=tk.W)
R5.config(state=tk.DISABLED)

L1 = tk.Label(frame_left, text='Density Threshold')
L1.pack(anchor=tk.W)

# E1=tk.Entry(frame_left,state='disabled')
# E1.bind("<Return>",update_DensThresh)
# E1.pack(anchor=tk.W)

dens_thresh_var = tk.StringVar()
E1 = tk.Entry(frame_left, textvariable=dens_thresh_var)
E1.pack(anchor=tk.W)

dens_thresh_var.trace("w", update_DensThresh)

tk.Label(frame_left, text='').pack()

L7 = tk.Label(frame_left, text='Plot Dot Radius (7 default)')
L7.pack(anchor=tk.W)

E3 = tk.Entry(frame_left, state='normal')
E3.bind("<KeyRelease>", update_sub)
E3.pack(anchor=tk.W)

tk.Label(frame_left, text='').pack()

L3 = tk.Label(frame_left, text='Score Threshold')
L3.pack(anchor=tk.W)

E2 = tk.Entry(frame_left)
E2.bind("<Return>", update_thresh)
E2.pack(anchor=tk.W)

L6 = tk.Label(frame_left, text='Color (force)')
L6.pack(anchor=tk.W)

OM1 = tk.OptionMenu(frame_left, var_color, "None", "Green", "Blue", "Red", "Black", "Yellow", "Orange", "White",
                    command=update_color)
OM1.pack(anchor=tk.W)

B2 = tk.Button(root, text="Run", command=run, state='disabled')
B2.pack(side=tk.BOTTOM, anchor=tk.E)

root.mainloop()

print("boxy " + boxy)
print("ploty " + ploty)
print("texty " + texty)
print("scory " + scory)
print("direct " + direct)
print("Rad " + str(sub))
print("Dens " + Dens)
print("DensThresh " + str(DensThresh))
print("Pol " + Pol)
print("gradi " + gradi)
print("thresh " + str(thresh))
print("direct2 " + direct2)
print("MainColor " + MainColor)
print("outer " + outer)

Image.MAX_IMAGE_PIXELS = None

locat = os.path.join(direct)
print(locat)

if direct2 != "":
    locat2 = os.path.join(direct2, "ImageData.csv")
    dfFil = pd.read_csv(locat2)

files = os.listdir(locat)

if Dens == "yes":
    for images in files:
        check = os.path.join(locat, images)
        if images.startswith("._"):  # mac files have these meta data files
            continue
        elif os.path.isdir(check):
            # skip directories
            continue
        elif images.endswith(".png"):
            # skip directories
            continue
        elif not images.endswith(".csv"):
            continue
        else:
            print(images)
            print("Density")
            print(Dens)
            print(DensThresh)
            if not images.endswith("D.csv"):
                print("Run DensityCSV.py program first")
                exit()

FILNAM = []

# This is if the file ends with .NoDups
for images in files:
    if not images.endswith(".csv"):
        continue

    elif images.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(images):
        # skip directories
        continue
    else:
        print(images)
        locat2 = os.path.join(locat, images)
        df1 = pd.read_csv(locat2)
        FWidth = 0
        FHeight = 0
        FGuard = 0

        # This chooses the file name to look up in the ImageData.csv file.  Since the original file
        # name may have changed it looks for it in the AllCSV.csv "File" column
        if direct2 != "":
            max_row = []
            # Assign the first value in the "File" column to the variable FIL
            FIL = df1.loc[0, 'File']
            # Find the index of the last occurrence of "SG" in the FIL string
            index = FIL.rfind('SG')
            # Remove the part of the string after the last "SG"
            FIL2 = FIL[:index + len('SG')]

            # Find a row in the dfFil DataFrame where the value in the "PNG" column begins with FIL2
            rowmatch = dfFil[dfFil['PNG'].str.startswith(FIL2)]
            if not rowmatch.empty:
                FWidth = int(rowmatch['Width'].iloc[0])
                FHeight = int(rowmatch['Height'].iloc[0])
                FGuard = int(rowmatch['Guard'].iloc[0])

            else:
                print(f'No matching row found for {FIL2}')

        df1max = df1['Class'].max()
        df1max = int(df1max)

        # Find the column title that starts with "GRD"
        for col_title in df1.columns:
            if col_title.startswith("GRD"):
                FilDat = col_title
                print(FilDat)
                break
            else:
                FilDat = "GRD0X0Y0"

        # Split the column title into parts
        if FGuard == 0:
            parts = FilDat.split("X")
            FGuard = int(parts[0].replace("GRD", ""))
            parts = parts[1].split("Y")
            FWidth = int(parts[0])
            FHeight = int(parts[1])

        FWidth = int(FWidth * ImgSiz)
        FHeight = int(FHeight * ImgSiz)

        if outer == "yes":
            if 'Poly' in df1.columns:
                df1 = df1[df1['Poly'] != 'Outside']
                df1 = df1.reset_index(drop=True)
            else:
                print("Run PolygonLasso.py first")
                exit()
        if Dens == "yes":
            DensMax = df1['Density'].max()

        SHAP = (df1.shape)
        r = SHAP[0]  # rows
        c = SHAP[1]  # columns
        print(r)
        print(c)

        # This looks through all the boxes to determine how big to make images
        wid_fin = 0
        hght_fin = 0
        for t1 in range(0, r):
            right = (df1.loc[t1, 'Right'])
            bottom = (df1.loc[t1, 'Bottom'])
            if right > wid_fin:
                wid_fin = right
            if bottom > hght_fin:
                hght_fin = bottom

        wid_fin = int(wid_fin) + 100
        # wid_fin = wid_fin + int(1250/divide1)
        hght_fin = int(hght_fin) + 100
        # hght_fin = hght_fin + int(950/divide1)

        if ploty == "yes":
            PlotImg = Image.new("RGBA", (wid_fin, hght_fin), (255, 0, 0, 0))

        if boxy == "yes":
            BoxImg = Image.new("RGBA", (wid_fin, hght_fin), (255, 0, 0, 0))

        if Pol == "yes":
            # df4 is just a list of each poly name
            df4 = df1.drop_duplicates(subset=['Poly'], keep="first")

            # This adds an index that goes from 0 to however many unique polys there are
            df4.reset_index(drop=True, inplace=True)

        colorlist = [
            "blue", "cyan", "orange", "yellow", "green", "purple", "black", "pink", "cyan", "magenta",
            "red", "lime", "teal", "navy", "maroon", "olive", "violet", "turquoise", "silver", "gold",
            "brown", "coral", "indigo", "khaki", "lavender", "salmon", "plum", "orchid", "peru", "tan",
            "crimson", "aqua", "chartreuse", "fuchsia", "chocolate"
        ]

        # colorlist = ["blue", "cyan", "orange", "yellow", "green", "purple", "black", "pink", "cyan", "magenta"]
        # colorlist = ["black", "black", "black", "black", "black", "black", "black", "black", "black", "black"]
        # colorlist = ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow"]

        for x in range(0, r):

            # NOTE: For below sometimes I needed to divide values by divide to work but other times not
            if ploty == "yes":
                dotx = (df1.loc[x, 'Dotx'])
                doty = (df1.loc[x, 'Doty'])
                scor = (df1.loc[x, 'Score'])
                clas = (df1.loc[x, 'Class'])
                Nam = (df1.loc[x, 'Object'])
                if Pol == "yes":
                    poly = (df1.loc[x, 'Poly'])
                if gradi == "yes":  # this will make the plots different colors based on score 1-10
                    grad = round(scor * 100 / fin)
                    if grad > 9:
                        grad = 9
                if Dens == "yes":
                    Densit = (df1.loc[x, 'Density'])

            if boxy == "yes":
                left = (df1.loc[x, 'Left'])
                right = (df1.loc[x, 'Right'])
                top = (df1.loc[x, 'Top'])
                bottom = (df1.loc[x, 'Bottom'])
                scor = (df1.loc[x, 'Score'])
                clas = (df1.loc[x, 'Class'])
                Nam = (df1.loc[x, 'Object'])
                if Pol == "yes":
                    poly = (df1.loc[x, 'Poly'])
                if gradi == "yes":  # this will make the plots different colors based on score 1-10
                    # grad = int(scor*10)
                    grad = round(scor * 100)
                    if grad > 9:
                        grad = 9
                if Dens == "yes":
                    Densit = (df1.loc[x, 'Density'])

            if ploty == "yes" and scor > thresh:
                draw = ImageDraw.Draw(PlotImg)
                clas = int(clas)
                col = colorlist[clas - 1]
                if gradi == "yes":
                    col = colorlist[grad]
                    # redgrad = int(grad *25.5)
                    for guide in range(0, 10):
                        gradcol = colorlist[guide]
                        draw.ellipse((sub * 10 - sub * 10, sub * guide * 20 - sub * 10 + sub * 10, sub * 10 + sub * 10,
                                      sub * guide * 20 + sub * 10 + sub * 10), fill=(gradcol), outline=(0, 0, 0))

                if Pol == "yes":  # Base colors on polygon outline
                    co = df4.loc[df4['Poly'] == poly].index.values
                    clrs = co[0]
                    if clrs > 34:
                        clrs = 34
                    col = colorlist[clrs]

                if Dens == "yes":
                    if DensThresh == 0:
                        DensThresh = int(DensMax * .75)
                    Denfin = int(23 * Densit / DensThresh)
                    if Denfin > 23:
                        Denfin = 23  # 23 because numbers go from 0-23

                    # These numbers tell where in the colors list to look.
                    tu1 = (Denfin - 1) * 3
                    tu2 = (Denfin * 3)

                    if tu1 < 0:  # Needed is Denfin is 0
                        tu1 = 0
                    if tu2 == 0:
                        tu2 = 3

                    # list of RGB triplets.  Each triplet represents RGB color (e.g. first is 0,104,55)
                    colors = [0, 104, 55, 36, 157, 83, 112, 193, 100, 145, 208, 104, 207, 235, 133, 221, 241, 145, 242,
                              250, 174, 250, 252, 185, 255, 254, 189, 255, 250, 182, 255, 245, 174, 255, 241, 167, 254,
                              234, 155, 254, 231, 151, 254, 224, 139, 254, 208, 126, 253, 187, 108, 253, 177, 99, 246,
                              122, 73, 243, 107, 66, 165, 0, 38, 144, 12, 149, 63, 6, 65, 0, 0, 0]
                    fillcolor = tuple(colors[tu1:tu2])
                    draw.ellipse((dotx - sub, doty - sub, dotx + sub, doty + sub), fill=fillcolor, outline=(0, 0, 0))

                print(dotx, doty)

                if MainColor != "None":
                    draw.ellipse((dotx - sub, doty - sub, dotx + sub, doty + sub), fill=MainColor, outline=(0, 0, 0))

                if Dens != "yes":
                    if gradi == "yes" or Pol == "yes":
                        draw.ellipse((dotx - sub, doty - sub, dotx + sub, doty + sub), fill=(col), outline=(0, 0, 0))

                if MainColor == "None":
                    if gradi != "yes" and Pol != "yes" and Dens != "yes":
                        draw.ellipse((dotx - sub, doty - sub, dotx + sub, doty + sub), fill=(col), outline=(0, 0, 0))

                if texty == "yes":
                    if scory == "yes":
                        if rand == "yes":
                            ran = random.random() * 100
                            if ran > ranthresh:
                                draw.text((dotx, doty), str(scor), fill="blue")
                        else:
                            draw.text((dotx, doty), str(scor), fill="blue")
                    else:
                        draw.text((dotx, doty), str(Nam), fill="blue")

            if boxy == "yes" and scor > thresh:
                boxd = ImageDraw.Draw(BoxImg)
                clas = int(clas)
                col = colorlist[clas - 1]

                if gradi == "yes":
                    col = colorlist[grad]
                    # redgrad = int(grad *25.5)
                    for guide in range(0, 10):
                        gradcol = colorlist[guide]
                        boxd.ellipse((sub * 10 - sub * 10, sub * guide * 20 - sub * 10 + sub * 10, sub * 10 + sub * 10,
                                      sub * guide * 20 + sub * 10 + sub * 10), fill=(gradcol), outline=(0, 0, 0))

                if Pol == "yes":  # Base colors on polygon outline
                    co = df4.loc[df4['Poly'] == poly].index.values
                    clrs = co[0]
                    col = colorlist[clrs]
                    # col = colorlist[poly]

                if MainColor != "None":
                    col = MainColor

                shape = [(left, top), (right, top)]
                boxd.line(shape, fill=col, width=5)

                shape = [(left, bottom), (right, bottom)]
                boxd.line(shape, fill=col, width=3)

                shape = [(left, top), (left, bottom)]
                boxd.line(shape, fill=col, width=3)

                shape = [(right, top), (right, bottom)]
                boxd.line(shape, fill=col, width=3)

                if texty == "yes":
                    if scory == "yes":
                        boxd.text((left, bottom), str(scor), fill="blue")
                    else:
                        boxd.text((left, bottom), str(Nam), fill="blue")

        lab = images + "  Thresh:" + str(thresh) + "  Density:" + Dens + ", " + str(DensThresh) + ", Circle Rad:" + str(
            sub) + ", Polygon:" + Pol + ", Gradient:" + gradi
        print("lab" + lab)

        if ploty == "yes":
            draw.text((2, 2), lab, fill="brown")
            if df1max > 1:
                for txtclr in range(1, df1max + 1):
                    col = colorlist[txtclr - 1]
                    draw.text((2, 14 * txtclr), str(txtclr), fill=col)

        else:
            boxd.text((2, 2), lab, fill="brown")
            if df1max > 1:
                for txtclr in range(1, df1max + 1):
                    col = colorlist[txtclr - 1]
                    boxd.text((2, 14 * txtclr), str(txtclr), fill=col)

        IMG_NAME = locat2[:-4] + "_DotPlot.png"
        IMG_NAME2 = locat2[:-4] + "_BoxPlot.png"

        # destin = locat + "\\" + IMAGE_NAME
        if ploty == "yes":
            width, height = PlotImg.size
            new_width, new_height = int(width * ImgSiz), int(height * ImgSiz)
            PlotImg_resized = PlotImg.resize((new_width, new_height), Image.BICUBIC)  # was ANTIALIAS then LANCZOS

            if direct2 != "" or (FGuard != 0 or FGuard != 0):
                # This moves if misaligned
                PlotImgFin = PlotImg_resized.crop((FGuard, FGuard, FWidth - FGuard, FHeight - FGuard))
                # This makes plot the same size as image
                PlotImgFin = PlotImgFin.crop((0, 0, FWidth, FHeight))
                print('fguard')
                print(FGuard)
                print(FWidth)
                print(FHeight)
                # print(FIL2)

                # Add pixels
                PlotImgFin.putpixel((0, 0), (0, 0, 0, 255))
                PlotImgFin.putpixel((FWidth - 1, FHeight - 1), (0, 0, 0, 255))
                draw = ImageDraw.Draw(PlotImgFin)
                draw.text((2, 2), lab, fill="brown")
                if df1max > 1:
                    for txtclr in range(1, df1max + 1):
                        col = colorlist[txtclr - 1]
                        draw.text((2, 14 * txtclr), str(txtclr), fill=col)

                PlotImgFin.save(IMG_NAME, 'PNG')

                print(FGuard)
                print(FWidth)
                print(FHeight)
            else:

                PlotImg_resized.save(IMG_NAME, 'PNG')

        if boxy == "yes":
            width, height = BoxImg.size
            new_width, new_height = int(width * ImgSiz), int(height * ImgSiz)
            BoxImg_resized = BoxImg.resize((new_width, new_height), Image.BICUBIC)  # was ANTIALIAS then LANCZOS
            if direct2 != "" or (FGuard != "" and FGuard != 0):
                # This moves if misaligned
                BoxImgFin = BoxImg_resized.crop((FGuard, FGuard, FWidth - FGuard, FHeight - FGuard))
                # This makes plot the same size as image
                BoxImgFin = BoxImgFin.crop((0, 0, FWidth, FHeight))

                # Add pixels
                BoxImgFin.putpixel((0, 0), (0, 0, 0, 255))
                BoxImgFin.putpixel((FWidth - 1, FHeight - 1), (0, 0, 0, 255))
                draw = ImageDraw.Draw(BoxImgFin)
                draw.text((2, 2), lab, fill="brown")
                if df1max > 1:
                    for txtclr in range(1, df1max + 1):
                        col = colorlist[txtclr - 1]
                        draw.text((2, 14 * txtclr), str(txtclr), fill=col)

                BoxImgFin.save(IMG_NAME2, 'PNG')
            else:
                BoxImg_resized.save(IMG_NAME, 'PNG')
