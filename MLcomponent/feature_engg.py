import numpy as np

# 1️⃣ Feature Engineering

# Charging efficiency (Charging Rate per Battery Capacity)
df_cleaned["Charging_Efficiency"] = df_cleaned["Charging Rate (kW)"] / df_cleaned["Battery Capacity (kWh)"]

# Energy consumption per km driven
df_cleaned["Energy_per_km"] = df_cleaned["Energy Consumed (kWh)"] / df_cleaned["Distance Driven (since last charge) (km)"]
df_cleaned["Energy_per_km"].replace([np.inf, -np.inf], np.nan, inplace=True)  # Remove infinite values
df_cleaned["Energy_per_km"].fillna(df_cleaned["Energy_per_km"].median(), inplace=True)  # Replace NaN with median

# Cycle count per year (Capturing battery wear rate)
df_cleaned["Cycle_Count_per_Year"] = df_cleaned["Cycle_Count"] / (df_cleaned["Vehicle Age (years)"] + 0.1)  # Avoid division by zero

# Extract hour from Charging Start Time (Time-based feature)
df_cleaned["Charging_Start_Hour"] = pd.to_datetime(df["Charging Start Time"]).dt.hour

# Encode Day of Week numerically (0 = Monday, 6 = Sunday)
df_cleaned["Day_of_Week"] = pd.to_datetime(df["Charging Start Time"]).dt.dayofweek

# 2️⃣ Outlier Handling

# Clipping Temperature (C) to a reasonable range (-10 to 50)
df_cleaned["Temperature (°C)"] = np.clip(df_cleaned["Temperature (°C)"], -10, 50)

# Capping Depth of Discharge at 100%
df_cleaned["Depth_of_Discharge (%)"] = np.clip(df_cleaned["Depth_of_Discharge (%)"], 0, 100)

# 3️⃣ Feature Selection (Correlation Analysis)
corr_matrix = df_cleaned.corr()

# Selecting features that have a correlation > 0.05 with Estimated SoH (%)
correlated_features = corr_matrix["Estimated SoH (%)"].abs().sort_values(ascending=False)
selected_features = correlated_features[correlated_features > 0.05].index.tolist()

# Retain only selected features
df_final = df_cleaned[selected_features]

# Display the updated dataset
tools.display_dataframe_to_user(name="Enhanced Preprocessed EV Charging Dataset", dataframe=df_final)

# Save the final dataset for model training
final_file_path = "/mnt/data/Enhanced_Processed_EV_Charging_Dataset.csv"
df_final.to_csv(final_file_path, index=False)

final_file_path
