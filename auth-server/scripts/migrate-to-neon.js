/**
 * Migration Script: SQLite to Neon Postgres
 *
 * This script migrates existing user data from the SQLite database
 * to Neon Postgres. Password hashes are preserved.
 *
 * Usage: node scripts/migrate-to-neon.js
 */

import Database from "better-sqlite3";
import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";
import fs from "fs";
import path from "path";

dotenv.config();

const SQLITE_DB_PATH = "./auth.db";

async function migrate() {
  // Check if SQLite database exists
  if (!fs.existsSync(SQLITE_DB_PATH)) {
    console.log("No SQLite database found. Nothing to migrate.");
    process.exit(0);
  }

  console.log("Starting migration from SQLite to Neon Postgres...");

  // Connect to SQLite
  const sqlite = new Database(SQLITE_DB_PATH);

  // Connect to Postgres
  const pool = new Pool({
    connectionString: process.env.NEON_DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });

  try {
    // Create tables in Postgres if they don't exist
    await pool.query(`
      CREATE TABLE IF NOT EXISTS auth_users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT,
        role TEXT DEFAULT 'student',
        email_verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS auth_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log("Postgres tables created/verified.");

    // Get all users from SQLite
    const users = sqlite.prepare("SELECT * FROM users").all();
    console.log(`Found ${users.length} users to migrate.`);

    let migratedUsers = 0;
    let skippedUsers = 0;

    for (const user of users) {
      try {
        // Check if user already exists in Postgres
        const existing = await pool.query(
          "SELECT id FROM auth_users WHERE email = $1",
          [user.email]
        );

        if (existing.rows.length > 0) {
          console.log(`  Skipping ${user.email} (already exists)`);
          skippedUsers++;
          continue;
        }

        // Insert user into Postgres
        await pool.query(
          `INSERT INTO auth_users (id, email, password_hash, name, role, email_verified, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
          [
            user.id,
            user.email,
            user.password_hash,
            user.name,
            user.role || "student",
            user.email_verified === 1,
            user.created_at,
            user.updated_at,
          ]
        );

        console.log(`  Migrated user: ${user.email}`);
        migratedUsers++;
      } catch (err) {
        console.error(`  Error migrating ${user.email}:`, err.message);
      }
    }

    // Migrate sessions (optional - they'll expire anyway)
    const sessions = sqlite.prepare("SELECT * FROM sessions").all();
    console.log(`Found ${sessions.length} sessions.`);

    let migratedSessions = 0;
    for (const session of sessions) {
      try {
        // Check if session user exists in Postgres
        const userExists = await pool.query(
          "SELECT id FROM auth_users WHERE id = $1",
          [session.user_id]
        );

        if (userExists.rows.length === 0) {
          continue; // Skip sessions for non-existent users
        }

        // Check if session already exists
        const existing = await pool.query(
          "SELECT id FROM auth_sessions WHERE token = $1",
          [session.token]
        );

        if (existing.rows.length > 0) {
          continue;
        }

        await pool.query(
          `INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at)
           VALUES ($1, $2, $3, $4, $5)`,
          [
            session.id,
            session.user_id,
            session.token,
            session.expires_at,
            session.created_at,
          ]
        );
        migratedSessions++;
      } catch (err) {
        // Sessions may fail if they reference old user IDs - that's OK
      }
    }

    console.log("\n========================================");
    console.log("Migration Complete!");
    console.log("========================================");
    console.log(`Users migrated: ${migratedUsers}`);
    console.log(`Users skipped (already exist): ${skippedUsers}`);
    console.log(`Sessions migrated: ${migratedSessions}`);
    console.log("========================================");

    // Backup SQLite file
    const backupPath = `${SQLITE_DB_PATH}.backup`;
    fs.copyFileSync(SQLITE_DB_PATH, backupPath);
    console.log(`\nSQLite database backed up to: ${backupPath}`);
    console.log("You can safely delete auth.db after verifying the migration.");
  } catch (error) {
    console.error("Migration failed:", error);
    process.exit(1);
  } finally {
    sqlite.close();
    await pool.end();
  }
}

migrate();
