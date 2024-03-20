import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os


def modify_csv(input_path, output_path):
    # Load CSV with specified delimiter
    dataframe = pd.read_csv(input_path, delimiter=';', encoding='utf-8')

    # Add an empty row at the dataframe's end
    empty_row = pd.DataFrame([pd.NA] * dataframe.shape[1]).T
    empty_row.iloc[:, 25] = pd.NA  # Ensure column Z remains empty
    dataframe = pd.concat([dataframe, empty_row])

    # Indices for columns to calculate averages, excluding Z
    columns_before_Z_indices = list(range(2, 25))  # C to Y
    columns_after_Z_indices = list(range(26, 43))  # AA to AQ
    calculation_indices = columns_before_Z_indices + columns_after_Z_indices

    # Calculate and append averages for specified columns
    averages = {dataframe.columns[i]: round(dataframe.iloc[:-1, i].mean(), 3) for i in calculation_indices}
    averages[dataframe.columns[25]] = pd.NA  # Exclude column Z from averaging

    # Append averages row to dataframe
    averages_row = pd.DataFrame(averages, index=[0])
    dataframe = pd.concat([dataframe, averages_row], ignore_index=True)

    # Save modified dataframe to CSV
    dataframe.to_csv(output_path, index=False, sep=';', encoding='utf-8')


def select_input_file_and_modify():
    # Initialize Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Define the initial directory path relative to the script location or an absolute path
    # For a relative path, assuming 'output' folder is in the same directory as the script:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the script is located
    output_dir_path = os.path.join(script_dir, "output")  # Path to the 'output' directory

    # Open file dialog to select the input CSV file, starting in the 'output' folder
    input_file_path = filedialog.askopenfilename(
        title="Select CSV file",
        initialdir=output_dir_path,  # Set the initial directory to the 'output' folder
        filetypes=[("CSV files", "*.csv")]
    )
    if not input_file_path:  # No file was selected
        return

    # Generate output file path by appending '_modified' before '.csv'
    output_file_path = input_file_path.rsplit('.', 1)[0] + '_modified.csv'

    # Process the CSV file
    modify_csv(input_file_path, output_file_path)
    print(f"File processed and saved as {output_file_path}")


if __name__ == "__main__":
    select_input_file_and_modify()
