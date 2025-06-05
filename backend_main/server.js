const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");

// Existing routes
const authRoutes = require("./routes/authRoutes");

// New routes
const vehicleRoutes = require("./routes/vehicleRoutes");
const sessionRoutes = require("./routes/sessionRoutes");
const chatbotRoutes = require("../pages/Chatbot/chatbotRoutes");

// Initialize
dotenv.config();
connectDB();

const app = express();
app.use(express.json());
app.use(cors());

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/vehicles", vehicleRoutes);
app.use("/api/sessions", sessionRoutes);
app.use("/api/chatbot", chatbotRoutes); // ✅ Register chatbot route

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
