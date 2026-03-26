/**
 * Physical AI Authentication Server
 *
 * Better Auth SDK + Neon Postgres.
 * Custom endpoints for user profile/onboarding.
 */

// Polyfill Web Crypto for Node.js < 19 (required by Better Auth OIDC cookie signing)
// Check for .subtle specifically — some Node versions expose globalThis.crypto but
// without the SubtleCrypto interface that Better Auth's RS256 signing requires.
import nodeCrypto from "crypto";
if (!globalThis.crypto?.subtle) {
  globalThis.crypto = nodeCrypto.webcrypto;
}
// Diagnostic: log crypto status at startup
console.log(`[startup] Node.js ${process.version} | globalThis.crypto: ${!!globalThis.crypto} | subtle: ${!!globalThis.crypto?.subtle}`);

import express from "express";
import cors from "cors";
import pkg from "pg";
const { Pool } = pkg;
import { toNodeHandler } from "better-auth/node";
import { auth, BETTER_AUTH_BASE_URL } from "./auth.js";
import dotenv from "dotenv";
import rateLimiter from "./utils/rate-limiter.js";
import crypto from "crypto";

dotenv.config();

const app = express();
app.set('trust proxy', 1); // Required: Railway runs behind a reverse proxy — trust forwarded headers
const PORT = process.env.PORT || 3002;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

// Initialize rate limiter
await rateLimiter.initialize();

// CORS — parse allowed origins from env var or fall back to localhost defaults
// Production frontend origin — always allowed regardless of CORS_ORIGINS env var
const PRODUCTION_ORIGIN = "https://ayeshakhalid192007-dev.github.io";

const allowedOrigins = [
  ...(process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(",").map((o) => o.trim())
    : [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
      ]),
  // Always include production origin so GitHub Pages frontend can reach the API
  ...(PRODUCTION_ORIGIN ? [PRODUCTION_ORIGIN] : []),
].filter((v, i, a) => a.indexOf(v) === i); // deduplicate

app.use(
  cors({
    origin: allowedOrigins,
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization", "Cookie"],
  })
);

// GET redirect for social sign-in — serves a tiny page that performs a
// same-origin POST to Better Auth's /api/auth/sign-in/social endpoint.
// Because the browser is ON the auth-server domain when the fetch runs,
// the OAuth state cookie is set as a **first-party** cookie, avoiding
// third-party cookie restrictions when the frontend (GitHub Pages) and
// auth server (Railway) are on different origins.
// Placed outside /api/auth/* to avoid Better Auth's catch-all handler.
app.get("/social-redirect", (req, res) => {
  const { provider, callbackURL } = req.query;

  if (!provider || !callbackURL) {
    return res.status(400).json({ error: "provider and callbackURL are required" });
  }

  // Only allow known providers to prevent injection
  if (!["google", "github"].includes(provider)) {
    return res.status(400).json({ error: "Invalid provider" });
  }

  // Embed values safely via JSON.stringify (handles all escaping)
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.send(`<!DOCTYPE html>
<html><head><title>Redirecting…</title></head>
<body>
<p>Redirecting to ${provider === "google" ? "Google" : "GitHub"}…</p>
<script>
(async () => {
  try {
    const resp = await fetch("/api/auth/sign-in/social", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ provider: ${JSON.stringify(provider)}, callbackURL: ${JSON.stringify(callbackURL)} })
    });
    const data = await resp.json();
    if (data.url) {
      window.location.href = data.url;
    } else {
      document.body.textContent = "Sign-in failed. Please go back and try again.";
    }
  } catch (e) {
    document.body.textContent = "Network error. Please go back and try again.";
  }
})();
</script>
</body></html>`);
});

// POST /credential-relay — same-domain sign-in relay for email/password PKCE flow.
// The frontend (GitHub Pages) cannot reliably send SameSite=Lax session cookies
// in cross-domain navigations. By having the browser POST credentials directly
// to this endpoint on the auth server, the resulting session cookie is first-party
// and is sent when we immediately redirect to /api/auth/oauth2/authorize.
// Same principle as /social-redirect for social login.
app.post("/credential-relay", express.urlencoded({ extended: false }), async (req, res) => {
  const { email, password, client_id, redirect_uri, response_type, scope, state, code_challenge, code_challenge_method } = req.body;

  const frontendLoginBase = process.env.OIDC_BASE_URL ||
    `${(process.env.FRONTEND_URL || "https://ayeshakhalid192007-dev.github.io").replace(/\/$/, "")}/humanoid-ai-studio`;

  // Rebuild the OAuth params to forward on redirect
  const oauthQS = new URLSearchParams({ client_id, redirect_uri, response_type: response_type || "code", scope: scope || "openid profile email", state, code_challenge, code_challenge_method: code_challenge_method || "S256" }).toString();

  if (!email || !password) {
    return res.redirect(`${frontendLoginBase}/auth/login?${oauthQS}&_error=${encodeURIComponent("Email and password are required")}`);
  }

  try {
    // Call sign-in as a same-origin request so Better Auth sets a first-party session cookie
    const signInResp = await auth.handler(
      new Request(`${BETTER_AUTH_BASE_URL}/api/auth/sign-in/email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
    );

    if (!signInResp.ok) {
      return res.redirect(`${frontendLoginBase}/auth/login?${oauthQS}&_error=${encodeURIComponent("Invalid email or password")}`);
    }

    // Forward session cookies from Better Auth as first-party (we are on the auth server domain)
    const rawSetCookie = signInResp.headers.getSetCookie?.() ?? [];
    rawSetCookie.forEach((c) => res.append("Set-Cookie", c));

    // Redirect to authorize — session cookie is now first-party and will be sent
    res.redirect(`/api/auth/oauth2/authorize?${oauthQS}`);
  } catch (err) {
    console.error("[credential-relay] error:", err);
    res.redirect(`${frontendLoginBase}/auth/login?${oauthQS}&_error=${encodeURIComponent("Authentication error. Please try again.")}`);
  }
});

// Better Auth handles ALL /api/auth/* routes
app.all("/api/auth/*", toNodeHandler(auth));

// JSON parsing for custom routes below
app.use(express.json());

// --- Helper: resolve session from cookie OR Bearer token ---
async function getSessionFromRequest(req) {
  // 1. Try Bearer token first (OAuth clients)
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith("Bearer ")) {
    // 1a. Try as Better Auth session token (bearer plugin)
    try {
      const session = await auth.api.getSession({
        headers: new Headers({ authorization: authHeader }),
      });
      if (session?.user) return session;
    } catch {
      // fall through
    }

    // 1b. Try as OAuth2 JWT access token via the OIDC userinfo endpoint.
    // The oidcProvider issues JWT access tokens that auth.api.getSession() does
    // not understand — use the /userinfo endpoint which validates JWTs natively.
    try {
      const userinfoResp = await auth.handler(
        new Request(`${BETTER_AUTH_BASE_URL}/api/auth/oauth2/userinfo`, {
          headers: { authorization: authHeader },
        })
      );
      if (userinfoResp.ok) {
        const info = await userinfoResp.json();
        if (info?.sub) {
          const result = await pool.query(`SELECT * FROM "user" WHERE id = $1`, [info.sub]);
          if (result.rows[0]) {
            return { user: result.rows[0], session: null };
          }
        }
      }
    } catch {
      // fall through to cookie check
    }
  }

  // 2. Fall back to cookie session (legacy / same-origin clients)
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) return null;

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

// Rate limiting middleware using Redis
async function checkRateLimit(req, res, next) {
  const clientIp = req.ip || req.connection?.remoteAddress || 'unknown';
  const endpoint = req.path; // Use endpoint as part of rate limit key
  const rateLimitKey = `${clientIp}:${endpoint}`;

  const result = await rateLimiter.checkLimit(rateLimitKey);

  if (!result.allowed) {
    const retryAfter = result.retryAfter || 60; // Default to 60 seconds if not provided
    res.set('Retry-After', retryAfter.toString());
    res.set('X-RateLimit-Reset', result.resetTime);

    return res.status(429).json({
      error: "Too many requests. Please try again later.",
      resetTime: result.resetTime,
      retryAfter: retryAfter
    });
  }

  // Set rate limit headers for successful requests
  res.set('X-RateLimit-Remaining', result.remaining || 0);
  res.set('X-RateLimit-Reset', result.resetTime);

  next();
}

// Sanitize text input: trim, collapse whitespace, strip control chars
function sanitizeText(str) {
  if (typeof str !== "string") return "";
  return str
    .trim()
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "")
    .slice(0, MAX_TEXT_LENGTH);
}

// POST /api/profile — save onboarding profile (with rate limiting)
app.post("/api/profile", checkRateLimit, async (req, res) => {
  try {
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

// --- Admin: register a new OAuth client ---
app.post("/api/admin/clients/register", async (req, res) => {
  try {
    const session = await getSessionFromRequest(req);
    if (!session?.user) {
      return res.status(401).json({ error: "Authentication required" });
    }
    if (session.user.role !== "admin") {
      return res.status(403).json({ error: "Forbidden — admin only" });
    }

    const { name, redirectUrls, clientType } = req.body;

    if (!name || !Array.isArray(redirectUrls) || redirectUrls.length === 0) {
      return res.status(400).json({ error: "name and redirectUrls[] are required" });
    }

    const isPublic = clientType !== "confidential";
    const clientId = crypto.randomBytes(24).toString("base64url");
    const clientSecret = isPublic ? null : crypto.randomBytes(32).toString("base64url");

    const metadata = JSON.stringify({
      token_endpoint_auth_method: isPublic ? "none" : "client_secret_post",
      grant_types: ["authorization_code", "refresh_token"],
    });

    await pool.query(
      `INSERT INTO "oauthApplication"
         (id, name, icon, metadata, "clientId", "clientSecret", "redirectUrls", type, disabled, "userId", "createdAt", "updatedAt")
       VALUES ($1, $2, NULL, $3, $4, $5, $6, $7, FALSE, NULL, NOW(), NOW())`,
      [
        crypto.randomUUID(),
        name,
        metadata,
        clientId,
        clientSecret,
        redirectUrls.join(","),
        isPublic ? "public" : "confidential",
      ]
    );

    res.status(201).json({
      client_id: clientId,
      client_secret: clientSecret,
      client_type: isPublic ? "public" : "confidential",
      name,
      redirect_uris: redirectUrls,
    });
  } catch (error) {
    console.error("Client registration error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Debug: show exact OAuth callback URLs (safe to expose — no secrets)
app.get("/debug/oauth-urls", (req, res) => {
  const base = (process.env.BETTER_AUTH_URL || "https://auth-server-production-c993.up.railway.app").replace(/\/+$/, "");
  res.json({
    better_auth_url: base,
    google_callback: `${base}/api/auth/callback/google`,
    github_callback: `${base}/api/auth/callback/github`,
    note: "Register these exact URLs in your Google Cloud Console and GitHub OAuth App",
  });
});

// Health check
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    const rateLimiterStatus = await rateLimiter.healthCheck();

    res.json({
      status: "healthy",
      service: "Physical AI Auth Server",
      database: "Neon Postgres",
      rateLimiter: rateLimiterStatus,
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
    version: "2.1.0",
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
async function startServer() {
  // Validate required env vars before starting
  if (!process.env.BETTER_AUTH_SECRET) {
    console.error("[startup] FATAL: BETTER_AUTH_SECRET is not set");
    process.exit(1);
  }
  if (!process.env.DATABASE_URL && !process.env.NEON_DATABASE_URL) {
    console.error("[startup] FATAL: DATABASE_URL or NEON_DATABASE_URL is not set");
    process.exit(1);
  }

  const authBase = (process.env.BETTER_AUTH_URL || "https://auth-server-production-c993.up.railway.app").replace(/\/+$/, "");
  console.log(`[startup] BETTER_AUTH_URL: ${authBase}`);
  console.log(`[startup] Google callback: ${authBase}/api/auth/callback/google`);
  console.log(`[startup] GitHub callback: ${authBase}/api/auth/callback/github`);

  try {
    app.listen(PORT, () => {
      console.log(`
========================================
  Physical AI Auth Server v2
========================================
  Server running on: http://localhost:${PORT}
  Environment: ${process.env.NODE_ENV || "development"}
  Database: Neon Postgres
  Auth: Better Auth SDK
  Rate Limiting: ${rateLimiter.isEnabled ? 'Redis' : 'In-memory Fallback'}

  Auth Endpoints: /api/auth/* (Better Auth)
  Profile: POST/GET /api/profile
  Health: http://localhost:${PORT}/health
  OAuth URLs: ${authBase}/debug/oauth-urls
========================================
  `);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

