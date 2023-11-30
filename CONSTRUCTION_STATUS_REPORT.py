# Ethan Gueck
# This app is intended to consolidate a zipped folder of Excel documents into a single CSV.

import os
import zipfile
import pandas as pd
import shutil
import datetime
import warnings
import re

pd.options.display.max_rows = None
pd.options.display.max_columns = None
warnings.filterwarnings("ignore", category=FutureWarning)


def get_latest_file(folder_path):
    files = os.listdir(folder_path)
    files = [f for f in files if f.endswith(('.xlsx', '.xls', '.csv'))]

    if not files:
        return None

    date_patterns = [
        r'\d{1,2}\.\d{1,2}\.\d{4}',    # D.M.YYYY
        r'\d{1,2}_\d{1,2}_\d{4}',      # D_M_YYYY
        r'\d{1,2}\.\d{1,2}\.\d{2}',     # D.M.YY
        r'\d{1,2}_\d{1,2}_\d{2}'        # D_M_YY
    ]

    latest_file = None
    latest_date = None

    for file in files:
        file_name, file_ext = os.path.splitext(file)
        for pattern in date_patterns:
            match = re.search(pattern, file_name)
            if match:
                date_str = match.group()
                try:
                    if len(date_str) == 8:
                        date = datetime.datetime.strptime(date_str, '%d.%m.%Y').date()
                    elif len(date_str) == 10:
                        date = datetime.datetime.strptime(date_str, '%d_%m_%Y').date()
                    elif len(date_str) == 6:
                        date = datetime.datetime.strptime(date_str, '%d.%m.%y').date()
                    elif len(date_str) == 8:
                        date = datetime.datetime.strptime(date_str, '%d_%m_%y').date()
                    else:
                        continue

                    if latest_date is None or date > latest_date:
                        latest_date = date
                        latest_file = file

                except ValueError:
                    continue

    if latest_file:
        return os.path.join(folder_path, latest_file)
    else:
        return None


def extract_zip_file(zip_path):
    # Extract the zip file to a temporary folder
    temp_folder = "temp"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_folder)

    master_df = pd.DataFrame()

    # Iterate through the files and subfolders
    for root, dirs, files in os.walk(temp_folder):
        for folder in dirs:
            if folder.lower() in ["weekly production", "weekly updates"]:
                wp_folder = os.path.join(root, folder)
                for wp_root, wp_dirs, wp_files in os.walk(wp_folder):
                    latest_file_path = get_latest_file(wp_root)
                    if latest_file_path:
                        df = pd.read_excel(latest_file_path, header=1) if latest_file_path.endswith(
                            ('.xlsx', '.xls')) else pd.read_csv(latest_file_path, header=1)
                        df = df.iloc[:, :23]  # Exclude the first row of each file
                        df = df.dropna(how='all')  # Remove rows with all NaN values
                        master_df = master_df.append(df, ignore_index=True)

    # Remove the temporary folder and its contents
    shutil.rmtree(temp_folder)
    return master_df

def main():
    zip_path = r"PATH.zip" # Input zip path
    zip_path = zip_path.replace("\\", "\\\\")

    master_df = extract_zip_file(zip_path)

    today = datetime.datetime.today().strftime("%Y-%m-%d")
    path_name = f'OUTPUT_DOCS/CONSTRUCTION_REPORT_{today}.csv'
    master_df.to_csv(path_name, index=False)

    print(master_df.columns)
    print(master_df.info())
    print(master_df.describe())
main()

