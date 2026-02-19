-- Schema creation for Better Auth with custom fields

-- Create Better Auth core tables (matching auth-server schema)
CREATE TABLE IF NOT EXISTS "user" (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    "emailVerified" BOOLEAN NOT NULL DEFAULT false,
    image TEXT,
    role TEXT DEFAULT 'student',
    "onboardingCompleted" BOOLEAN DEFAULT false,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "session" (
    id TEXT PRIMARY KEY,
    "expiresAt" TIMESTAMP NOT NULL,
    token TEXT NOT NULL UNIQUE,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

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
);

CREATE TABLE IF NOT EXISTS "verification" (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    value TEXT NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

-- Custom user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT UNIQUE NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    software_background TEXT NOT NULL DEFAULT 'none',
    hardware_background TEXT NOT NULL DEFAULT 'none',
    robotics_knowledge TEXT NOT NULL DEFAULT 'none'
      CHECK (robotics_knowledge IN ('none', 'beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Remove CHECK constraints on background fields to allow free-text
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name LIKE '%software_background%'
        AND table_name = 'user_profiles'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS
            (SELECT constraint_name FROM information_schema.table_constraints
             WHERE constraint_name LIKE '%software_background%'
             AND table_name = 'user_profiles' LIMIT 1);
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name LIKE '%hardware_background%'
        AND table_name = 'user_profiles'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS
            (SELECT constraint_name FROM information_schema.table_constraints
             WHERE constraint_name LIKE '%hardware_background%'
             AND table_name = 'user_profiles' LIMIT 1);
    END IF;
END $$;

-- Update user_profiles to allow free-text backgrounds
ALTER TABLE user_profiles ALTER COLUMN software_background SET DEFAULT 'none';
ALTER TABLE user_profiles ALTER COLUMN hardware_background SET DEFAULT 'none';

--DOWN--
-- Rollback Auth tables (be careful in production - this deletes user data)
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS "session";
DROP TABLE IF EXISTS "user";