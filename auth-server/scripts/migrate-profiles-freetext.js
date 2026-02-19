/**
 * Migrate user_profiles to allow free-text backgrounds.
 *
 * - Drops CHECK constraints on software_background and hardware_background
 * - Keeps robotics_knowledge as enum (none/beginner/intermediate/advanced)
 *
 * Run: node scripts/migrate-profiles-freetext.js
 */

import pkg from "pg";
const { Pool } = pkg;
import dotenv from "dotenv";

dotenv.config();

const pool = new Pool({
  connectionString: process.env.NEON_DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

async function migrate() {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    // Drop existing CHECK constraints on software_background and hardware_background
    const constraints = await client.query(`
      SELECT conname FROM pg_constraint
      WHERE conrelid = 'user_profiles'::regclass
        AND contype = 'c'
        AND (conname LIKE '%software%' OR conname LIKE '%hardware%')
    `);

    for (const row of constraints.rows) {
      await client.query(
        `ALTER TABLE user_profiles DROP CONSTRAINT "${row.conname}"`
      );
      console.log(`Dropped constraint: ${row.conname}`);
    }

    // Change column types to TEXT without length limit
    await client.query(`
      ALTER TABLE user_profiles
        ALTER COLUMN software_background TYPE TEXT,
        ALTER COLUMN hardware_background TYPE TEXT
    `);

    await client.query("COMMIT");
    console.log("Migration complete: backgrounds now accept free text.");
  } catch (error) {
    await client.query("ROLLBACK");
    console.error("Migration failed:", error);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

migrate();
