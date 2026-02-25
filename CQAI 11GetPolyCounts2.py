"""Once you run PolygonLasso on the data to produce the files starting with "Poly", this will
take all the CSV files starting with the name "Poly" and isolate the summarized counts
for every polygon and save it as a different file name "COUNTS.cvs"

Do not use if you deleted outside ("OPoly" files).

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

saver = os.path.join(locat,"PolyCounts.csv")
sum = 0
add = 0
files = os.listdir(locat)

df1 = [] #raw counts
df2 = [] #just polygon column
df3 = [] #Output to CSV

#df3 = pd.DataFrame(columns = ['Name', 'Age'])
df3 = pd.DataFrame()

df3["Polygon"] = pd.NaT
df3["Counts"] = pd.NaT
df3["Area"] = pd.NaT
df3["File"] = pd.NaT

#print(df3)


for csvs in files:
    #print(csvs)
    csvs1 = os.path.join(locat,csvs)
    if not csvs.endswith(".csv"):
        continue
    if not csvs.startswith(("Poly", "OPoly")): #add , "KN" to get files without Poly
        continue
    elif csvs.startswith("._"):  # mac files have these meta data files
        continue
    elif os.path.isdir(csvs1):
        # skip directories
        continue
    else:
        TotIn = 0
        TotArea = 0
        df1 = pd.read_csv(csvs1) #raw data
        SHAP = (df1.shape)
        r1 = SHAP[0]  # rows
        r = r1 - 1
        print('hi')
        df2 = df1[['Polygon']].copy()
        sum = df2['Polygon'].count() #The total number of unique polygons

        print(sum)

        for y in range(0, sum-1):
            Count1 = int(df1.loc[y, 'Counts'])
            Area1 = int(df1.loc[y, 'Area'])
            print(Count1)
            TotIn = TotIn + Count1
            TotArea = TotArea + Area1

        for x in range(0, sum):  # (0,r) for x in range(0,5350):
            p = (df1.loc[x, 'Polygon'])
            df3.loc[x+add, 'Polygon'] = p
            df3.loc[x+add, 'Counts'] = (df1.loc[x, 'Counts'])
            df3.loc[x+add, 'Area'] = (df1.loc[x, 'Area'])
            #df3.loc[x+add, 'File'] = csvs1
            df3.loc[x + add, 'File'] = os.path.basename(csvs1)
            #counts = (df1.loc[x, 'Counts'])
            #area = (df1.loc[x, 'Area'])
            print(df3)

        df3.loc[x + add+1, 'Polygon'] = 'Tot Inside'
        df3.loc[x + add+1, 'Counts'] = TotIn
        df3.loc[x + add + 1, 'Area'] = TotArea
        #df3.loc[x + add+1, 'File'] = csvs1
        df3.loc[x + add + 1, 'File'] = os.path.basename(csvs1)
        add = add + sum + 1


        print(TotIn)



df3.to_csv(saver, index=False)

print('This formula will extract the file name in excel (in cell E2):')
print('Note: slash (/) marks may be forward or backward depending on')
print('the computer it was generated on.')
print('Mac')
print('=MID(E2, FIND(CHAR(1), SUBSTITUTE(E2, "/", CHAR(1), LEN(E2)-LEN(SUBSTITUTE(E2, "/", ""))))+1, LEN(E2))')
print ('')
print('PC')
print('=MID(E2, FIND(CHAR(1), SUBSTITUTE(E2, "\\", CHAR(1), LEN(E2)-LEN(SUBSTITUTE(E2, "\\", ""))))+1, LEN(E2))')
print ('')
print ('To get litter number before dash')
print ('=TRIM(RIGHT(LEFT(D2,FIND("-",D2)-1),2))')
print ('')
print ('To get animal number after dash')
print ('=TRIM(LEFT(MID(D2,FIND("-",D2)+1,2),2))')
