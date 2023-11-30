# Ethan Gueck
# This code is intended to read two JSON files and merge them with the unnecessary columns dropped.
# This script has very specific use case namely converting the output from the NJUNS API script.

import json
import pandas as pd
import csv

pd.set_option('display.max_columns', None)
# In order to run this snip you must run an api post on the below NJUNS data tables:
# "ticketWallEntryBrowse-view"

file_path = r"OUTPUT_FOLDER/output_data.json"
file_path.replace("\\", "\\\\")
file_path2 = r"OUTPUT_FOLDER/output_data2.json"
file_path.replace("\\", "\\\\")

with open(file_path, 'r') as file:
    json_data = json.load(file)
df = pd.DataFrame(json_data)

with open(file_path2, 'r') as file:
    json_data2 = json.load(file)
df2 = pd.DataFrame(json_data2)

output_df = df.merge(df2, on="id", how='outer')


def extract_user_columns(row):
    user_data = row['user']
    return pd.Series(user_data)


def extract_ticket_columns(row):
    ticket_data = row['ticket']
    return pd.Series(ticket_data)


# Apply the functions to create new columns
user_columns = output_df.apply(extract_user_columns, axis=1)
ticket_columns = output_df.apply(extract_ticket_columns, axis=1)

# Concatenate the new columns with the original DataFrame
output_df = pd.concat([output_df, user_columns, ticket_columns], axis=1)
output_df = output_df.drop(['_entityName_x', '_instanceName_x', 'id', 'attachments_x', 'origin_x',
       'type_x', 'version_x', 'flagged_x', 'principalSet_x', 'createTs',
       'user', '_entityName_y', '_instanceName_y',
       'attachments_y', 'ticket', 'origin_y', 'type_y', 'version_y',
       'flagged_y', 'principalSet_y', 'comment_y', '_entityName',
       '_instanceName', 'id', 'version', '_entityName',
       '_instanceName', 'assetId', 'contactEmail', 'contactName',
       'contactPhone', 'createTs', 'createdBy', 'crossStreet', 'houseNumber',
       'id', 'latitude', 'longitude', 'miscId', 'numberOfAssets', 'option1',
       'option2', 'option3', 'principalSet', 'priority', 'referenceId',
       'remarks', 'startDate', 'status', 'street1', 'ticketNumber',
       'updatedBy', 'version', 'wfAssignedDate', 'wfTitle',
       'workRequestedDate'], axis=1)
print(output_df.head())
print(output_df.columns)
output_df.to_csv('output_json_modified.csv', index=False)
