"""
This will delete all the objects that are inside polygons.  If you plan on running
PolygonLasso.py again make sure to make "DelPoly" = "yes"

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

folder_path = filedialog.askdirectory()

DelPoly = "yes" #If "yes" than will delete Poly, Polygon, Counts, and Area columns
# Iterate through all the CSV files in the folder
for file in os.listdir(folder_path):
  if file.endswith(".csv"):
    # Read the CSV file into a Pandas dataframe
    df = pd.read_csv(os.path.join(folder_path, file))

    # Remove rows where the Poly column does not contain "Outside"
    df = df[df["Poly"] == "Outside"]

    # Renumber the Objects column
    df["Object"] = range(len(df))

    # Drop the Polygon, Counts, and Area columns
    if DelPoly == "yes":
        df = df.drop(columns=["Poly", "Polygon", "Counts", "Area"])

    # Save the dataframe to a new CSV file
    new_file_name = "I" + file
    df.to_csv(os.path.join(folder_path, new_file_name), index=False)
