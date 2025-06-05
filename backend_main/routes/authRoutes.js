const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const User = require("../models/User");

const router = express.Router();
console.log("JWT Secret:", process.env.JWT_SECRET);


// Signup Route
router.post("/signup", async (req, res) => {
    let { username, email, password } = req.body;

    try {
        // ✅ 1. Trim input to remove unwanted spaces
        username = username.trim();
        email = email.trim().toLowerCase();
        password = password.trim();

        // ✅ 2. Input Validation
        if (!username || !email || !password) {
            return res.status(400).json({ message: "All fields are required" });
        }
        if (!/^\S+@\S+\.\S+$/.test(email)) {
            return res.status(400).json({ message: "Invalid email format" });
        }
        if (password.length < 6) {
            return res.status(400).json({ message: "Password must be at least 6 characters" });
        }

        // ✅ 3. Check if user already exists
        let user = await User.findOne({ email });
        if (user) return res.status(400).json({ message: "User already exists" });

        // ✅ 4. Hash password before saving
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // ✅ 5. Create new user
        user = new User({ username, email, password: hashedPassword });
        await user.save();

        // ✅ 6. Generate JWT Token
        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "1h" });

        // ✅ 7. Send response with token
        res.cookie("token", token, { httpOnly: true, secure: process.env.NODE_ENV === "production" });
        res.json({
            message: "Signup successful!",
            token,  // ✅ Now included in response
            user: { 
              id: user._id, 
              username, 
              email 
            }
        });

    } catch (err) {
        res.status(500).json({ message: "Server Error", error: err.message });
    }
});

// Login Route
router.post("/login", async (req, res) => {
    let { email, password } = req.body;

    try {
        // ✅ 1. Trim & normalize input
        email = email.trim().toLowerCase();
        password = password.trim();

        // ✅ 2. Check for empty fields
        if (!email || !password) {
            return res.status(400).json({ message: "Both email and password are required" });
        }

        // ✅ 3. Find user
        const user = await User.findOne({ email });
        if (!user) return res.status(400).json({ message: "Invalid credentials" });

        // ✅ 4. Compare passwords
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).json({ message: "Invalid credentials" });

        // ✅ 5. Generate JWT Token
        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "1h" });

        // ✅ 6. Send response with token
        res.cookie("token", token, { httpOnly: true, secure: process.env.NODE_ENV === "production" });
        res.json({
            message: "Login successful!",
            token,  // ✅ Now included in response
            user: { 
              id: user._id, 
              username: user.username, 
              email: user.email 
            }
        });

    } catch (err) {
        res.status(500).json({ message: "Server Error", error: err.message });
    }
});

// ✅ Logout Route
router.post("/logout", (req, res) => {
    res.clearCookie("token");
    res.json({ message: "Logged out successfully" });
});

module.exports = router;
