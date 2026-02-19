/**
 * Idempotent schema fix for Physical AI Auth database.
 *
 * Ensures:
 * 1. Better Auth core tables exist ("user", "session", "account", "verification")
 * 2. Custom columns "role" and "onboardingCompleted" exist on "user" table
 * 3. "user_profiles" table exists (free-text backgrounds, no CHECK on software/hardware)
 * 4. Migrates any existing auth_users data into new Better Auth tables
 *
 * Safe to run multiple times — all operations are idempotent.
 *
 * Run: node scripts/fix-schema.js
 */

import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";

dotenv.config();

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

async function fixSchema() {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    // ─── Step 1: Create Better Auth core tables ───

    // "user" table (Better Auth standard schema)
    await client.query(`
      CREATE TABLE IF NOT EXISTS "user" (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        "emailVerified" BOOLEAN NOT NULL DEFAULT false,
        image TEXT,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
      )
    `);
    console.log('"user" table ensured.');

    // "session" table
    await client.query(`
      CREATE TABLE IF NOT EXISTS "session" (
        id TEXT PRIMARY KEY,
        "expiresAt" TIMESTAMP NOT NULL,
        token TEXT NOT NULL UNIQUE,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "ipAddress" TEXT,
        "userAgent" TEXT,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
      )
    `);
    console.log('"session" table ensured.');

    // "account" table
    await client.query(`
      CREATE TABLE IF NOT EXISTS "account" (
        id TEXT PRIMARY KEY,
        "accountId" TEXT NOT NULL,
        "providerId" TEXT NOT NULL,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        "accessToken" TEXT,
        "refreshToken" TEXT,
        "idToken" TEXT,
        "accessTokenExpiresAt" TIMESTAMP,
        "refreshTokenExpiresAt" TIMESTAMP,
        scope TEXT,
        password TEXT,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
      )
    `);
    console.log('"account" table ensured.');

    // "verification" table
    await client.query(`
      CREATE TABLE IF NOT EXISTS "verification" (
        id TEXT PRIMARY KEY,
        identifier TEXT NOT NULL,
        value TEXT NOT NULL,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP DEFAULT NOW(),
        "updatedAt" TIMESTAMP DEFAULT NOW()
      )
    `);
    console.log('"verification" table ensured.');

    // ─── Step 2: Add custom columns to "user" table ───

    const roleExists = await client.query(`
      SELECT 1 FROM information_schema.columns
      WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'role'
    `);
    if (roleExists.rows.length === 0) {
      await client.query(`ALTER TABLE "user" ADD COLUMN "role" TEXT DEFAULT 'student'`);
      console.log('Added "role" column to "user" table.');
    } else {
      console.log('"role" column already exists.');
    }

    const onboardingExists = await client.query(`
      SELECT 1 FROM information_schema.columns
      WHERE table_schema = 'public' AND table_name = 'user' AND column_name = 'onboardingCompleted'
    `);
    if (onboardingExists.rows.length === 0) {
      await client.query(`ALTER TABLE "user" ADD COLUMN "onboardingCompleted" BOOLEAN DEFAULT false`);
      console.log('Added "onboardingCompleted" column to "user" table.');
    } else {
      console.log('"onboardingCompleted" column already exists.');
    }

    // ─── Step 3: Ensure user_profiles table (free-text backgrounds) ───

    await client.query(`
      CREATE TABLE IF NOT EXISTS user_profiles (
        id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id TEXT UNIQUE NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        software_background TEXT NOT NULL DEFAULT 'none',
        hardware_background TEXT NOT NULL DEFAULT 'none',
        robotics_knowledge TEXT NOT NULL DEFAULT 'none'
          CHECK (robotics_knowledge IN ('none', 'beginner', 'intermediate', 'advanced')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log("user_profiles table ensured.");

    // Drop CHECK constraints on software_background and hardware_background
    const constraints = await client.query(`
      SELECT conname FROM pg_constraint
      WHERE conrelid = 'user_profiles'::regclass
        AND contype = 'c'
        AND (conname LIKE '%software%' OR conname LIKE '%hardware%')
    `);
    for (const row of constraints.rows) {
      await client.query(`ALTER TABLE user_profiles DROP CONSTRAINT "${row.conname}"`);
      console.log(`Dropped constraint: ${row.conname}`);
    }
    if (constraints.rows.length === 0) {
      console.log("No CHECK constraints to drop on software/hardware columns.");
    }

    // ─── Step 4: Migrate existing auth_users if any ───

    const oldTableExists = await client.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables WHERE table_name = 'auth_users'
      )
    `);

    if (oldTableExists.rows[0].exists) {
      const oldUsers = await client.query("SELECT * FROM auth_users");
      let migrated = 0;

      for (const user of oldUsers.rows) {
        // Insert into "user" table
        const inserted = await client.query(
          `INSERT INTO "user" (id, name, email, "emailVerified", role, "onboardingCompleted", "createdAt", "updatedAt")
           VALUES ($1, $2, $3, $4, $5, false, $6, $7)
           ON CONFLICT (id) DO NOTHING
           RETURNING id`,
          [
            user.id,
            user.name || user.email.split("@")[0],
            user.email,
            user.email_verified || false,
            user.role || "student",
            user.created_at || new Date(),
            user.updated_at || new Date(),
          ]
        );

        if (inserted.rows.length > 0) {
          // Insert into "account" table (credential provider)
          await client.query(
            `INSERT INTO account (id, "accountId", "providerId", "userId", password, "createdAt", "updatedAt")
             VALUES ($1, $2, 'credential', $3, $4, $5, $6)
             ON CONFLICT DO NOTHING`,
            [
              `acct_${user.id}`,
              user.id,
              user.id,
              user.password_hash,
              user.created_at || new Date(),
              user.updated_at || new Date(),
            ]
          );

          // Create default profile
          await client.query(
            `INSERT INTO user_profiles (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING`,
            [user.id]
          );

          migrated++;
          console.log(`  Migrated user: ${user.email}`);
        }
      }

      console.log(`Migrated ${migrated} of ${oldUsers.rows.length} users from auth_users.`);
    } else {
      console.log("No auth_users table found — skipping data migration.");
    }

    await client.query("COMMIT");

    // ─── Verify ───
    const tables = await client.query(
      `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name`
    );
    console.log("\nFinal tables:", tables.rows.map(r => r.table_name).join(", "));
    console.log("\nSchema fix complete.");
  } catch (error) {
    await client.query("ROLLBACK");
    console.error("Schema fix failed:", error);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

fixSchema();
