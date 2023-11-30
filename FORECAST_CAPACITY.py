# Ethan Gueck
# This code is intended to process an Excel document containing due dates and prescribe when completion will be based on
# owner capacity.

import datetime
import pandas as pd
import openpyxl
from openpyxl import pivot
pd.options.display.max_rows = None
class constraint_forecasting:
    def __init__(self):
        pass
    def get_reports(self):
        # Read the data into a pandas dataframe
        self.df = pd.read_csv("REDACTED")
        self.df_priority = pd.read_excel("REDACTED")
        # EXAMPLE DF
        '''
        OWNER PART      POLES DATE               AREA
        OTHER VA-       61    645104.1722222222  VA- 
        OTHER VA-       61    645104.1722222222  VA- 
        '''
    def assign_capacity(self):
        # Assign capacity
        self.distinct_owner = self.df['OWNER'].unique()
        self.pole_owner_capacity = {'OTHER' : 800, 'REDACTED' : 847,  'REDACTED' : 1195, 'REDACTED' : 1000, 'REDACTED' : 300}
        for i in self.distinct_owner:
            if i not in [key.split()[0] for key in self.pole_owner_capacity.keys()]:
                self.pole_owner_capacity[i] = 800
    def assign_priorities(self):
        df = self.df
        # Assign priorities
        self.area_priority = {area: priority for area, priority in zip(self.df_priority['COUNTY_NOMEN'], self.df_priority['PRIORITY'])}
        self.area_priority['VA- '] = 999
        print(self.area_priority)
        df['PRIORITY'] = df['AREA'].map(self.area_priority)
    def convert_to_mo(self):
        # Step 1: Convert all days in DATE to the 1st of the month
        df = self.df
        df['DATE'] = pd.to_datetime(df['DATE']).dt.to_period('M').dt.to_timestamp()

        # Loop until no months exceed the constraint
        while True:
            # Step 2: Calculate the sum of POLES by OWNER for each month
            sums = df.groupby(['OWNER', 'DATE'])['POLES'].sum().reset_index()

            # Step 3: Compare the sum for each pole owner with the constraint of 25 poles per month
            exceeded = sums.merge(pd.DataFrame(self.pole_owner_capacity.items(), columns=['OWNER', 'CAPACITY']), on='OWNER')
            exceeded = exceeded[exceeded['POLES'] > exceeded['CAPACITY']]
            # Step 4: Change the date for areas that exceeded the constraint
            if exceeded.empty:
                # No areas exceeded the constraint, exit the loop
                break
            else:
                for _, row in exceeded.iterrows():
                    owner = row['OWNER']
                    date = row['DATE']
                    owner_df = df[(df['OWNER'] == owner) & (df['DATE'] == date)]
                    if not owner_df.empty:
                        owner_df = owner_df.sort_values('PRIORITY', ascending=False)
                        highest_priority_row = owner_df.iloc[0]
                        #print(highest_priority_row)
                        #print(area_priority[highest_priority_row['AREA']])
                        df.loc[highest_priority_row.name, 'DATE'] += pd.offsets.MonthBegin(1)
    def write_df(self):
        df = self.df.sort_values("DATE")

        # Output the final dataframe
        # print(df)

        # Create a new Excel workbook and worksheet
        writer = pd.ExcelWriter('OUTPUT_DOCS/CONSTRAINT_FORECAST.xlsx', engine='openpyxl')
        df.to_excel(writer, sheet_name='CONSTRAINT_FORECAST')

        # Save the workbook
        writer.save()
cf = constraint_forecasting()
cf.get_reports()
cf.assign_capacity()
cf.assign_priorities()
cf.convert_to_mo()
cf.write_df()