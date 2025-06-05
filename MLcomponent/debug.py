import joblib
import pandas as pd
import numpy as np

# Load the trained model
model_path = "ev_battery_soh_model.pkl"  # Ensure this file is in the same directory
model = joblib.load(model_path)

# Expected feature names (Ensure these match exactly)
feature_names = [
    "Battery Capacity (kWh)", "Charging Duration (hours)", "Charging Rate (kW)",
    "State of Charge Start (%)", "State of Charge End (%)", "Distance Driven (since last charge) (km)",
    "Temperature (°C)", "Vehicle Age (years)", "Charger Type", "User Type",
    "Cycle_Count", "Temperature_Stress_Score", "Charging_Efficiency", "Energy_per_km",
    "Cycle_Count_per_Year"
]

# Define new test input with correct feature order
test_input = {
    "Battery Capacity (kWh)": 0.558460,
    "Charging Duration (hours)": 0.074284,
    "Charging Rate (kW)": 11.0,
    "State of Charge Start (%)": 35.0,
    "State of Charge End (%)": 85.0,
    "Distance Driven (since last charge) (km)": 120.0,
    "Temperature (°C)": 25.0,
    "Vehicle Age (years)": 3.0,
    "Charger Type": 1,  # Fast Charger = 1, Normal Charger = 0
    "User Type": 2,  # Regular = 0, Occasional = 1, Heavy User = 2
    "Cycle_Count": 500,  # Estimated
    "Temperature_Stress_Score": 0.75,  # Estimated
    "Charging_Efficiency": 0.92,  # Estimated
    "Energy_per_km": 0.2148,  # Estimated
    "Cycle_Count_per_Year": 166.67  # Estimated
}

# Convert to DataFrame (Ensures correct feature names)
test_df = pd.DataFrame([test_input])

# Ensure all columns exist and types are correct
test_df = test_df.astype(float)  # Convert all to float

# Debugging: Print the final test input before prediction
print("\n✅ Debug: Final Model Input Features\n")
print(test_df)

# Check if all expected features exist
missing_features = [col for col in feature_names if col not in test_df.columns]
if missing_features:
    print(f"\n🚨 Missing Features: {missing_features}")
    exit()

# Make prediction
predicted_soh = model.predict(test_df)[0]

# Display result
print(f"\n🔋 Predicted Battery State of Health (SoH%): {predicted_soh:.2f}%\n")

# Provide Interpretation
if predicted_soh >= 80:
    print("✅ Battery is in great shape! (Green)")
elif 50 <= predicted_soh < 80:
    print("🟡 Moderate battery health. Consider improving charging habits.")
else:
    print("🔴 High degradation detected. Battery replacement may be needed.")
