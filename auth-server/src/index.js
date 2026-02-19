/**
 * Physical AI Authentication Server
 *
 * Better Auth SDK + Neon Postgres.
 * Custom endpoints for user profile/onboarding.
 */

import express from "express";
import cors from "cors";
import pkg from "pg";
const { Pool } = pkg;
import { toNodeHandler } from "better-auth/node";
import { auth } from "./auth.js";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3002;

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

// CORS
app.use(
  cors({
    origin: [
      "http://localhost:3000",
      "http://localhost:3001",
      "http://localhost:3002",
      "http://127.0.0.1:3000",
    ],
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization", "Cookie"],
  })
);

// Better Auth handles ALL /api/auth/* routes
app.all("/api/auth/*", toNodeHandler(auth));

// JSON parsing for custom routes below
app.use(express.json());

// --- Helper: parse session from cookie ---
async function getSessionFromRequest(req) {
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) return null;

  const cookies = {};
  cookieHeader.split(";").forEach((cookie) => {
    const [name, ...rest] = cookie.trim().split("=");
    cookies[name] = decodeURIComponent(rest.join("="));
  });

  const sessionToken = cookies["physical-ai.session_token"];
  if (!sessionToken) return null;

  try {
    const session = await auth.api.getSession({
      headers: new Headers({ cookie: cookieHeader }),
    });
    return session;
  } catch {
    return null;
  }
}

// --- Allowed values ---
const ALLOWED_ROBOTICS_LEVELS = ["none", "beginner", "intermediate", "advanced"];
const MAX_TEXT_LENGTH = 2000;

// Simple in-memory rate limiter for signup-related endpoints
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 10; // max requests per window

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW) {
    rateLimitMap.set(ip, { windowStart: now, count: 1 });
    return true;
  }
  entry.count++;
  return entry.count <= RATE_LIMIT_MAX;
}

// Sanitize text input: trim, collapse whitespace, strip control chars
function sanitizeText(str) {
  if (typeof str !== "string") return "";
  return str
    .trim()
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "")
    .slice(0, MAX_TEXT_LENGTH);
}

// POST /api/profile — save onboarding profile
app.post("/api/profile", async (req, res) => {
  try {
    const clientIp = req.ip || req.connection?.remoteAddress;
    if (!checkRateLimit(clientIp)) {
      return res.status(429).json({ error: "Too many requests. Please wait." });
    }

    const session = await getSessionFromRequest(req);
    if (!session?.user) {
      return res.status(401).json({ error: "Authentication required" });
    }

    const { softwareBackground, hardwareBackground, roboticsKnowledge } =
      req.body;

    // Validate robotics knowledge (enum)
    if (!ALLOWED_ROBOTICS_LEVELS.includes(roboticsKnowledge)) {
      return res.status(400).json({ error: "Invalid roboticsKnowledge value. Must be: none, beginner, intermediate, or advanced." });
    }

    // Sanitize free-text fields
    const safeSoftware = sanitizeText(softwareBackground);
    const safeHardware = sanitizeText(hardwareBackground);

    if (!safeSoftware) {
      return res.status(400).json({ error: "Software background is required." });
    }
    if (!safeHardware) {
      return res.status(400).json({ error: "Hardware background is required." });
    }

    const userId = session.user.id;

    // Upsert user_profiles
    const result = await pool.query(
      `INSERT INTO user_profiles (user_id, software_background, hardware_background, robotics_knowledge)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (user_id) DO UPDATE SET
         software_background = $2,
         hardware_background = $3,
         robotics_knowledge = $4,
         updated_at = CURRENT_TIMESTAMP
       RETURNING *`,
      [userId, safeSoftware, safeHardware, roboticsKnowledge]
    );

    // Mark onboardingCompleted on user table
    await pool.query(
      `UPDATE "user" SET "onboardingCompleted" = true, "updatedAt" = NOW() WHERE id = $1`,
      [userId]
    );

    res.json({
      profile: result.rows[0],
      onboardingCompleted: true,
    });
  } catch (error) {
    console.error("Profile save error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /api/profile — get user profile
app.get("/api/profile", async (req, res) => {
  try {
    const session = await getSessionFromRequest(req);
    if (!session?.user) {
      return res.status(401).json({ error: "Authentication required" });
    }

    const result = await pool.query(
      "SELECT * FROM user_profiles WHERE user_id = $1",
      [session.user.id]
    );

    res.json({ profile: result.rows[0] || null });
  } catch (error) {
    console.error("Profile fetch error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Health check
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({
      status: "healthy",
      service: "Physical AI Auth Server",
      database: "Neon Postgres",
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({
      status: "unhealthy",
      error: "Database connection failed",
    });
  }
});

// Root
app.get("/", (req, res) => {
  res.json({
    name: "Physical AI Authentication Server",
    version: "2.0.0",
    database: "Neon Postgres",
    auth: "Better Auth SDK",
    endpoints: {
      auth: "ALL /api/auth/* (Better Auth)",
      profile: {
        save: "POST /api/profile",
        get: "GET /api/profile",
      },
      health: "GET /health",
    },
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error("Server error:", err);
  res.status(500).json({
    error: "Internal Server Error",
    message: process.env.NODE_ENV === "development" ? err.message : undefined,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
========================================
  Physical AI Auth Server v2
========================================
  Server running on: http://localhost:${PORT}
  Environment: ${process.env.NODE_ENV || "development"}
  Database: Neon Postgres
  Auth: Better Auth SDK

  Auth Endpoints: /api/auth/* (Better Auth)
  Profile: POST/GET /api/profile
  Health: http://localhost:${PORT}/health
========================================
  `);
});
