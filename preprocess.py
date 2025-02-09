# 1️⃣ Handling Missing Values
df_processed = df_raw.dropna()  # Dropping rows with missing values

# 2️⃣ Removing Unrealistic Values
df_processed = df_processed[(df_processed["State of Charge (Start %)"] <= 100) & 
                            (df_processed["State of Charge (End %)"] <= 100)]

# 3️⃣ Feature Engineering

# Charging efficiency (Charging Rate per Battery Capacity)
df_processed["Charging_Efficiency"] = df_processed["Charging Rate (kW)"] / df_processed["Battery Capacity (kWh)"]

# Energy consumption per km driven
df_processed["Energy_per_km"] = df_processed["Energy Consumed (kWh)"] / df_processed["Distance Driven (since last charge) (km)"]
df_processed["Energy_per_km"].replace([np.inf, -np.inf], np.nan, inplace=True)  # Remove infinite values
df_processed["Energy_per_km"].fillna(df_processed["Energy_per_km"].median(), inplace=True)  # Replace NaN with median

# Cycle count per year (Capturing battery wear rate)
df_processed["Cycle_Count_per_Year"] = df_processed["Cycle_Count"] / (df_processed["Vehicle Age (years)"] + 0.1)  # Avoid division by zero

# Extract hour from Charging Start Time (Time-based feature)
df_processed["Charging_Start_Hour"] = pd.to_datetime(df_raw["Charging Start Time"]).dt.hour

# Encode Day of Week numerically (0 = Monday, 6 = Sunday)
df_processed["Day_of_Week"] = pd.to_datetime(df_raw["Charging Start Time"]).dt.dayofweek

# 4️⃣ Outlier Handling

# Clipping Temperature (C) to a reasonable range (-10 to 50)
df_processed["Temperature (°C)"] = np.clip(df_processed["Temperature (°C)"], -10, 50)

# Capping Depth of Discharge at 100%
df_processed["Depth_of_Discharge (%)"] = np.clip(df_processed["Depth_of_Discharge (%)"], 0, 100)

# 5️⃣ Encoding Categorical Variables

from sklearn.preprocessing import LabelEncoder

cat_cols = ["Vehicle Model", "Charging Station Location", "Charger Type", "User Type"]
encoder = LabelEncoder()

for col in cat_cols:
    df_processed[col] = encoder.fit_transform(df_processed[col])

# 6️⃣ Scaling Numerical Features

num_cols = df_processed.select_dtypes(include=['float64']).columns
scaler = MinMaxScaler()

df_processed[num_cols] = scaler.fit_transform(df_processed[num_cols])

# Display the updated dataset
tools.display_dataframe_to_user(name="Final Preprocessed EV Charging Dataset", dataframe=df_processed)

# Save the final processed dataset
final_processed_path = "/mnt/data/Final_Processed_EV_Charging_Dataset.csv"
df_processed.to_csv(final_processed_path, index=False)

final_processed_path
