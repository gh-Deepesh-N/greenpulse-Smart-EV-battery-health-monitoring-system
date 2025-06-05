const jwt = require("jsonwebtoken");

const protect = (req, res, next) => {
    let token = req.header("Authorization");

    if (!token) return res.status(401).json({ message: "No token, authorization denied" });

    if (token.startsWith("Bearer ")) {
        token = token.slice(7, token.length).trimStart();
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ message: "Invalid token" });
    }
};

module.exports = protect;
