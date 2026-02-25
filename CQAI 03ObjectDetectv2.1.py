"""
Not run in pycharm before becuase you need to conda activate tensorflow.
Usually run in C:\Users\gooch\Documents\Tensorflow
This combines the programs ObjectDetect and 1024 CombineCSVPlusMultiSizeGuardv1.3.py.
After training your model, this takes sliced images from ImageSliceGuard.py and
identifies cells in the slices.  It then saves this as CSV files individually for
each slice initially but then combines them into a single CSV file for each image
that was sliced.


© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""


import os
import wget
import tarfile
import zipfile
import matplotlib
import os
import pandas as pd
import random
import PIL
import re
from PIL import Image
from PIL import ImageDraw

import shutil
import numpy as np


div = input("How many divisions per image: ")
filcount = 0

DATER = input("Enter Date Of my_centernet: ")
piper = "pipeline" + DATER + ".config"

THRESHOLD = float(input("Enter threshold: "))

BASE_DIRECTORY = ""

BASE_DIRECTORY = os.path.join('C:', os.sep, 'Users' ,'gooch', 'Documents', 'Tensorflow')
# BASE_DIRECTORY = "C:\\Users\\gooch\\Documents\\Tensorflow"

# os.environ["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"] + ":/usr/local/cuda/lib64"
#os.environ['PYTHONPATH'] = r"C:\Users\gooch\Documents\Tensorflow\models"

UNIQUE_MODIFIER =DATER
CUSTOM_MODEL_NAME = 'my_centernet' + '_' + UNIQUE_MODIFIER
PRETRAINED_MODEL_NAME = 'centernet_hg104_512x512_kpts_coco17_tpu-32'
PRETRAINED_MODEL_URL = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/centernet_hg104_512x512_kpts_coco17_tpu-32.tar.gz'
TF_RECORD_SCRIPT_NAME = 'generate_tfrecord.py'
LABEL_MAP_NAME = "label_map" + DATER + ".pbtxt"

paths = {
    'WORKSPACE_PATH': os.path.join(BASE_DIRECTORY, 'Workspace'),
    'ANNOTATION_PATH': os.path.join(BASE_DIRECTORY, 'Workspace', CUSTOM_MODEL_NAME, 'Annotations'),
    'MODEL_PATH' : os.path.join(BASE_DIRECTORY, 'Workspace'),
    'CHECKPOINT_PATH': os.path.join(BASE_DIRECTORY, 'Workspace' ,CUSTOM_MODEL_NAME),
    'OUTPUT_PATH': os.path.join(BASE_DIRECTORY, 'Workspace', CUSTOM_MODEL_NAME, 'Output'),
    'TFJS_PATH' :os.path.join(BASE_DIRECTORY, 'Workspace' ,CUSTOM_MODEL_NAME, 'tfjsexport'),
    'TFLITE_PATH' :os.path.join(BASE_DIRECTORY, 'Workspace' ,CUSTOM_MODEL_NAME, 'tfliteexport'),
    'IMAGE_PATH': os.path.join(BASE_DIRECTORY, 'Workspace' ,CUSTOM_MODEL_NAME, 'Images'),
    'PRETRAINED_MODEL_PATH': os.path.join(BASE_DIRECTORY, 'Workspace' ,'pre-trained-models'),
    'SCRIPTS_PATH': os.path.join(BASE_DIRECTORY ,'scripts'),
    # 'PROTOC_PATH':os.path.join(BASE_DIRECTORY,'protoc')
}

files = {
    'PIPELINE_CONFIG' :os.path.join(paths['ANNOTATION_PATH'], piper),
    'TF_RECORD_SCRIPT': os.path.join(paths['SCRIPTS_PATH'], TF_RECORD_SCRIPT_NAME),
    'LABELMAP': os.path.join(paths['ANNOTATION_PATH'], LABEL_MAP_NAME)
}


TRAIN_IMAGES = os.path.join(paths['IMAGE_PATH'], 'Train')
TEST_IMAGES = os.path.join(paths['IMAGE_PATH'], 'Test')
EVAL_IMAGES = os.path.join(paths['IMAGE_PATH'], 'Unlabeled')
PROCESSED_IMAGES = os.path.join(paths['IMAGE_PATH'], 'Labeled')

import cv2
import numpy as np
#from matplotlib import pyplot as plt

#------------------------------------------------------------------------------

import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
from keras import backend as K

#matplotlib inline

category_index = label_map_util.create_category_index_from_labelmap(files['LABELMAP'])

#-------------------------------------------------------------------------------


# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
detection_model = model_builder.build(model_config=configs['model'], is_training=False)
import pandas as pd

# Restore checkpoint
checkpoints = []
for x in os.listdir(paths['CHECKPOINT_PATH']):
    if x[0:5] == 'ckpt-':
        checkpoints.append(int(x[5:x.index('.')]))

checkpoints = sorted(checkpoints)
checkpoint = checkpoints[-1]

ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], ('ckpt-' + str(checkpoint)))).expect_partial()


@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections

#------------------------------------------------------------------------------
eval_images_count = len([name for name in os.listdir(EVAL_IMAGES) if os.path.isfile(os.path.join(EVAL_IMAGES, name))])
processed_images_count = len([name for name in os.listdir(PROCESSED_IMAGES) if os.path.isfile(os.path.join(PROCESSED_IMAGES, name))])
total_images_count = eval_images_count + processed_images_count

print(f'Number of files in EVAL_IMAGES: {eval_images_count}')
print(f'Number of files in PROCESSED_IMAGES: {processed_images_count}')
print(f'Total number of files: {total_images_count}')

for EVAL_IMAGE in os.listdir(EVAL_IMAGES):
    if EVAL_IMAGE.endswith(".jpg"):  # or EVAL_IMAGE.endswith(".gif"): #add other file extensions here

        filcount = filcount + 1
        IMAGE_NAME = os.path.join(PROCESSED_IMAGES, EVAL_IMAGE)
        img = cv2.imread(os.path.join(EVAL_IMAGES, EVAL_IMAGE))
        image_np = np.array(img)

        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = detect_fn(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                      for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        label_id_offset = 1
        image_np_with_detections = image_np.copy()

        #viz_utils.visualize_boxes_and_labels_on_image_array(
            #image_np_with_detections,
            #detections['detection_boxes'],
            #detections['detection_classes'] + label_id_offset,
            #detections['detection_scores'],
            #category_index,
            #use_normalized_coordinates=True,
            #max_boxes_to_draw=1000, #For images
            #min_score_thresh=0.08, #For images
            #agnostic_mode=False)

        # Kevin Added below until df.to_csv...
        boxes = np.squeeze(detections['detection_boxes'])  # Kevin added from here to df.to_csv
        scores = np.squeeze(detections['detection_scores'])
        cls = detections['detection_classes'] + label_id_offset

        # set a min thresh score, say 0.01
        min_score_thresh = THRESHOLD
        bboxes = boxes[scores > min_score_thresh]
        sscores = scores[scores > min_score_thresh]
        ccls = cls[scores > min_score_thresh]

        # get image size
        im_width, im_height, c = image_np_with_detections.shape
        final_box = []
        nu = 0

        for box in bboxes:
            ymin, xmin, ymax, xmax = box
            SC = sscores[nu]
            classes = ccls[nu]
            # columns [left, right, top, bottom, score, classes]
            final_box.append([xmin, xmax, ymin, ymax, SC, classes])
            nu = nu + 1

        df = pd.DataFrame.from_dict(final_box)
        #print(EVAL_IMAGE)
        num_rows = df.shape[0]
        print(f"{EVAL_IMAGE}: {num_rows}: {filcount} of {eval_images_count}")
        #print(df)
        df.to_csv(IMAGE_NAME[0:-4] + ".csv")

        # plt.imshow(cv2.cvtColor(image_np_with_detections, cv2.COLOR_BGR2RGB))
        # plt.show()

        # REMOVE # BELOW "viz_utils" above TO LABEL IMAGES
        # plt.imsave(os.path.join(PROCESSED_IMAGES, EVAL_IMAGE), cv2.cvtColor(image_np_with_detections, cv2.COLOR_BGR2RGB))
        # K.clear_session()

"""This program will combine all the individual CSV files into one whole file.
It will do it to all the files in a folder.  It will do it with different size
files (change the divide value).  It will also only plot values on the half
of the gaurd nearest the center of the picture so there's no overlap of objects
in the guard region.

v1.1 opens the ImageData.csv file in the Annotations folder and adds a column
name that contains the Guard, Width, and Height of the original image file.
The column name has a "GRD" in the beginning followed by the gaurd pixels,
an "X" followed by the width, and a "Y" with the height.  This needs to be
used in conjunction with 1024ImageSliceGuardv1.1.py.

v1.2 calculates divide by taking the "Guard" value from the first row in the
ImageData.csv file and makes divide = 100/Guard

PROCESSED_IMAGES = os.path.join(paths['IMAGE_PATH'], 'Labeled')

direct = easygui.diropenbox('Where are the files?')
locat = os.path.join(direct)
"""

SaveImg = "No"

#This will divide 1250 to get a smaller slice (e.g. 2 will cut size in half
# divide = 1 is normal size


#Do not change.  This is used later on to determing if a object in the guard
#zone should be included
good = "yes"



locat = PROCESSED_IMAGES
print(locat)

#sav7 = os.path.join(locat, "Extra")
sav7 =  os.path.join(paths['IMAGE_PATH'], 'Labeled', 'Extra')
if not os.path.exists(sav7):
    os.makedirs(sav7)
print(sav7)


blnk = os.path.dirname(paths['IMAGE_PATH'])
annot = os.path.dirname(blnk)
ImageDat = os.path.join(paths["ANNOTATION_PATH"], "ImageData.csv")
print(ImageDat)
if os.path.exists(ImageDat):
    dfFil = pd.read_csv(ImageDat)
    print(dfFil)
    #div = dfFil['Divide'].iloc[0]
    #div = int(100/div) #this will give an error if guard is less than 20

divide = int(div)
print(divide)
print('Merging files')

#Note: Since tensorflow decreases the size to 512 x 512 anyways I decided to make the
#size square and a multiple of 512 which is 1024.  However, the program adds a
#100 pixel guard zone so the images will be 1224 instead.  I may want to make this
#a 824 x 824 instead.
sizew = int(1024/divide) #Normally this is 1250 but will be divided to make smaller slices
sizet = int(1024/divide) #This was normally 950
guard = int(100/divide)
if guard < 20:
    guard = 20



files = os.listdir(locat)

for images in files:
    DASH = images.count('-')
    if DASH > 2:
        print("You can not have more than 2 dashes '-' in the file names.")
        print("*******Please rename files and re-run program.*******")
        exit()


FILNAM = []

for images in files:
    if not images.endswith(".csv"):
        continue
    elif images.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(images):
        # skip directories
        continue
    else:

        DASH = images.count('-')
        if DASH == 2:
            wide1 = re.search('-(.*)sv', images)  # This doesn't capture the second number because there are two -
            wide = re.search('-(.*).c', wide1.group(1))
        else:
            # Use below if 1 dash in file name
            wide = re.search('-(.*).csv', images)  # This doesn't capture the second number #because there are two -
            # wide = re.search('-(.*).c', wide1.group(1))

        tall = re.search('SG_(.*)-', images)
        #wide = re.search('-(.*).jpg', images)

        colum = wide.group(1)  # if 0 than width = 1350
        row = tall.group(1)  # if 0 than tall = 1050
        le = (len(str(colum)) + len(str(row)) + 5) * -1
        #le tells us how to isolate the base name
        nam1 = images[:le]

        FILNAM.append([nam1, row, colum])

#In order to delete duplicates I need to convert it to a pandas dataframe
FILNAM = pd.DataFrame.from_dict(FILNAM)

#Sort but need to consider the numbers are stringspd.to_numeric turns to numbers
cols = [1, 2]
FILNAM[cols] = FILNAM[cols].apply(pd.to_numeric, errors='coerce', axis=1)
FILNAM = FILNAM.sort_values([1, 2], ascending = (True, True))


#This deletes the duplicate objects giving you the last files
#This can then be used to find how many columns and rows are in the merged image.
FILNAM.drop_duplicates(subset=0, keep='last', inplace=True)

print(FILNAM)

SHAP = (FILNAM.shape)
r1 = SHAP[0] #rows
c1 = SHAP[1] #columns
#print(r1)

for x1 in range(0, r1):
    nam = FILNAM.iloc[x1][0]
    colum = FILNAM.iloc[x1][2]
    colum = int(colum)
    row = FILNAM.iloc[x1][1]
    row = int(row)
    PlotFile = []

    for y in range(0, int(row)+1):
        for x in range(0, int(colum)+1):

            width = sizew + (2*guard) #was 1450
            height = sizet + (2*guard) #was 1150
            if x == 0:
                width = sizew + guard #was 1350

            if y == 0:
                height = sizet + guard #was1050

            # curr = locat + nam + str(y) + "-" + str(x) + ".jpg"  # ".plot.png"
            tnam = nam + str(y) + "-" + str(x) + ".csv"
            CSV_NAM = os.path.join(locat, tnam)
            CSVSAV = os.path.join(sav7, tnam)

            #print("row-height", row, height)
            #print("column-width", colum, width)

            df1 = pd.read_csv(CSV_NAM)

            SHAP = (df1.shape)
            r = SHAP[0]  # rows
            c = SHAP[1]  # columns

            colorlist = ["red", "green", "orange", "blue", "yellow"]

            for x7 in range(0, r):
                left = (df1.loc[x7, '0']) * width
                right = (df1.loc[x7, '1']) * width
                top = (df1.loc[x7, '2']) * height
                bottom = (df1.loc[x7, '3']) * height
                scor = (df1.loc[x7, '4'])
                clas = (df1.loc[x7, '5'])
                # csv columns [left, right, top, bottom, score, class] class according to label_map.pbtxt
                # 1=Oligodendrocyte, 2=Question, 3=Interneuron, 4=Pyramidal, 5=Axon
                col = colorlist[clas - 1]

                dotx = (left + right) / 2  # place dot in middle of bounding box
                doty = (top + bottom) / 2
                #print(dotx, doty)

                #If on the left half of the leftmost guard and not a left edge slice
                if dotx < (guard / 2) and x > 0:
                    good = "no"

                #If on the right half of the rightmost guard and not a right edge slice
                if dotx > (sizew + (guard * 1.5)) and x < (int(colum) + 1):
                    good = "no"

                # If on the top half of the top guard and not top edge slice
                if doty < (guard / 2) and y > 0:
                    good = "no"

                # If on the bottom half of the bottom guard and not a bottom edge slice
                if doty > (sizet + (guard * 1.5)) and x < (int(row) + 1):
                    good = "no"


                x1 = int(x) * sizew #was 1250  x value
                y1 = int(y) * sizet #was 950
                # rt = (x*1250) + 1250 # right
                # bt = (y*950) + 950 # bottom

                if y == 0:
                    y1 = y1 + guard #was 100

                if x == 0:
                    x1 = x1 + guard #was 100

                left1 = left + x1
                right1 = right + x1
                top1 = top + y1
                bottom1 = bottom + y1
                dotx1 = dotx + x1
                doty1 = doty + y1

                if good == "yes":
                    PlotFile.append([left1, right1, top1, bottom1, dotx1, doty1, scor, clas, x, y, tnam])

                good = "yes"

                # print(CSV_NAME)
                #print(left)
                #print(right)
                #print(top)
                #print(bottom)
                # print(IMAGE_NAME)
                #print()


            shutil.move(CSV_NAM, CSVSAV)

    ender = str(row) + "-" + str(colum) + "_AllCSV.csv"
    SCSV1 = nam + str(row) + "-" + str(colum) + "_AllCSV.csv"
    SCSV = os.path.join (locat, SCSV1)
    print(SCSV)

    df = pd.DataFrame.from_dict(PlotFile)
    df.index.name = 'Object'
    df_new = df.rename(columns={0: 'Left', 1: 'Right', 2: 'Top', 3: 'Bottom', 4: 'Dotx', 5: 'Doty', 6: 'Score', 7: 'Class', 8: 'Column', 9: 'Row', 10: 'File'})
    df_new.to_csv(SCSV)


    FWidth = 0
    FHeight = 0
    FGuard = 0

    # This chooses the file name to look up in the ImageData.csv file.  Since the original file
    # name may have changed it looks for it in the AllCSV.csv "File" column
    if os.path.exists(ImageDat):
        # Assign the first value in the "File" column to the variable FIL
        FIL = dfFil.loc[0, 'File']
        # Find the index of the last occurrence of "SG" in the FIL string
        index = FIL.rfind('SG')
        # Remove the part of the string after the last "SG"
        FIL2 = SCSV1

        # Find a row in the dfFil DataFrame where the value in the "PNG" column begins with FIL2
        rowmatch = dfFil[dfFil['PNG'].str.startswith(FIL2)]
        if not rowmatch.empty:
            FWidth = int(rowmatch['Width'].iloc[0])
            FHeight = int(rowmatch['Height'].iloc[0])
            FGuard = int(rowmatch['Guard'].iloc[0])
            Titl = "GRD" + str(FGuard) + "X" + str(FWidth) + "Y" + str(FHeight)

            # Load the CSV file into a DataFrame
            dfNext = pd.read_csv(SCSV)
            dfNext[Titl] = np.nan
            dfNext.to_csv(SCSV, index=False)
        else:
            print(f'No matching row found for {FIL2}')

print('Done')

# =======================
# Delete .jpg in Unlabeled and .csv in Labeled/Extra
# =======================

# Unlabeled images are in EVAL_IMAGES
UNLABELED_FOLDER = EVAL_IMAGES
if os.path.isdir(UNLABELED_FOLDER):
    for f in os.listdir(UNLABELED_FOLDER):
        if f.lower().endswith(".jpg"):
            try:
                os.remove(os.path.join(UNLABELED_FOLDER, f))
            except:
                pass

LABELED_EXTRA_FOLDER = os.path.join(PROCESSED_IMAGES, "Extra")
if os.path.isdir(LABELED_EXTRA_FOLDER):
    for f in os.listdir(LABELED_EXTRA_FOLDER):
        if f.lower().endswith(".csv"):
            try:
                os.remove(os.path.join(LABELED_EXTRA_FOLDER, f))
            except:
                pass

