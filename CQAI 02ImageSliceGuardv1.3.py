"""
This will slice the image into slices.  If divide = 1 then it will slice into slices 1024 x 1024.
Because we don't want to cut an object in half at the edge of the slice, we add a guard
zone which overlaps adjacent slices.

For images that are blank or have a very uniform color, it is highly unlikely there will
be positive cells.  I had the program look for slices where the maxima and minima greyscale
values differ by less than 50 (the "difference" variable).  It then creates a blank CSV
file in the "Labeled" folder.

In v1.1 I created a datafile named "ImageData.csv" that saves the image file name, Height,
Width, and guard in a csv file saved in the Annotations folder.  This will allow me to
make plot images that will automatically align perfectly with the original image.

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""


import os
import easygui
from PIL import Image
import shutil
import pandas as pd

direct = easygui.diropenbox('Where are the files?')
direct = os.path.join(direct)
sav = os.path.join(direct, "Extra")

#This is to move blank images to the images/labeled folder. os.path.dirname
#moves the path to the parent folder /images
blnk = os.path.dirname(direct)
annot = os.path.dirname(blnk)
if not os.path.exists(sav):
    os.makedirs(sav)


divide = 1 # divide = 1 results in slices at 1224x1224
greysc = "yes1" #If this is yes it will convert the slices to greyscale before saving
savtolab = "yes" #If this is yes, it will save blank csv files to labeled folder

sizew = int(1024/divide) #Normally this is 1250 but will be divided to make smaller slices
sizet = int(1024/divide) #This was normally 950
guard = int(100/divide)
if guard < 20:
    guard = 20


Image.MAX_IMAGE_PIXELS = None
files = os.listdir(direct)

for images in files:
    DASH = images.count('-')
    if DASH > 1:
        print("You can not have more than one dash '-' in the file names.")
        print("*******Please rename files and re-run program.*******")
        exit()

    for images in files:
        DASH = images.count('-')
        if DASH > 2:
            print("You can not have more than 2 dashes '-' in the file names.")
            print("*******Please rename files and re-run program.*******")
            exit()

# Create a DataFrame with the specified columns
df = pd.DataFrame(columns=["File", "Width", "Height", "Guard", "Xnum", "Ynum", "PNG", "Divide"])

nu = 0

for fil in files:

    nu = nu + 1
    print(nu)
    fil1 = direct + fil
    fil1 = os.path.join(direct, fil)
    fil3 = os.path.join(sav, fil)
    blnk3 = os.path.join(blnk, "Labeled", fil)

    # the os.listdir() will also list folders which will mess things up. This skips it.
    if os.path.isdir(fil1):
        # skip directories
        continue
    elif fil.startswith("._"):  # mac files have these meta data files
        continue
    elif fil.startswith("desktop.ini"):
        continue
    im = Image.open(fil1)
    width, height = im.size



    print(width)
    print(height)
    print()
    xnum = int(width / sizew) + 1
    ynum = int(height / sizet) + 1

    print(xnum)
    print(ynum)
    print(fil)
    Png = fil[:-4] + "SG_" + str(ynum-1) + "-" + str(xnum-1) + "_AllCSV.csv"
    # Add a row to the DataFrame with the file name, width, height, guard, xnum, and ynum values
    df.loc[len(df)] = [fil, width, height, guard, xnum, ynum, Png, divide]

    for y in range(0, ynum):
        for x in range(0, xnum):

            if x == 0:
                x1 = 0
            else:
                x1 = (x * sizew) - guard  # x value left line

            if y == 0:
                y1 = 0
            else:
                y1 = (y * sizet) - guard  # upper line

            rt = (x * sizew) + sizew + guard  # right line
            bt = (y * sizet) + sizet + guard  # bottomline

            #print("x=" + str(x1) + ", y=" + str(y1) + ", rt= " + str(rt) + ", bt= " + str(bt))

            im1 = im.crop((x1, y1, rt, bt))
            fil2 = fil1[:-4] + "SG_" + str(y) + "-" + str(x) + ".jpg"

            #This is to move the file if blank to image\Labeled folder
            blnk2 = blnk3[:-4] + "SG_" + str(y) + "-" + str(x) + ".csv"
            #blnk4 = blnk3[:-4] + "SG_" + str(y) + "-" + str(x) + ".jpg" #if you want to save blank image

            #If the image is greyscale and really uniform and contains no objects to
            #to identify, it adds  CSV file to the "Blank" folder.
            if greysc == "yes":
                im1 = im1.convert("L")
                extrema = im1.getextrema()
                difference = extrema[1] - extrema[0]
                if difference < 50 and savtolab == "yes":
                    df2 = pd.DataFrame()
                    df2.to_csv(blnk2)
                    #im1.save(blnk4) #to save the image also
                else:
                    im1.save(fil2)

            #This is the same if the file is color
            if greysc != "yes":
                im2 = im1.convert("L")
                extrema = im2.getextrema()
                difference = extrema[1] - extrema[0]
                if difference < 50 and savtolab == "yes":
                    df2 = pd.DataFrame()
                    df2.to_csv(blnk2)
                else:
                    im1.save(fil2)

    im.close()
    im1.close()
    shutil.move(fil1, fil3)

# Save the file information as a CSV file in the specified location if it exists then
# append data to the end of the file.
file_path = os.path.join(annot, "Annotations", "ImageData.csv")
if os.path.isfile(file_path):
    # If the file exists, read it into a DataFrame
    df_existing = pd.read_csv(file_path)

    # Check if the "Divide" column exists
    if 'Divide' not in df_existing.columns:
        # If it doesn't exist, add the "Divide" column
        df_existing['Divide'] = pd.NA

        # Write the DataFrame back to the CSV file
        df_existing.to_csv(file_path, index=False)


if not os.path.isfile(file_path):
    df.to_csv(file_path, mode='w', header=True, index=False)
else:

    df.to_csv(file_path, mode='a', header=False, index=False)

