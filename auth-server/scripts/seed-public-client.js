/**
 * Seed the book app as a trusted public OAuth client.
 *
 * Public clients use PKCE instead of a client secret (clientSecret = NULL).
 * This script is idempotent — safe to re-run.
 *
 * Run: node scripts/seed-public-client.js
 */

import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";
import crypto from "crypto";

dotenv.config();

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL || process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

const CLIENT_ID = process.env.BOOK_CLIENT_ID || "physical-ai-book";
const REDIRECT_URIS = process.env.BOOK_REDIRECT_URIS
  ? process.env.BOOK_REDIRECT_URIS.split(",").map((u) => u.trim()).join(",")
  : "http://localhost:3000/auth/callback";

async function seedPublicClient() {
  const client = await pool.connect();
  try {
    const existing = await client.query(
      `SELECT id FROM "oauthApplication" WHERE "clientId" = $1`,
      [CLIENT_ID]
    );

    const metadata = JSON.stringify({
      token_endpoint_auth_method: "none",
      grant_types: ["authorization_code", "refresh_token"],
    });

    if (existing.rows.length > 0) {
      await client.query(
        `UPDATE "oauthApplication"
         SET "redirectUrls" = $1, "updatedAt" = NOW()
         WHERE "clientId" = $2`,
        [REDIRECT_URIS, CLIENT_ID]
      );
      console.log(`✓ Updated existing client: ${CLIENT_ID}`);
    } else {
      await client.query(
        `INSERT INTO "oauthApplication"
           (id, name, icon, metadata, "clientId", "clientSecret", "redirectUrls", type, disabled, "userId", "createdAt", "updatedAt")
         VALUES ($1, $2, NULL, $3, $4, NULL, $5, 'public', FALSE, NULL, NOW(), NOW())`,
        [
          crypto.randomUUID(),
          "Physical AI Book",
          metadata,
          CLIENT_ID,
          REDIRECT_URIS,
        ]
      );
      console.log(`✓ Created public client: ${CLIENT_ID}`);
    }

    console.log(`  redirect_uris: ${REDIRECT_URIS}`);
    console.log(`  type: public (PKCE only, no secret)`);
    console.log("\n✅ Public client seed complete.");
  } catch (err) {
    console.error("Seed failed:", err.message);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

seedPublicClient();
