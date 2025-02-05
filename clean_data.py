import pandas as pd
import numpy as np
import os

# Directory containing the dataset files
directory_path = 'C:\Users\ndeep\Desktop\minor_sem6\ev_dataset\extracted_data\CALCE'

# Function to clean each file
def clean_data(timeseries_path, cycle_data_path):
    timeseries_df = pd.read_csv(timeseries_path)
    cycle_data_df = pd.read_csv(cycle_data_path)

    # 1. Handling Missing Values
    timeseries_df['Environment_Temperature (C)'].fillna(timeseries_df['Environment_Temperature (C)'].mean(), inplace=True)
    timeseries_df['Cell_Temperature (C)'].fillna(timeseries_df['Cell_Temperature (C)'].mean(), inplace=True)

    # For Cycle Data
    cycle_data_df.drop(['Start_Time', 'End_Time'], axis=1, inplace=True, errors='ignore')

    # 2. Data Consistency
    valid_cycle_indices = cycle_data_df['Cycle_Index'].dropna().unique()
    timeseries_df = timeseries_df[timeseries_df['Cycle_Index'].isin(valid_cycle_indices)]

    # 3. Outlier Detection and Removal
    for col in ['Current (A)', 'Voltage (V)', 'Cell_Temperature (C)', 'Environment_Temperature (C)']:
        if col in timeseries_df.columns:
            Q1 = timeseries_df[col].quantile(0.25)
            Q3 = timeseries_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            timeseries_df = timeseries_df[(timeseries_df[col] >= lower_bound) & (timeseries_df[col] <= upper_bound)]

    # 4. Feature Engineering
    if 'Current (A)' in timeseries_df.columns and 'Voltage (V)' in timeseries_df.columns:
        timeseries_df['Average_Power (W)'] = timeseries_df['Current (A)'] * timeseries_df['Voltage (V)']

    if 'Cell_Temperature (C)' in timeseries_df.columns and 'Environment_Temperature (C)' in timeseries_df.columns:
        timeseries_df['Temperature_Gradient (C)'] = timeseries_df['Cell_Temperature (C)'] - timeseries_df['Environment_Temperature (C)']

    # Save cleaned data
    timeseries_cleaned_path = timeseries_path.replace('.csv', '_cleaned.csv')
    cycle_cleaned_path = cycle_data_path.replace('.csv', '_cleaned.csv')

    timeseries_df.to_csv(timeseries_cleaned_path, index=False)
    cycle_data_df.to_csv(cycle_cleaned_path, index=False)

    print(f"Cleaned files saved as '{timeseries_cleaned_path}' and '{cycle_cleaned_path}'")

# Automate the process for all files in the directory
for root, dirs, files in os.walk(directory_path):
    timeseries_files = [f for f in files if 'timeseries' in f and f.endswith('.csv')]
    cycle_files = [f for f in files if 'cycle_data' in f and f.endswith('.csv')]

    for ts_file in timeseries_files:
        corresponding_cycle_file = ts_file.replace('timeseries', 'cycle_data')
        
        if corresponding_cycle_file in cycle_files:
            ts_path = os.path.join(root, ts_file)
            cycle_path = os.path.join(root, corresponding_cycle_file)
            
            clean_data(ts_path, cycle_path)

print("Data cleaning complete for all files in the directory.")
