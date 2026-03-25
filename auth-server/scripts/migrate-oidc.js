/**
 * OIDC / OAuth 2.1 Database Migration
 *
 * Creates the tables required by Better Auth's oidcProvider and jwt plugins.
 * IMPORTANT: Better Auth v1.x uses camelCase table and column names directly —
 * it performs NO automatic snake_case conversion. All names must match exactly.
 *
 *   - "oauthApplication"  — registered OAuth clients
 *   - "oauthAccessToken"  — issued access / refresh tokens
 *   - "oauthConsent"      — user consent records
 *   - "jwks"              — RS256 key pairs (fix columns to camelCase)
 *
 * Run: node scripts/migrate-oidc.js
 */

import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";

dotenv.config();

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL || process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

async function migrateOIDC() {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    // --- Fix jwks columns: rename snake_case → camelCase ---
    // Better Auth reads/writes "publicKey", "privateKey", "createdAt" directly.
    const jwksColumns = await client.query(
      `SELECT column_name FROM information_schema.columns
       WHERE table_schema = 'public' AND table_name = 'jwks'`
    );
    const jwksCols = jwksColumns.rows.map((r) => r.column_name);
    if (jwksCols.includes("public_key")) {
      await client.query(`ALTER TABLE "jwks" RENAME COLUMN "public_key" TO "publicKey"`);
      console.log("✓ jwks: renamed public_key → publicKey");
    }
    if (jwksCols.includes("private_key")) {
      await client.query(`ALTER TABLE "jwks" RENAME COLUMN "private_key" TO "privateKey"`);
      console.log("✓ jwks: renamed private_key → privateKey");
    }
    if (jwksCols.includes("created_at")) {
      await client.query(`ALTER TABLE "jwks" RENAME COLUMN "created_at" TO "createdAt"`);
      console.log("✓ jwks: renamed created_at → createdAt");
    }
    // Ensure table exists if it wasn't created yet
    await client.query(`
      CREATE TABLE IF NOT EXISTS "jwks" (
        "id"         TEXT NOT NULL PRIMARY KEY,
        "publicKey"  TEXT NOT NULL,
        "privateKey" TEXT NOT NULL,
        "createdAt"  TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    `);
    console.log("✓ jwks table ready");

    // --- oauthApplication (camelCase — required by Better Auth Kysely adapter) ---
    await client.query(`
      CREATE TABLE IF NOT EXISTS "oauthApplication" (
        "id"           TEXT        NOT NULL PRIMARY KEY,
        "name"         TEXT        NOT NULL,
        "icon"         TEXT,
        "metadata"     TEXT,
        "clientId"     TEXT        NOT NULL UNIQUE,
        "clientSecret" TEXT,
        "redirectUrls" TEXT        NOT NULL,
        "type"         TEXT        NOT NULL DEFAULT 'public',
        "disabled"     BOOLEAN     NOT NULL DEFAULT FALSE,
        "userId"       TEXT,
        "createdAt"    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        "updatedAt"    TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    `);
    console.log('✓ "oauthApplication" table ready');

    // --- oauthAccessToken ---
    await client.query(`
      CREATE TABLE IF NOT EXISTS "oauthAccessToken" (
        "id"                     TEXT        NOT NULL PRIMARY KEY,
        "accessToken"            TEXT        NOT NULL UNIQUE,
        "refreshToken"           TEXT        UNIQUE,
        "accessTokenExpiresAt"   TIMESTAMPTZ NOT NULL,
        "refreshTokenExpiresAt"  TIMESTAMPTZ,
        "clientId"               TEXT        NOT NULL,
        "userId"                 TEXT,
        "scopes"                 TEXT        NOT NULL DEFAULT '',
        "createdAt"              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        "updatedAt"              TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    `);
    await client.query(`
      CREATE INDEX IF NOT EXISTS "idx_oauthAccessToken_clientId_userId"
        ON "oauthAccessToken"("clientId", "userId");
    `);
    console.log('✓ "oauthAccessToken" table ready');

    // --- oauthConsent ---
    await client.query(`
      CREATE TABLE IF NOT EXISTS "oauthConsent" (
        "id"           TEXT        NOT NULL PRIMARY KEY,
        "clientId"     TEXT        NOT NULL,
        "userId"       TEXT        NOT NULL,
        "scopes"       TEXT        NOT NULL DEFAULT '',
        "createdAt"    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        "updatedAt"    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        "consentGiven" BOOLEAN     NOT NULL DEFAULT FALSE,
        UNIQUE ("userId", "clientId")
      );
    `);
    console.log('✓ "oauthConsent" table ready');

    await client.query("COMMIT");
    console.log("\n✅ OIDC migration complete.");
  } catch (err) {
    await client.query("ROLLBACK");
    console.error("Migration failed, rolled back:", err.message);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

migrateOIDC();
