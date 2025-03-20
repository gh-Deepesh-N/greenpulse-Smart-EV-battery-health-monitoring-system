from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load("ev_battery_soh_model.pkl")

# Function to compute derived inputs
def compute_derived_inputs(user_input):
    return {
        "Cycle_Count": (user_input["Vehicle Age (years)"] * 250) + (user_input["User Type"] * 50),
        "Temperature_Stress_Score": max(0, (user_input["Temperature (°C)"] - 25) * 0.05),
        "Charging_Efficiency": 0.95 - (user_input["Charging Rate (kW)"] * 0.001),
        "Energy_per_km": user_input["Distance Driven (since last charge) (km)"] / user_input["Battery Capacity (kWh)"],
        "Cycle_Count_per_Year": (user_input["Vehicle Age (years)"] * 250) / user_input["Vehicle Age (years)"] if user_input["Vehicle Age (years)"] > 0 else 0
    }

# Normalization factors for inputs
normalization_factors = {
    "Battery Capacity (kWh)": 100,
    "Charging Duration (hours)": 12,
    "Charging Rate (kW)": 250,
    "State of Charge (Start %)": 100,
    "State of Charge (End %)": 100,
    "Distance Driven (since last charge) (km)": 800,
    "Temperature (°C)": 50,
    "Vehicle Age (years)": 20,
    "Cycle_Count": 3000,
    "Temperature_Stress_Score": 10,
    "Charging_Efficiency": 1,
    "Energy_per_km": 0.3,
    "Cycle_Count_per_Year": 300
}

# Route to render the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle the form submission and prediction
@app.route('/predict', methods=['POST'])
def predict():
    user_input = {
        "Battery Capacity (kWh)": float(request.form['batteryCapacity']),
        "Charging Duration (hours)": float(request.form['chargingDuration']),
        "Charging Rate (kW)": float(request.form['chargingRate']),
        "State of Charge (Start %)": float(request.form['socStart']),
        "State of Charge (End %)": float(request.form['socEnd']),
        "Distance Driven (since last charge) (km)": float(request.form['distanceDriven']),
        "Temperature (°C)": float(request.form['temperature']),
        "Vehicle Age (years)": float(request.form['vehicleAge']),
        "Charger Type": int(request.form['chargerType']),
        "User Type": int(request.form['userType']),
    }

    # Compute derived inputs
    derived_inputs = compute_derived_inputs(user_input)

    # Merge derived inputs with user inputs
    full_input = {**user_input, **derived_inputs}

    # Normalize the inputs before feeding into the model
    normalized_input = {
        key: (value / normalization_factors[key]) if key in normalization_factors else value
        for key, value in full_input.items()
    }

    # Prepare DataFrame for prediction
    test_df = pd.DataFrame([normalized_input])
    prediction = model.predict(test_df)[0]

    # Denormalize the prediction (multiply by 100 to get percentage)
    predicted_soh = prediction * 100

    # Determine health status based on SoH
    if predicted_soh >= 80:
        health_status = "✅ Battery is in great shape!"
        status_class = "green"
    elif 50 <= predicted_soh < 80:
        health_status = "🟡 Moderate battery health. Consider improving charging habits."
        status_class = "yellow"
    else:
        health_status = "🔴 High degradation detected. Battery replacement may be needed."
        status_class = "red"

    # Return the result as a JSON response
    return jsonify({
        'predicted_soh': round(predicted_soh, 2),
        'health_status': health_status,
        'status_class': status_class
    })

if __name__ == '__main__':
    app.run(debug=True)
