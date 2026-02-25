"""
CQAI 1 Training
Use this program if you want to generate training and test files for LabelImg but
don't want to create a slice for all the images.  This will just save files above
a threshold randomly.  This will slice but only save a random number of files to
create a training and testing folders.  You need to change the totfil variable to
however many files you want to end up being saved.  Make sure to change the greysc
and divide if it needs to be altered

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import easygui
from PIL import Image
import shutil
import random

totfil = 350
divide = 1
greysc = "yes1" #If this is yes it will convert the slices to greyscale before saving

direct = easygui.diropenbox('Where are the files?')
direct = os.path.join(direct)
folder_path = direct
sav = os.path.join(direct, "Extra")

if not os.path.exists(sav):
    os.makedirs(sav)

#This will divide 1250 to get a smaller slice (e.g. 2 will cut size in half
# divide = 1 is normal size
filnum = 0
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



nu = 0

#this just counts the total number of slices that would normally be created but doesn't save
#anything
for fil in files:
    nu = nu + 1
    print(nu)
    fil1 = direct + fil
    fil1 = os.path.join(direct, fil)
    fil3 = os.path.join(sav, fil)

    # the os.listdir() will also list folders which will mess things up. This skips it.

    if os.path.isdir(fil1):
        # skip directories
        continue
    elif fil.startswith("._"):  # mac files have these meta data files
        continue
    elif fil.startswith("desktop.ini"):  # mac files have these meta data files
        continue

    im = Image.open(fil1)
    width, height = im.size
    im.close()

    print(width)
    print(height)
    print()
    xnum = int(width / sizew) + 1
    ynum = int(height / sizet) + 1

    print(xnum)
    print(ynum)

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

            print("x=" + str(x1) + ", y=" + str(y1) + ", rt= " + str(rt) + ", bt= " + str(bt))

            #im1 = im.crop((x1, y1, rt, bt))
            fil2 = fil1[:-4] + "SG_" + str(y) + "-" + str(x) + ".jpg"

            #if greysc == "yes":
                #im1 = im1.convert("L")

            filnum = filnum + 1
            print(filnum)
            #im1.save(fil2)
            # Note: I originally save with a quality of 8 in photoshop.  However, this really doesn't translate to
            # python code.  Therefor, I changed the quality settings in python until the file size was similar to
            # what photoshop makes with a quality 8.
            # When I saved with photoshop I sliced which saved as a gif first which I then converted to jpg.

rat = totfil/filnum
thr = int(rat * 1000000)

#Once the total number of slices that would be created is calculated.  We randomly save a certain percentage
# to make sure save the correct number of random files are saved equal to totfil variable
for fil in files:

    nu = nu + 1
    print(nu)
    fil1 = direct + fil
    fil1 = os.path.join(direct, fil)
    fil3 = os.path.join(sav, fil)

    # the os.listdir() will also list folders which will mess things up. This skips it.
    if os.path.isdir(fil1):
        # skip directories
        continue
    elif fil.startswith("._"):  # mac files have these meta data files
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

    im1 = None
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

            print("x=" + str(x1) + ", y=" + str(y1) + ", rt= " + str(rt) + ", bt= " + str(bt))

            ran = random.random() * 1000000
            print(ran)
            print(thr)
            if ran < thr:
                print('yes')
                im1 = im.crop((x1, y1, rt, bt))
                fil2 = fil1[:-4] + "SG_" + str(y) + "-" + str(x) + ".jpg"

                if greysc == "yes":
                    im1 = im1.convert("L")
                im1.save(fil2)
            else:
                print('no')
    im.close()
    if im1 is not None:
        im1.close()
    shutil.move(fil1, fil3)

print(rat)
print(thr)
print(filnum)
print(totfil)

# This deletes JPG files that are too uniform or just black and white pixels
for file_name in os.listdir(folder_path):
    if file_name.lower().endswith(".jpg"):
        file_path = os.path.join(folder_path, file_name)
        try:
            with Image.open(file_path) as img:
                # Convert image to grayscale
                grayscale_img = img.convert("L")
                # Calculate extrema (min and max pixel values)
                extrema = grayscale_img.getextrema()
                difference = extrema[1] - extrema[0]

                # Get pixel value distribution
                pixel_counts = grayscale_img.histogram()
                total_pixels = sum(pixel_counts)
                intensity_count = sum(pixel_counts[:5]) + sum(pixel_counts[251:])
                intensity_ratio = intensity_count / total_pixels  # Pixels below intensity 5

                # Delete image if it meets any of the criteria
                if difference < 100 or intensity_ratio > 0.95:
                    os.remove(file_path)
                    print(f"Deleted uniform or mostly black/white image: {file_name}")
                else:
                    print(f"Kept non-uniform image: {file_name}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")