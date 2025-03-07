import pandas as pd
import numpy as np
import os

# Directory containing the dataset files
directory_path = r'C:\Users\ndeep\Desktop\minor_sem6\ev_dataset\extracted_data\CALCE'
cleaned_data_path = r'C:/Users/ndeep/Desktop/minor_sem6/cleaned_data/CALCE_cleaned'

# Ensure the cleaned data directory exists
os.makedirs(cleaned_data_path, exist_ok=True)

# Function to clean each file
def clean_data(timeseries_path, cycle_data_path):
    timeseries_df = pd.read_csv(timeseries_path)
    cycle_data_df = pd.read_csv(cycle_data_path)

    print(f"Processing {timeseries_path} and {cycle_data_path}")
    print(f"Original time-series data shape: {timeseries_df.shape}")

    # 1. Handling Missing Values
    timeseries_df['Environment_Temperature (C)'] = timeseries_df['Environment_Temperature (C)'].fillna(timeseries_df['Environment_Temperature (C)'].mean())
    timeseries_df['Cell_Temperature (C)'] = timeseries_df['Cell_Temperature (C)'].fillna(timeseries_df['Cell_Temperature (C)'].mean())

    # For Cycle Data
    cycle_data_df.drop(['Start_Time', 'End_Time'], axis=1, inplace=True, errors='ignore')

    # 2. Data Consistency
    if 'Cycle_Index' in timeseries_df.columns and 'Cycle_Index' in cycle_data_df.columns:
        valid_cycle_indices = cycle_data_df['Cycle_Index'].dropna().unique()
        print(f"Valid cycle indices: {len(valid_cycle_indices)}")
        
        if len(valid_cycle_indices) > 0:
            timeseries_df = timeseries_df[timeseries_df['Cycle_Index'].isin(valid_cycle_indices)]
        print(f"After Cycle_Index filtering: {timeseries_df.shape}")

    # 3. Outlier Detection and Removal (Relaxed IQR from 1.5 to 3)
    for col in ['Current (A)', 'Voltage (V)', 'Cell_Temperature (C)', 'Environment_Temperature (C)']:
        if col in timeseries_df.columns:
            Q1 = timeseries_df[col].quantile(0.25)
            Q3 = timeseries_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR  # Relaxed IQR multiplier
            upper_bound = Q3 + 3 * IQR
            before_outliers = timeseries_df.shape[0]
            timeseries_df = timeseries_df[(timeseries_df[col] >= lower_bound) & (timeseries_df[col] <= upper_bound)]
            after_outliers = timeseries_df.shape[0]
            print(f"Outlier removal for {col}: {before_outliers - after_outliers} rows removed")

    # 4. Feature Engineering
    if 'Current (A)' in timeseries_df.columns and 'Voltage (V)' in timeseries_df.columns:
        timeseries_df['Average_Power (W)'] = timeseries_df['Current (A)'] * timeseries_df['Voltage (V)']

    if 'Cell_Temperature (C)' in timeseries_df.columns and 'Environment_Temperature (C)' in timeseries_df.columns:
        timeseries_df['Temperature_Gradient (C)'] = timeseries_df['Cell_Temperature (C)'] - timeseries_df['Environment_Temperature (C)']

    # Save cleaned data
    timeseries_cleaned_path = os.path.join(cleaned_data_path, os.path.basename(timeseries_path).replace('.csv', '_cleaned.csv'))
    cycle_cleaned_path = os.path.join(cleaned_data_path, os.path.basename(cycle_data_path).replace('.csv', '_cleaned.csv'))

    if not timeseries_df.empty:
        timeseries_df.to_csv(timeseries_cleaned_path, index=False)
        print(f"Saved cleaned time-series: {timeseries_cleaned_path}")
    else:
        print(f"Warning: Cleaned time-series data is empty for {timeseries_path}")

    if not cycle_data_df.empty:
        cycle_data_df.to_csv(cycle_cleaned_path, index=False)
        print(f"Saved cleaned cycle data: {cycle_cleaned_path}")
    else:
        print(f"Warning: Cleaned cycle data is empty for {cycle_data_path}")

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
