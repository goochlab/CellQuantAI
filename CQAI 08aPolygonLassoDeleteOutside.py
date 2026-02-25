"""
You need to run PolygonLasso.py first.  This will delete all the objects that are outside all polygons.
If you plan on running PolygonLasso.py again make sure to make "DelPoly" = "yes"
2023-10-03 Added code that preserves the original image size

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import pandas as pd
from tkinter import filedialog
from tkinter import Tk

DelPoly = "yes1"  # if yes then it will delete the ‘Poly’, ‘Polygon’, ‘Counts’, and ‘Area’ columns before saving

root = Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()

for file in os.listdir(folder_selected):
    if file.startswith("._"):  # mac files have these meta data files
        continue
    if file.endswith(".csv"):
        print(file)
        file_path = os.path.join(folder_selected, file)
        data = pd.read_csv(file_path)

        # Find column names that start with "GRD"
        grd_columns = data.filter(regex='^GRD').columns

        # Check if any such column exists and save the first one as 'Param'
        if len(grd_columns) > 0:
            Param = grd_columns[0]
        else:
            print("No column starts with 'GRD'")

        df1 = data[
            ['Object', 'Left', 'Right', 'Top', 'Bottom', 'Dotx', 'Doty', 'Score', 'Class', 'Column', 'Row', 'File',
             'Poly']]
        df2 = data[['Polygon', 'Counts', 'Area']]
        df1 = df1[df1['Poly'] != "Outside"]
        df1.reset_index(drop=True, inplace=True)
        df2.reset_index(drop=True, inplace=True)
        result = pd.concat([df1, df2], axis=1)
        result['Object'] = result.index  # renumber Object becuase will throw errors if not
        result = result[result['Left'].notna()]
        # Add an empty column named after the 'Param' variable
        result[Param] = None

        if DelPoly == "yes":
            result.drop(['Poly', 'Polygon', 'Counts', 'Area'], axis=1, inplace=True)

        output_file_name = "O" + os.path.basename(file)
        output_file_path = os.path.join(folder_selected, output_file_name)
        result.to_csv(output_file_path, index=False)