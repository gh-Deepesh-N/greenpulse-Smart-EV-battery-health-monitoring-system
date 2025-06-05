const mongoose = require("mongoose");

const SessionSchema = new mongoose.Schema({
  vehicleId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Vehicle",
    required: true
  },
  sessionDate: {
    type: Date,
    default: Date.now
  },
  startSoC: Number,
  endSoC: Number,
  chargingDuration: Number,
  chargingRate: Number,
  distanceDriven: Number,
  temperature: Number,

  // ✅ New field for charger type
  chargerType: {
    type: String,
    enum: ["fast", "normal"],
    default: "normal"
  },

  // Derived fields
  depthOfDischarge: Number,
  temperatureStressScore: Number,
  chargingEfficiency: Number,
  energyPerKm: Number
}, { timestamps: true });

module.exports = mongoose.model("Session", SessionSchema);
