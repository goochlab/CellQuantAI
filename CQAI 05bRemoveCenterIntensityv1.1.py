"""
The CSV and TIF UL images need to be in the same folder for this to
work.  This will look at how uniform the pixels are in the bounding
boxes by comparing the average pixel intensity in the center of the
bounding box verses the edges.  It will then keep rows that have
bounding boxes have a center with lower intensity (darker).

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
import numpy as np

# Open a window to select a folder
root = Tk()
root.withdraw()  # Hide the main window
folder_selected = filedialog.askdirectory()

THRESH = 1
COLUMN = "yes"
# List all CSV and TIF files in the selected folder
csv_files = [f for f in os.listdir(folder_selected) if f.endswith('.csv')]
tif_files = [f for f in os.listdir(folder_selected) if f.endswith('.tif')]

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
        FilDat = next((col for col in df.columns if col.startswith("GRD")), "GRD0X0Y0")

        # Split the column title into parts
        parts = FilDat.split("X")
        FGuard = int(parts[0].replace("GRD", ""))
        parts = parts[1].split("Y")
        FWidth = int(parts[0])
        FHeight = int(parts[1])

        # Create a mask for rows where 'Top' and 'Bottom' or 'Left' and 'Right' are the same
        mask = (df['Top'] != df['Bottom']) & (df['Left'] != df['Right'])
        df = df[mask].copy()  # Make a copy to avoid modifying the original dataframe

        # Initialize an empty list to store indices to drop
        indices_to_drop = []

        # Initialize a list to store crop coordinates, object names, and intensity differences
        crop_data = []

        # Iterate over the dataframe rows
        for index, row in df.iterrows():
            left, top, right, bottom = row['Left'], row['Top'], row['Right'], row['Bottom']

            # Skip rows where width or height is 1 or below
            if (right - left) <= 1 or (bottom - top) <= 1:
                print(f"Skipping row {index} due to small bounding box: Width={right - left}, Height={bottom - top}")
                continue

            # Check if any coordinate is NaN and skip the row if so
            if any(np.isnan([left, top, right, bottom])):
                print(f"Row {index}: One or more coordinates are NaN, skipping this row.")
                continue  # Skip this row if NaN is found

            # Crop the image using valid coordinates
            cropped_img = img.crop((left - FGuard, top - FGuard, right - FGuard, bottom - FGuard)).convert(
                'L')  # Convert to grayscale

            # Get pixel values
            pixel_values = list(cropped_img.getdata())
            width, height = cropped_img.size

            # Calculate pixel indices for outer rectangles
            outer_x_start = int(0.15 * width)
            outer_x_end = int(0.85 * width)
            outer_y_start = int(0.15 * height)
            outer_y_end = int(0.85 * height)

            outer_rect1_indices = [(x, y * width) for x in range(0, outer_x_start + 1) for y in range(0, height)] + \
                                  [(x, y * width) for x in range(outer_x_end, width) for y in range(0, height)]
            outer_rect2_indices = [(x, y * width) for x in range(outer_x_start, outer_x_end + 1) for y in
                                   range(0, outer_y_start + 1)] + \
                                  [(x, y * width) for x in range(outer_x_start, outer_x_end + 1) for y in
                                   range(outer_y_end, height)]

            # Calculate average intensity of outer rectangles
            avg_outer_intensity = (sum(pixel_values[x + y] for x, y in outer_rect1_indices) +
                                   sum(pixel_values[x + y] for x, y in outer_rect2_indices)) / (
                                          len(outer_rect1_indices) + len(outer_rect2_indices))

            # Calculate indices for inner rectangle
            inner_rect_indices = [(x, y * width) for x in range(outer_x_start, outer_x_end + 1) for y in
                                  range(outer_y_start, outer_y_end + 1)]

            # Calculate average intensity of inner rectangle
            avg_inner_intensity = sum(pixel_values[x + y] for x, y in inner_rect_indices) / len(inner_rect_indices)

            # Calculate difference
            intensity_difference = avg_outer_intensity - avg_inner_intensity

            # Store crop coordinates, object name, and intensity difference
            crop_data.append((left, top, right, bottom, row['Object'], intensity_difference))

            # Compare with threshold and mark for dropping if needed
            if intensity_difference < THRESH:
                indices_to_drop.append(index)
                print(f"Row {index}: Intensity difference {intensity_difference} is less than threshold.")

        # Drop the rows with indices collected
        df.drop(indices_to_drop, inplace=True)

        # Reset index to avoid misalignment
        df.reset_index(drop=True, inplace=True)

        # Renumber the "Object" column
        df['Object'] = range(1, len(df) + 1)

        # Add "Difference" column to the original dataframe
        if COLUMN == "yes":
            filtered_crop_data = [data for i, data in enumerate(crop_data) if i not in indices_to_drop]
            df['Difference'] = pd.Series([data[5] for data in filtered_crop_data], dtype='float64')

        # Check for rows where Left, Right, Top, or Bottom have missing data and clear Object for those rows
        invalid_rows = df[['Left', 'Right', 'Top', 'Bottom']].isnull().any(axis=1)
        df.loc[invalid_rows, 'Object'] = None

        # Save the modified dataframe to a new CSV file
        new_csv_file = os.path.splitext(csv_file)[0] + 'NoCen.csv'
        df.to_csv(os.path.join(folder_selected, new_csv_file), index=False)

print("Processing complete.")
