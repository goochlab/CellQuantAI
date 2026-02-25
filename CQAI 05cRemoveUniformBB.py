"""
The CSV and TIF UL images need to be in the same folder for this to
work.  This will look at how uniform the pixels are in the bounding
boxes and remove the rows where the pixel intensity extremes are
below a threshold.  Added is Right-Left or Bottom-Top is below 1
this row is skipped

© 2023 Washington University in St. Louis
Non-commercial research use only.
See LICENSE.txt for full terms.
https://github.com/goochlab/CellQuantAI/blob/main/LICENSE.txt
"""
import os
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from PIL import Image

# Open a window to select a folder
root = Tk()
root.withdraw()  # Hide the main window
folder_selected = filedialog.askdirectory()

THRESH = 50 #usually 150
COLUMN = "yes"

# List all CSV and TIF files in the selected folder
csv_files = [f for f in os.listdir(folder_selected) if f.endswith('.csv')]
tif_files = [f for f in os.listdir(folder_selected) if f.endswith('.tif')]

# If no TIF files are found, print message and stop
if len(tif_files) == 0:
    print("Please place CSV files in same folder as TIF images")
    raise SystemExit

for csv_file in csv_files:
    print(csv_file)
    # Find the matching TIF file
    csv_base = os.path.splitext(csv_file)[0]
    matches = {tif: os.path.commonprefix([csv_base, os.path.splitext(tif)[0]]) for tif in tif_files}
    tif_file = max(matches, key=matches.get)

    # Open the TIF file with PIL
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(os.path.join(folder_selected, tif_file)) as img:
        # Load the CSV file as a pandas dataframe
        df = pd.read_csv(os.path.join(folder_selected, csv_file))

        # Find the column title that starts with "GRD"
        #The Guard means we need to subtract FGuard from the
        for col_title in df.columns:
            if col_title.startswith("GRD"):
                FilDat = col_title
                break
            else:
                FilDat = "GRD0X0Y0"

        # Split the column title into parts
        parts = FilDat.split("X")
        FGuard = int(parts[0].replace("GRD", ""))
        parts = parts[1].split("Y")
        FWidth = int(parts[0])
        FHeight = int(parts[1])

        # Create a mask for rows where 'Top' and 'Bottom' or 'Left' and 'Right' are the same
        mask = (df['Top'] != df['Bottom']) & (df['Left'] != df['Right'])
        df = df[mask]

        # Initialize an empty list to store indices to drop
        indices_to_drop = []

        # Iterate over the dataframe rows
        for index, row in df.iterrows():
            left, top, right, bottom = row['Left'], row['Top'], row['Right'], row['Bottom']

            # Skip rows where width or height is 1 or below
            if (right - left) <= 1 or (bottom - top) <= 1:
                print(f"Skipping row {index} due to small bounding box: Width={right - left}, Height={bottom - top}")
                continue

            cropped_img = img.crop((left-FGuard, top-FGuard, right-FGuard, bottom-FGuard)).convert('L')  # Convert to grayscale

            # Calculate the 5th and 95th percentiles of pixel intensities
            pixel_values = list(cropped_img.getdata())
            pixel_values.sort()
            num_pixels = len(pixel_values)
            fifth_percentile = pixel_values[int(0.05 * num_pixels)]
            ninety_fifth_percentile = pixel_values[int(0.95 * num_pixels)]

            # Check if the difference is below the threshold
            if (ninety_fifth_percentile - fifth_percentile) < THRESH:
                indices_to_drop.append(index)
                print(index)

            # Add the new column if COLUMN is "yes"
            if COLUMN == "yes":
                df.loc[index, 'percentile_difference'] = ninety_fifth_percentile - fifth_percentile

        # Drop the rows with indices collected
        df.drop(indices_to_drop, inplace=True)

        # Renumber the "Object" column
        df['Object'] = range(1, len(df) + 1)

        # Save the modified dataframe to a new CSV file
        NAM = "NoUni" + str(THRESH) + ".csv"
        new_csv_file = os.path.splitext(csv_file)[0] + NAM
        df.to_csv(os.path.join(folder_selected, new_csv_file), index=False)
