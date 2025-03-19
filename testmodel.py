import joblib
import pandas as pd

# Load the trained model
model_path = "ev_battery_soh_model.pkl"  # Ensure this file is in the same directory
model = joblib.load(model_path)

# Normalization factors (from training dataset)
normalization_factors = {
    "Battery Capacity (kWh)": 100,
    "Charging Duration (hours)": 12,
    "Charging Rate (kW)": 250,
    "State of Charge (Start %)": 100,  # ✅ Updated Feature Name
    "State of Charge (End %)": 100,  # ✅ Updated Feature Name
    "Distance Driven (since last charge) (km)": 800,
    "Temperature (°C)": 50,
    "Vehicle Age (years)": 20,
    "Cycle_Count": 3000,
    "Temperature_Stress_Score": 10,
    "Charging_Efficiency": 1,
    "Energy_per_km": 0.3,
    "Cycle_Count_per_Year": 300,

    
}

# Function to compute derived inputs
def compute_derived_inputs(user_input):
    return {
        "Cycle_Count": (user_input["Vehicle Age (years)"] * 250) + (user_input["User Type"] * 50),
        "Temperature_Stress_Score": max(0, (user_input["Temperature (°C)"] - 25) * 0.05),
        "Charging_Efficiency": 0.95 - (user_input["Charging Rate (kW)"] * 0.001),
        "Energy_per_km": user_input["Distance Driven (since last charge) (km)"] / user_input["Battery Capacity (kWh)"],
        "Cycle_Count_per_Year": (user_input["Vehicle Age (years)"] * 250) / user_input["Vehicle Age (years)"] if user_input["Vehicle Age (years)"] > 0 else 0
    }

# User-friendly test case (Updated Feature Names)
test_case = {
    "Battery Capacity (kWh)": 50,
    "Charging Duration (hours)": 2.0,
    "Charging Rate (kW)": 40,
    "State of Charge (Start %)": 30,
    "State of Charge (End %)": 70,
    "Distance Driven (since last charge) (km)": 200,
    "Temperature (°C)": 50,
    "Vehicle Age (years)": 5,
    "Charger Type": 1,
    "User Type": 1,
}

# Compute derived inputs and merge with user inputs
derived_inputs = compute_derived_inputs(test_case)
full_input = {**test_case, **derived_inputs}

# Normalize inputs before feeding into the model
normalized_input = {
    key: (value / normalization_factors[key]) if key in normalization_factors else value
    for key, value in full_input.items()
}

# Convert to DataFrame
test_df = pd.DataFrame([normalized_input])

# Debugging Step: Print Expected vs Actual Features
print("🔍 Expected Model Feature Names:", model.feature_names_in_)
print("🔍 Test Data Feature Names:", list(test_df.columns))

# Ensure Feature Names Match
test_df = test_df[model.feature_names_in_]

# Make prediction
predicted_soh_normalized = model.predict(test_df)[0]

# Convert back to percentage scale
predicted_soh = predicted_soh_normalized * 100

# Display result
print(f"\n🔋 Predicted Battery State of Health (SoH%): {predicted_soh:.2f}%\n")
if predicted_soh >= 80:
    print("✅ Battery is in great shape! (Green)")
elif 50 <= predicted_soh < 80:
    print("🟡 Moderate battery health. Consider improving charging habits.")
else:
    print("🔴 High degradation detected. Battery replacement may be needed.")
