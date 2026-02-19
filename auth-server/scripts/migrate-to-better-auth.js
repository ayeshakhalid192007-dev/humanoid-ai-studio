/**
 * Migrate existing custom auth users to Better Auth tables.
 *
 * Reads from auth_users/auth_sessions and inserts into
 * Better Auth's user/account/session tables.
 *
 * Run: node scripts/migrate-to-better-auth.js
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
    // Check if auth_users table exists
    const tableCheck = await client.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_name = 'auth_users'
      )
    `);

    if (!tableCheck.rows[0].exists) {
      console.log("No auth_users table found. Nothing to migrate.");
      return;
    }

    // Read existing users
    const users = await client.query("SELECT * FROM auth_users");
    console.log(`Found ${users.rows.length} users to migrate.`);

    if (users.rows.length === 0) {
      console.log("No users to migrate.");
      return;
    }

    await client.query("BEGIN");

    for (const user of users.rows) {
      // Insert into Better Auth's "user" table
      await client.query(
        `INSERT INTO "user" (id, name, email, "emailVerified", role, "onboardingCompleted", "createdAt", "updatedAt")
         VALUES ($1, $2, $3, $4, $5, false, $6, $7)
         ON CONFLICT (id) DO NOTHING`,
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

      // Insert into "account" table (credential provider)
      const accountId = `acct_${user.id}`;
      await client.query(
        `INSERT INTO account (id, "userId", "accountId", "providerId", password, "createdAt", "updatedAt")
         VALUES ($1, $2, $3, 'credential', $4, $5, $6)
         ON CONFLICT DO NOTHING`,
        [
          accountId,
          user.id,
          user.id,
          user.password_hash,
          user.created_at || new Date(),
          user.updated_at || new Date(),
        ]
      );

      // Create default user_profiles entry
      await client.query(
        `INSERT INTO user_profiles (user_id, software_background, hardware_background, robotics_knowledge)
         VALUES ($1, 'none', 'none', 'none')
         ON CONFLICT (user_id) DO NOTHING`,
        [user.id]
      );

      console.log(`  Migrated user: ${user.email}`);
    }

    await client.query("COMMIT");
    console.log(`\nMigration complete. ${users.rows.length} users migrated.`);

    // Verify
    const verifyUsers = await client.query('SELECT count(*) FROM "user"');
    const verifyAccounts = await client.query("SELECT count(*) FROM account");
    const verifyProfiles = await client.query(
      "SELECT count(*) FROM user_profiles"
    );
    console.log(`\nVerification:`);
    console.log(`  Users: ${verifyUsers.rows[0].count}`);
    console.log(`  Accounts: ${verifyAccounts.rows[0].count}`);
    console.log(`  Profiles: ${verifyProfiles.rows[0].count}`);
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
