/**
 * Create user_profiles table in Neon Postgres.
 *
 * Run: node scripts/create-profiles-table.js
 */

import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";

dotenv.config();

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

async function createProfilesTable() {
  const client = await pool.connect();
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS user_profiles (
        id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
        user_id TEXT UNIQUE NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        software_background TEXT NOT NULL DEFAULT 'none'
          CHECK (software_background IN ('none', 'beginner', 'intermediate', 'advanced')),
        hardware_background TEXT NOT NULL DEFAULT 'none'
          CHECK (hardware_background IN ('none', 'beginner', 'intermediate', 'advanced')),
        robotics_knowledge TEXT NOT NULL DEFAULT 'none'
          CHECK (robotics_knowledge IN ('none', 'beginner', 'intermediate', 'advanced')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log("user_profiles table created successfully.");
  } catch (error) {
    console.error("Error creating user_profiles table:", error);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

createProfilesTable();
