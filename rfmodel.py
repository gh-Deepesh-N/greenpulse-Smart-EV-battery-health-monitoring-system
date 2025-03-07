import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Load the dataset (Ensure evdatasetfinal.csv is in the same directory)
file_path = r"C:\Users\ndeep\Downloads\evdatasetfinal.csv"
df = pd.read_csv(file_path)

# Select relevant features and target variable
features = [
    "Battery Capacity (kWh)", "Charging Duration (hours)", "Charging Rate (kW)",
    "State of Charge (Start %)", "State of Charge (End %)", "Distance Driven (since last charge) (km)",
    "Temperature (°C)", "Vehicle Age (years)", "Charger Type", "User Type",
    "Cycle_Count", "Temperature_Stress_Score", "Charging_Efficiency", "Energy_per_km",
    "Cycle_Count_per_Year"
]

target = "Estimated SoH (%)"

# Splitting the data into training (80%) and testing (20%) sets
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the trained model
model_filename = "ev_battery_soh_model.pkl"
joblib.dump(rf_model, model_filename)

# Evaluate the model
y_pred = rf_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Print evaluation metrics
print(f"\n✅ Model Training Complete! Model saved as {model_filename}")
print(f"📊 Model Performance:")
print(f"   🔹 Mean Absolute Error (MAE): {mae:.5f}")
print(f"   🔹 Root Mean Squared Error (RMSE): {rmse:.5f}")
print(f"   🔹 R² Score: {r2:.5f}")

