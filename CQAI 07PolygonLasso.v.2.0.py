"""
V1.0 This will not export a Poly CSV file if the P.csv file doesn't
contain a polygon (i.e. len(df2) = 0).
V1.1 the P.csv files only need to have similar names in this version.
It just looks for the most familiar beginnings.  I also removed the
part that makes sure there's a corresponding P.csv file

V2.0 Important change.  The polygon was shifted by the guard zone.  This
was corrected in V2.0.  I also made it check to see if the CSV has
already been run through PolygonLasso and updated since this will give
errors.

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import easygui
from PIL import Image
from PIL import ImageFilter
import pandas as pd
import cv2
import numpy as np
import re
from PIL import ImageDraw
import shutil


def common_prefix(str1, str2):
    i = 0
    while i < len(str1) and i < len(str2) and str1[i] == str2[i]:
        i += 1
    return str1[:i]


pres = 0

direct = easygui.diropenbox('Where are the plots?')
locat = os.path.join(direct)
files = os.listdir(locat)

Image.MAX_IMAGE_PIXELS = None

files = os.listdir(locat)

for CSVS in files:
    PolNum = 1
    if not CSVS.endswith(".csv"):
        continue
    elif CSVS.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(CSVS):  # skip directories
        continue
    elif CSVS.endswith("P.csv"):
        continue
    else:
        CSVS_NAME = os.path.join(locat, CSVS)

        # Find the "P.csv" file whose name most closely matches the beginning of the CSVS file
        matches = {f: len(common_prefix(CSVS, f)) for f in files if f.endswith("P.csv")}
        PolyImg = max(matches, key=matches.get)
        print(CSVS + " - " + PolyImg)

        POLY_NAME = os.path.join(locat, PolyImg)
        df1 = []  # Raw data
        df2 = []  # Polygon x,y coordinates
        df3 = []  # Coordinates for the current polygon
        df5 = []  # Summary of counts per polygon and area

        if 'polyarr' in dir():
            print('Section Done!')
            del polyarr

        df1 = pd.read_csv(CSVS_NAME)  # Detected cells
        SHAP = (df1.shape)
        df1["Poly"] = pd.NaT  # Makes a new column named Poly that's empty
        r1 = SHAP[0]  # rows
        c1 = SHAP[1]  # columns

        # --- NEW: stop if a column named "Polygon" exists ---
        if "Polygon" in df1.columns:
            print(f"Error: {CSVS} already contains a 'Polygon' column. Stopping program.")
            exit()  # stops the script immediately

        # --- NEW: extract GRD shift from column ---
        grd_cols = [col for col in df1.columns if col.startswith("GRD")]
        if grd_cols:
            grd_col = grd_cols[0]  # use first GRD column
            shift_match = re.search(r'GRD(\d+)X', grd_col)
            if shift_match:
                shift = int(shift_match.group(1))  # pixels to shift polygon up and left
            else:
                shift = 0
        else:
            shift = 0
        # --- END NEW ---

        df2 = pd.read_csv(POLY_NAME)
        if len(df2) == 0:
            print("No polygon coordinates found. Skipping export.")
            continue

        df4 = df2.drop_duplicates(subset=['Polygon'], keep="first")
        df5 = df4[['Polygon']].copy()
        df5.reset_index(drop=True, inplace=True)
        SHAP5 = (df5.shape)
        r5 = SHAP5[0]
        df5["Counts"] = pd.NaT  # Makes a new column named Counts that's empty
        df5["Area"] = pd.NaT  # Makes a new column named Area that's empty
        df5.loc[r5, 'Counts'] = r1
        df5.loc[r5, 'Polygon'] = "Total"

        SHAP2 = (df4.shape)
        r2 = SHAP2[0]  # rows
        c2 = SHAP2[1]  # columns

        for t in range(0, r2):
            count = 0  # zeroes out counts for this polygon
            Pol = (df4.iloc[t, 0])

            df3 = df2.loc[df2['Polygon'] == Pol]
            # --- MODIFIED: apply guard zone shift and use float32 for safety ---
            polyarr = df3[["X", "Y"]].to_numpy(dtype=np.float32)
            polyarr[:,0] += shift  # shift X right
            polyarr[:,1] += shift  # shift Y down
            # --- END MODIFIED ---

            for x in range(0, r1):
                dotx = (df1.loc[x, 'Dotx'])
                doty = (df1.loc[x, 'Doty'])

                dist = cv2.pointPolygonTest(polyarr, (dotx, doty), False)
                if dist < 0:
                    if pd.isnull(df1.at[x, 'Poly']):
                        df1.at[x, 'Poly'] = "Outside"
                else:
                    df1.at[x, 'Poly'] = Pol
                    count = count + 1

            df5.loc[t, 'Counts'] = count
            area = cv2.contourArea(polyarr)
            df5.loc[t, 'Area'] = area

        print(df5)

        SAV = "Poly" + CSVS
        SAV1 = os.path.join(locat, SAV)
        df1 = pd.concat([df1, df5], axis=1)
        df1.to_csv(SAV1, index=False)
