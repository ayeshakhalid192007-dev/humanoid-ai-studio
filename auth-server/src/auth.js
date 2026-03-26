/**
 * Better Auth Configuration
 *
 * Configures Better Auth with:
 * - Email/Password authentication (PBKDF2 for password compat)
 * - Session management
 * - Neon Postgres database (via pg Pool)
 * - Onboarding support via additionalFields
 * - OAuth 2.1 / OIDC Provider (oidcProvider plugin)
 * - JWT / JWKS with RS256 signing (jwt plugin)
 * - Bearer token acceptance (bearer plugin)
 * - Admin plugin for role management
 */

import dotenv from "dotenv";
dotenv.config();

import { betterAuth } from "better-auth";
import { oidcProvider } from "better-auth/plugins/oidc-provider";
import { jwt } from "better-auth/plugins/jwt";
import { bearer } from "better-auth/plugins/bearer";
import { admin } from "better-auth/plugins/admin";
import pg from "pg";
import crypto from "crypto";

const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

// Parse allowed origins from env or fall back to localhost defaults.
// Uses CORS_ORIGINS to stay consistent with index.js and the .env file.
// Production frontend origin — always trusted regardless of env config
const PRODUCTION_ORIGIN = "https://ayeshakhalid192007-dev.github.io";

const trustedOrigins = [
  ...((process.env.CORS_ORIGINS || process.env.ALLOWED_ORIGINS)
    ? (process.env.CORS_ORIGINS || process.env.ALLOWED_ORIGINS).split(",").map((o) => o.trim())
    : [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
      ]),
  PRODUCTION_ORIGIN,
].filter((v, i, a) => a.indexOf(v) === i); // deduplicate

// Sanitize base URL — ensure https:// prefix and strip trailing slash
const rawAuthUrl = process.env.BETTER_AUTH_URL || "https://auth-server-production-c993.up.railway.app";
const BETTER_AUTH_BASE_URL = (rawAuthUrl.startsWith("http") ? rawAuthUrl : `https://${rawAuthUrl}`).replace(/\/+$/, "");

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: BETTER_AUTH_BASE_URL,
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
  // Social providers — Google and GitHub OAuth 2.0
  // Better Auth handles the full OAuth flow automatically:
  // - POST /api/auth/sign-in/social  → returns { url } to redirect to provider
  // - GET  /api/auth/callback/:provider → exchanges code, creates/links user
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
      // Explicitly request read:user + user:email so we always get the primary
      // email, even when the GitHub user has their email set to private.
      scope: ["read:user", "user:email"],
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
  trustedOrigins,
  advanced: {
    useSecureCookies: process.env.NODE_ENV === "production",
    cookiePrefix: "physical-ai",
  },
  plugins: [
    // Bearer token support — allows API clients to authenticate with Authorization: Bearer <token>
    bearer(),

    // JWT plugin — enables JWKS endpoint (/api/auth/jwks) with RS256 asymmetric signing
    jwt({
      jwks: {
        keyPairConfig: {
          alg: "RS256",
        },
        disablePrivateKeyEncryption: true,
      },
    }),

    // OIDC Provider — turns this server into an OAuth 2.1 / OIDC authorization server
    oidcProvider({
      loginPage: `${process.env.FRONTEND_URL || "https://ayeshakhalid192007-dev.github.io/humanoid-ai-studio"}/auth/login`,
      consentPage: `${process.env.FRONTEND_URL || "https://ayeshakhalid192007-dev.github.io/humanoid-ai-studio"}/auth/consent`,
      // The book app is a trusted first-party public client (no secret — uses PKCE)
      trustedClients: [
        {
          clientId: process.env.BOOK_CLIENT_ID || "physical-ai-book",
          type: "public",
          redirectUrls: (process.env.BOOK_REDIRECT_URIS || "https://ayeshakhalid192007-dev.github.io/humanoid-ai-studio/auth/callback").split(",").map((u) => u.trim()),
          skipConsent: true,
        },
      ],
      // Expose role and onboardingCompleted in userinfo / ID token claims
      async getAdditionalUserInfoClaim(user) {
        return {
          role: user.role,
          onboardingCompleted: user.onboardingCompleted,
        };
      },
      useJWTPlugin: true,
      accessTokenExpiresIn: 60 * 60 * 6,        // 6 hours
      refreshTokenExpiresIn: 60 * 60 * 24 * 7,  // 7 days
      codeExpiresIn: 600,                        // 10 minutes
    }),

    // Admin plugin — role-based access control
    admin({
      defaultRole: "student",
      adminRoles: ["admin"],
    }),
  ],
});
