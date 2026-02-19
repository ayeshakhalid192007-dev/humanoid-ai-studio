/**
 * Better Auth Configuration
 *
 * Configures Better Auth with:
 * - Email/Password authentication (PBKDF2 for password compat)
 * - Session management
 * - Neon Postgres database (via pg Pool)
 * - Onboarding support via additionalFields
 */

import dotenv from "dotenv";
dotenv.config();

import { betterAuth } from "better-auth";
import pg from "pg";
import crypto from "crypto";

const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3002",
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    minPasswordLength: 8,
    password: {
      hash: async (password) => {
        const salt = crypto.randomBytes(16).toString("hex");
        const hash = crypto
          .pbkdf2Sync(password, salt, 1000, 64, "sha512")
          .toString("hex");
        return `${salt}:${hash}`;
      },
      verify: async ({ hash, password }) => {
        const [salt, storedHash] = hash.split(":");
        const verifyHash = crypto
          .pbkdf2Sync(password, salt, 1000, 64, "sha512")
          .toString("hex");
        return storedHash === verifyHash;
      },
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "student",
        input: false,
      },
      onboardingCompleted: {
        type: "boolean",
        defaultValue: false,
        input: false,
      },
    },
  },
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
  ],
  advanced: {
    useSecureCookies: process.env.NODE_ENV === "production",
    cookiePrefix: "physical-ai",
  },
  plugins: [
    // Add security plugin
    {
      name: "security-headers",
      routes: {
        async beforeAuth(ctx) {
          // Add security headers to all auth responses
          ctx.response.headers.set("X-Content-Type-Options", "nosniff");
          ctx.response.headers.set("X-Frame-Options", "DENY");
          ctx.response.headers.set("X-XSS-Protection", "1; mode=block");
          ctx.response.headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
          return ctx;
        }
      }
    }
  ]
});
