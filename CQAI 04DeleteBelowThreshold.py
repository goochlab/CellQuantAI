"""
This will just open the .csv files and delete all rows with a score below a certain
threshold.  The remove duplicates will only work if you renumber the Object column.
This adds the "T" and threshold to the end of the file name.

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd

root = tk.Tk()
root.withdraw()

thresh = 0.15
ender = "T" + str(thresh)

folder_path = filedialog.askdirectory()

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        print(filename)
        file_path = os.path.join(folder_path, filename)
        name_part, ext = os.path.splitext(filename)
        newfil = name_part + ender + ext
        df = pd.read_csv(file_path)
        df = df[df['Score'] >= thresh]
        df = df.reset_index(drop=True)
        df['Object'] = df.index #renumber Object becuase will throw errors if not
        new_file_path = os.path.join(folder_path, newfil)
        df.to_csv(new_file_path, index=False)