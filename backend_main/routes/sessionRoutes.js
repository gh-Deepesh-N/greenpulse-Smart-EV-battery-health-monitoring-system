const express = require("express");
const router = express.Router();
const Vehicle = require("../models/Vehicle"); // ✅ Correct
const Session = require("../models/Session");
const protect = require("../middleware/authMiddleware");

// [1] Create a new session for a given vehicle
router.post("/create/:vehicleId", protect, async (req, res) => {
  try {
    const { vehicleId } = req.params;
    const {
      sessionDate,
      startSoC,
      endSoC,
      chargingDuration,
      chargingRate,
      distanceDriven,
      temperature,
      chargerType
    } = req.body;

    // Validate that the vehicle belongs to the current user
    const vehicle = await Vehicle.findOne({ _id: vehicleId, userId: req.user.id });
    if (!vehicle) {
      return res.status(403).json({ message: "Vehicle not found or not owned by user." });
    }

    // 1. Compute Derived Fields
    const depthOfDischarge = 100 - (startSoC || 0);

    // Calculate Temperature Stress Score (only if temperature > 25)
    let temperatureStressScore = 0;
    if (temperature > 25) {
      temperatureStressScore = (temperature - 25) * 0.05;
    }

    // Calculate Charging Efficiency
    let chargingEfficiency = 0.95 - ((chargingRate || 0) * 0.001);
    if (chargingEfficiency < 0) chargingEfficiency = 0;
    if (chargingEfficiency > 1) chargingEfficiency = 1;

    // Calculate Energy per km
    let energyPerKm = 0;
    if (distanceDriven && vehicle.batteryCapacity) {
      energyPerKm = distanceDriven / vehicle.batteryCapacity;
    }

    // Create a new session with derived fields
    const newSession = new Session({
      vehicleId,
      sessionDate,
      startSoC,
      endSoC,
      chargingDuration,
      chargingRate,
      distanceDriven,
      temperature,
      chargerType, // Store charger type

      // Computed fields:
      depthOfDischarge,
      temperatureStressScore,
      chargingEfficiency,
      energyPerKm
    });

    const savedSession = await newSession.save();
    res.status(201).json({ message: "Session logged successfully!", session: savedSession });
  } catch (error) {
    console.error("Error creating session:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [2] Get all sessions for a given vehicle
router.get("/vehicle/:vehicleId", protect, async (req, res) => {
  try {
    const { vehicleId } = req.params;
    // Ensure vehicle belongs to user
    const vehicle = await Vehicle.findOne({ _id: vehicleId, userId: req.user.id });
    if (!vehicle) {
      return res.status(403).json({ message: "Vehicle not found or not owned by user." });
    }

    // Fetch sessions associated with that vehicle
    const sessions = await Session.find({ vehicleId }).sort({ sessionDate: -1 });
    res.json(sessions);
  } catch (error) {
    console.error("Error fetching sessions:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [3] Optionally, get a single session by ID
router.get("/:sessionId", protect, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const session = await Session.findById(sessionId);
    if (!session) {
      return res.status(404).json({ message: "Session not found" });
    }

    // Check ownership by checking the session's vehicle → userId
    const vehicle = await Vehicle.findOne({ _id: session.vehicleId });
    if (!vehicle || vehicle.userId.toString() !== req.user.id) {
      return res.status(403).json({ message: "Not authorized to view this session" });
    }

    res.json(session);
  } catch (error) {
    console.error("Error fetching session:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [4] Optionally, update a session
router.put("/:sessionId", protect, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const sessionToUpdate = await Session.findById(sessionId);
    if (!sessionToUpdate) {
      return res.status(404).json({ message: "Session not found" });
    }

    // Ensure current user owns the vehicle for this session
    const vehicle = await Vehicle.findById(sessionToUpdate.vehicleId);
    if (!vehicle || vehicle.userId.toString() !== req.user.id) {
      return res.status(403).json({ message: "Not authorized to update this session" });
    }

    const {
      sessionDate,
      startSoC,
      endSoC,
      chargingDuration,
      chargingRate,
      distanceDriven,
      temperature,
      chargerType
    } = req.body;

    // 1. Compute Derived Fields
    const depthOfDischarge = 100 - (startSoC || 0);

    // Calculate Temperature Stress Score (only if temperature > 25)
    let temperatureStressScore = 0;
    if (temperature > 25) {
      temperatureStressScore = (temperature - 25) * 0.05;
    }

    // Calculate Charging Efficiency
    let chargingEfficiency = 0.95 - ((chargingRate || 0) * 0.001);
    if (chargingEfficiency < 0) chargingEfficiency = 0;
    if (chargingEfficiency > 1) chargingEfficiency = 1;

    // Calculate Energy per km
    let energyPerKm = 0;
    if (distanceDriven && vehicle.batteryCapacity) {
      energyPerKm = distanceDriven / vehicle.batteryCapacity;
    }

    // Update the session with the computed data
    const updatedSession = await Session.findByIdAndUpdate(
      sessionId, 
      {
        sessionDate,
        startSoC,
        endSoC,
        chargingDuration,
        chargingRate,
        distanceDriven,
        temperature,
        chargerType, // Update charger type
        depthOfDischarge,
        temperatureStressScore,
        chargingEfficiency,
        energyPerKm
      }, 
      { new: true }
    );
    
    res.json({ message: "Session updated", session: updatedSession });
  } catch (error) {
    console.error("Error updating session:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

// [5] Optionally, delete a session
router.delete("/:sessionId", protect, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const sessionToDelete = await Session.findById(sessionId);
    if (!sessionToDelete) {
      return res.status(404).json({ message: "Session not found" });
    }

    // Ensure current user owns the vehicle for this session
    const vehicle = await Vehicle.findById(sessionToDelete.vehicleId);
    if (!vehicle || vehicle.userId.toString() !== req.user.id) {
      return res.status(403).json({ message: "Not authorized to delete this session" });
    }

    await Session.deleteOne({ _id: sessionId });
    res.json({ message: "Session deleted" });
  } catch (error) {
    console.error("Error deleting session:", error);
    res.status(500).json({ message: "Server Error" });
  }
});

module.exports = router;
