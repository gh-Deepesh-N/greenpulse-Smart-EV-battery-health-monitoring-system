const mongoose = require("mongoose");

const VehicleSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  vehicleName: {
    type: String,
    default: ""
  },
  vehicleModel: {
    type: String,
    required: true
  },
  batteryCapacity: {
    type: Number,
    default: 0
  },
  vehicleAge: {
    type: Number,
    default: 0
  },
  // ✅ New field for usage type
  userType: {
    type: String,
    enum: ["regular", "occasional", "heavy"],
    default: "regular"
  }
}, { timestamps: true });

module.exports = mongoose.model("Vehicle", VehicleSchema);
