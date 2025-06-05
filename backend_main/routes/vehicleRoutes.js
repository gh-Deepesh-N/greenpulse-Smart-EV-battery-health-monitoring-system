const express = require("express");
const router = express.Router();
const Vehicle = require("../models/Vehicle"); // ✅ Correct
// This middleware verifies token & attaches user info to req.user
const protect = require("../middleware/authMiddleware");

// [1] Create a new vehicle for the logged-in user
router.post("/create", protect, async (req, res) => {
  try {
    const { vehicleName, vehicleModel, batteryCapacity, vehicleAge } = req.body;
    
    // Create a new vehicle referencing the logged-in user's ID
    const newVehicle = new Vehicle({
      userId: req.user.id,
      vehicleName,
      vehicleModel,
      batteryCapacity,
      vehicleAge
    });
    
    const savedVehicle = await newVehicle.save();
    res.status(201).json({ message: "Vehicle created", vehicle: savedVehicle });
  } catch (error) {
    console.error("Error creating vehicle:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [2] Get all vehicles for the logged-in user
router.get("/my-vehicles", protect, async (req, res) => {
  try {
    const vehicles = await Vehicle.find({ userId: req.user.id });
    res.json(vehicles);
  } catch (error) {
    console.error("Error fetching vehicles:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [3] Optionally, get a single vehicle by ID
router.get("/:vehicleId", protect, async (req, res) => {
  try {
    const vehicle = await Vehicle.findOne({
      _id: req.params.vehicleId,
      userId: req.user.id
    });
    if (!vehicle) {
      return res.status(404).json({ message: "Vehicle not found" });
    }
    res.json(vehicle);
  } catch (error) {
    console.error("Error fetching vehicle:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [4] Optionally, update a vehicle
router.put("/:vehicleId", protect, async (req, res) => {
  try {
    const updated = await Vehicle.findOneAndUpdate(
      { _id: req.params.vehicleId, userId: req.user.id },
      { ...req.body },  // or specify fields to update
      { new: true }
    );
    if (!updated) {
      return res.status(404).json({ message: "Vehicle not found or not yours" });
    }
    res.json({ message: "Vehicle updated", vehicle: updated });
  } catch (error) {
    console.error("Error updating vehicle:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [5] Optionally, delete a vehicle
router.delete("/:vehicleId", protect, async (req, res) => {
  try {
    const deleted = await Vehicle.findOneAndDelete({
      _id: req.params.vehicleId,
      userId: req.user.id
    });
    if (!deleted) {
      return res.status(404).json({ message: "Vehicle not found or not yours" });
    }
    res.json({ message: "Vehicle deleted" });
  } catch (error) {
    console.error("Error deleting vehicle:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

module.exports = router;
