"""This will take all the CSV files after CombineCVSPlusMultiSize.py had combined them
and just count the number of rows in each file.  This is typically the total number
of cell counted in the object

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""

import os
import pandas as pd
import easygui

direct = easygui.diropenbox('Where are the files?')
locat = os.path.join(direct)
print(locat)

saver = os.path.join(locat, "COUNTS.csv")

files = os.listdir(locat)

COUNTS = []

for csvs in files:
    print(csvs)
    csvs1 = os.path.join(locat, csvs)
    if not csvs.endswith(".csv"):
        continue
    elif csvs.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(csvs1):
        # skip directories
        continue
    else:
        df = pd.read_csv(csvs1)

        SHAP = (df.shape)
        r1 = SHAP[0]  # rows
        r = r1

        COUNTS.append([csvs, "All", r])

        class_counts = df['Class'].value_counts()
        for index, value in class_counts.items():
            COUNTS.append([csvs, index, value])

Countdf = pd.DataFrame(COUNTS, columns=['File', 'Object', 'Counts'])

Countdf.to_csv(saver, index=False)
