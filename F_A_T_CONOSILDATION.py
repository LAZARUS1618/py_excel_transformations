# Ethan Gueck
# Fiber Assignment Tool App
# This application is intended to consolidate a folder of excel files and the sheets within them into one data source.

import os
import pandas as pd
import datetime
# Iterate through directories and subdirectories
def find_excel_files(start_dir):
    excel_files = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.xlsx'):
                excel_files.append(os.path.join(root, file))
    return excel_files

# Combine all sheets from multiple Excel files into a single DataFrame
def combine_excel_sheets(excel_files):
    combined_df = pd.DataFrame()
    for file in excel_files:
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            sheet_df = xls.parse(sheet_name)
            combined_df = pd.concat([combined_df, sheet_df], ignore_index=True)
            combined_df.iloc[:, 0:4] = combined_df.iloc[:, 0:4].fillna(method='ffill')
    return combined_df


# Write the combined DataFrame to a CSV file
def write_to_csv(dataframe, output_csv):
    dataframe.to_csv(output_csv, index=False)

# Specify the directory where you want to start searching for Excel files
start_directory = '' # SELECT DIRECTORY
start_directory.replace("\\", "\\\\")
excel_files = find_excel_files(start_directory)
combined_data = combine_excel_sheets(excel_files)
now = datetime.datetime.now()
timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')
output_csv = f'combined_data_{timestamp}.csv'
write_to_csv(combined_data, output_csv)
print(f'Combined data has been written to {output_csv}')




