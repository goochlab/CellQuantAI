
"""This program identifies cells whose bounding boxes overlap and calculates the overlap between the boxes
It then considers objects two different ones if the area of the rectangular overlap is less than 0.2 (20%) of either
bounding box. This needs the CSV combined file after all the individual CSV files have been joined together.
It will also delete all scores below a certain threshold by assigning a number to the thresh variable

This was modified to include numpy in the deletion process to speed things up

v1.1 previously the column name would have data about the original image.  The NoDups would rename
the column the number 12.  This version preserves the image data and deletes the 12 column
v1.2 This didn't remove rows with values exactly the same for left, right, top, and bottom.
This fixes this problem after the original program is run in the end.

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import pandas as pd
import random
import PIL
import re
from PIL import Image
from PIL import ImageDraw
import math
import easygui
import sys
from sys import getsizeof
import numpy as np

#Image.MAX_IMAGE_PIXELS = None
#locat = "I:\\CI30_534\\CI30 534 AC3 10x_28-33_Junk1.csv"
#locat = "D:\\LabSync Files\\Nicole\\Monkey_AI_Labeled\\CI30_534\\CSV\\CI30 534 AC3 10x_28-33_NoDups.csv"

#Make this 1 if you don't want to eliminate any overlapping objects Normally = 0.8
rat = 0.8
print ("Ratio: " + str(rat))

#This will delete objects whose score is below the thresh.  If you don't want to delete below a
#threshold make this 0
thresh = 0.0
print ("Thresh: " + str(thresh))

direct = easygui.diropenbox('Where are the files?')
folder_selected = direct
direct = os.path.join(direct)
print(direct)
files = os.listdir(direct)


for images in files:
    if not images.endswith(".csv"):
        continue
    elif images.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(images):
        # skip directories
        continue
    else:
        Err = "no"
        DASH = images.count('-')
        if DASH == 2:
            wide1 = re.search('-(.*).csv', images)  # This doesn't capture the second number because there are two -
            wide = re.search('-(.*)AllCSV', wide1.group(1))
        else:
            # Use below if 1 dash in file name
            wide = re.search('-(.*)_AllCSV.csv', images)  # This doesn't capture the second number because there are two -
            # wide = re.search('-(.*).c', wide1.group(1))

        tall = re.search('SG_(.*)-', images)
        # wide = re.search('-(.*).jpg', images)

        try:
            # code that may raise an AttributeError
            colum1 = wide.group(1)
        except AttributeError:
            # handle the error
            colum1 = "No"
            Err = "yes"
        #colum1 = wide.group(1)  # if 0 than width = 1350
        try:
            # code that may raise an AttributeError
            row1 = tall.group(1)
        except AttributeError:
            # handle the error
            row1 = "No"
            Err = "yes"
        #row1 = tall.group(1)  # if 0 than tall = 1050
        le = (len(str(colum1)) + len(str(row1)) + 12) * -1
        # le tells us how to isolate the base name
        nam1 = images[:le]
        # print('row: '+row)
        # print('column: ' + colum)
        # print(nam1)

        locat = os.path.join(direct, images)
        #locat = images #I call this images even though it's AllCSV.csv files
        print(locat)

        PlotFile = []
        df1 = []
        dele = []
        Over = []
        Frames = []
        Remove = []
        Deleter = []
        DELETER = ""
        NODUPS = []
        df1 = []
        Filler = []
        ObjArray = []


        x = 0
        MinDist = 100

        df1 = pd.read_csv(locat)
        Overlap = []
        Topper = []
        dele = []

        # Find column names that start with "GRD"
        grd_columns = df1.filter(regex='^GRD').columns

        # Check if any such column exists and save the first one as 'Param'
        if len(grd_columns) > 0:
            Param = grd_columns[0]
        else:
            print("No column starts with 'GRD'")

        df1.sort_values(by=['Left'], inplace=True)  # This sorts values from low to high by left


        Topper = pd.DataFrame.from_dict(Topper)

        SHAP = (df1.shape)
        r = SHAP[0]  # rows
        c = SHAP[1]  # columns
        # Number of rows and columns
        # print(r,c)

        ObjArray = df1.to_numpy()
        #print(ObjArray)

        #This tells you how large the array is
        print(ObjArray.nbytes)

        df1.sort_values(by=['Object'], inplace=True)
        ObjArray2 = df1.to_numpy()
        #exit()

        #print(ObjArray[2,3]) # starting from 0, 2 is row and 3 is column

        colorlist = ["red", "green", "orange", "blue", "yellow"]

        for x in range(0, r):  # (0,r) for x in range(0,5350):
            unnam = ObjArray[x,0]
            #unnam = (df1.loc[x, 'Object'])
            dotx = ObjArray[x,5]
            #dotx = (df1.loc[x, 'Dotx'])
            doty = ObjArray[x,6]
            #doty = (df1.loc[x, 'Doty'])
            scor = ObjArray[x,7]
            #scor = (df1.loc[x, 'Score'])
            clas = ObjArray[x,8]
            #clas = (df1.loc[x, 'Class'])
            left = ObjArray[x,1]
            #left = (df1.loc[x, 'Left'])
            right = ObjArray[x,2]
            #right = (df1.loc[x, 'Right'])
            top = ObjArray[x,3]
            #top = (df1.loc[x, 'Top'])
            bottom = ObjArray[x,4]
            #bottom = (df1.loc[x, 'Bottom'])
            area = (right - left) * (bottom - top)  # area of rectangle

            per=str(x / r * 100)
            print('\rPercent: '+ per, end='', flush=True)

            if scor < thresh:
                dele.append([unnam])
                ObjArray2[unnam, 0] = 999999999  # Mark for delete
                continue


            for y in range(x + 1, r):  # (x+1,r)for y in range(x+1, r):
                #unnam2 = (df1.loc[y, 'Object'])
                unnam2 = ObjArray[y,0]
                #dotx1 = (df1.loc[y, 'Dotx'])
                dotx1 = ObjArray[y,5]
                #doty1 = (df1.loc[y, 'Doty'])
                doty1 = ObjArray[y,6]
                #scor1 = (df1.loc[y, 'Score'])
                scor1 = ObjArray[y,7]
                #clas1 = (df1.loc[y, 'Class'])
                clas1 = ObjArray[y,8]
                #left1 = (df1.loc[y, 'Left'])
                left1 = ObjArray[y,1]
                #right1 = (df1.loc[y, 'Right'])
                right1 = ObjArray[y,2]
                #top1 = (df1.loc[y, 'Top'])
                top1 = ObjArray[y,3]
                #bottom1 = (df1.loc[y, 'Bottom'])
                bottom1 = ObjArray[y,4]
                area1 = (right1 - left1) * (bottom1 - top1)  # area of rectangle
                dist = math.sqrt((dotx - dotx1) ** 2 + (doty - doty1) ** 2)

                if left1 > right:
                    #print('break')
                    break

                #if scor1 < thresh:
                    #continue

                # If true then rectangles overlap somewhere
                if (((left > left1 and left < right1) or (right > left1 and right < right1) or (
                        left < left1 and right > right1) or (left1 < left and right1 > right)) and (
                        (top > top1 and top < bottom1) or (bottom > top1 and bottom < bottom1) or (
                        top < top1 and bottom > bottom1) or (top1 < top and bottom1 > bottom))):
                    #print("Yes**************************************")

                    # Determine the left side of overlapped rectangle
                    if (left > left1 and left < right1):
                        left3 = left
                    else:
                        left3 = left1

                    # Determine the right side of overlapped rectangle
                    if (right > left1 and right < right1):
                        right3 = right
                    else:
                        right3 = right1

                    # Determine the top side of overlapped rectangle
                    if (top > top1 and top < bottom1):
                        top3 = top
                    else:
                        top3 = top1

                    # Determine the bottom side of overlapped rectangle
                    if (bottom > top1 and bottom < bottom1):
                        bottom3 = bottom
                    else:
                        bottom3 = bottom1

                    # examination found that if ratio or ratio1 is above 0.2 it is highly likely
                    # they're 2 different objects
                    area3 = (right3 - left3) * (bottom3 - top3)  # area of overlap
                    #print("X: " + str(unnam) + "  Y: " + str(unnam2) + "  Overlap: " + str(area3))
                    if area == 0:
                        area = 0.00000001

                    if area1 == 0:
                        area1 = 0.00000001
                    ratio = area3 / area  # ratio of overlapped rectangle to first rectangle
                    ratio1 = area3 / area1  # ratio of overlapped rectangle to second rectangle

                    #print("area1:" + str(area))
                    #print("area2:" + str(area1))
                    #print("area3:" + str(area3))

                    if (ratio > rat or ratio1 > rat):

                        if scor < scor1:
                            # df1.drop(labels=x, axis=0, inplace=True)
                            dele.append([unnam])

                            if 0 <= unnam < ObjArray2.shape[0]:  # Check if unnam is within valid bounds
                                ObjArray2[unnam, 0] = 999999999  # Mark for delete
                            else:
                                print(f"Skipping out-of-bounds index: {unnam}")

                        else:
                            # df1.drop(labels=y, axis=0, inplace=True)
                            dele.append([unnam2])

                            if 0 <= unnam2 < ObjArray2.shape[0]:  # Check if unnam2 is within valid bounds
                                ObjArray2[unnam2, 0] = 999999999  # Mark for delete
                            else:
                                print(f"Skipping out-of-bounds index: {unnam2}")

            Over = []
            Overlap = []
            laster = 0

        #Below deletes using numpy-------------------------------

        NODUPS = pd.DataFrame.from_dict(ObjArray2)
        NODUPS.index.name = 'Object'
        NODUPS = NODUPS.rename(
            columns={0: 'Object', 1: 'Left', 2: 'Right', 3: 'Top', 4: 'Bottom', 5: 'Dotx', 6: 'Doty', 7: 'Score',
                     8: 'Class', 9: 'Column', 10: 'Row', 11: 'File'})
        NODUPS = NODUPS.drop_duplicates(subset=['Object'], keep=False)

        # Add an empty column named after the 'Param' variable
        NODUPS[Param] = np.nan

        # Delete column named "12"
        if "12" in str(NODUPS.columns):
            NODUPS = NODUPS.drop(12, axis=1)
        else:
            print("Column '12' does not exist in the DataFrame.")

        # In order to delete duplicates I need to convert it to a pandas dataframe
        Deleter = pd.DataFrame.from_dict(dele)

        # This deletes the duplicate objects
        Deleter.drop_duplicates(inplace=True)

        # This saves a file of deleted objects
        DELETER = nam1 + row1 + "-" + colum1
        DELETER = DELETER + "Deleted.csv"
        DELETER = os.path.join(direct, DELETER)
        #print(DELETER)
        #Deleter.to_csv(DELETER)

        # List converts back to list
        dele = Deleter.values.tolist()

        # Determines the row and columns of Deleter
        r1 = len(dele)

        # Turns to a pandas dataframe

        if Err == "no":
            FILLER = nam1 + row1 + "-" + colum1
        else:
            FILLER = images.replace('.csv', '_')
        FILLER = os.path.join(direct, FILLER)
        FILLER = FILLER + "NoDups.csv"


        NODUPS.to_csv(FILLER, index=False)

#RemoveDuplicates does not remove rows that have the exact same values for
#'Left', 'Right', 'Top', and 'Bottom'.  This removes these rows on the
#backend

folder_selected = os.path.join(folder_selected)
print(folder_selected)


files = os.listdir(folder_selected)

for filename in files:
    if filename.endswith("NoDups.csv"):
        if filename.startswith("._"):  # mac files have these meta data files
            continue
        if os.path.isdir(filename):
            # skip directories
            continue
        print(filename)
        df = pd.read_csv(os.path.join(folder_selected, filename))  # Load CSV file into a pandas dataframe

        # If "Left", "Right", "Top", and "Bottom" are the same between rows, delete the row with the lower "Score"
        df = df.sort_values('Score', ascending=False).drop_duplicates(subset=['Left', 'Right', 'Top', 'Bottom'])

        # Renumber the "Object" column with integers starting with 1
        df['Object'] = range(1, len(df) + 1)

        # Save as a new CSV file with a "D" appended to the front of the name
        df.to_csv(os.path.join(folder_selected, filename), index=False)

