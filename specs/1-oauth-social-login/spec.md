# Feature Specification: OAuth Social Login (Google & GitHub)

**Feature Branch**: `feature/oauth-google-github`
**Created**: 2026-03-24
**Status**: Implemented
**Input**: User description: "Add Google OAuth and GitHub OAuth login/signup to existing email/password auth using OAuth 2.0"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Signs Up with Google (Priority: P1)

A new visitor to the platform clicks "Continue with Google" on the signup page, is redirected to Google's authorization page, grants permission, and returns to the platform as a fully registered user — without needing to fill in a name, email, or password.

**Why this priority**: Social signup dramatically reduces registration friction. It is the primary new-user onboarding path this feature enables and delivers standalone value immediately.

**Independent Test**: Can be fully tested by clicking "Continue with Google" on /auth/signup and completing Google's consent screen, which results in a logged-in user on the dashboard.

**Acceptance Scenarios**:

1. **Given** a visitor who has never registered, **When** they click "Continue with Google" and complete Google's consent, **Then** a new user account is created (matched by Google-provided email), the provider "google" and Google user ID are stored, and the user lands on /dashboard as authenticated.
2. **Given** the same new user revisits and clicks "Continue with Google" again, **Then** no duplicate account is created — the existing account is found by email and the user is logged in.
3. **Given** Google's authorization is denied by the user, **Then** the user is returned to the signup page with a clear, non-technical message that sign-in was cancelled.

---

### User Story 2 - New User Signs Up with GitHub (Priority: P1)

A developer clicks "Continue with GitHub" on the signup or login page, authorizes the app on GitHub, and arrives on the platform as a registered user.

**Why this priority**: GitHub OAuth is as critical as Google for the developer audience of this robotics/AI education platform.

**Independent Test**: Can be fully tested by clicking "Continue with GitHub" on /auth/signup and completing GitHub's authorization screen, resulting in a logged-in user.

**Acceptance Scenarios**:

1. **Given** a new visitor, **When** they click "Continue with GitHub" and authorize the app, **Then** a new account is created using GitHub's email, with provider "github" and GitHub user ID stored.
2. **Given** the GitHub account shares an email with an existing email/password account, **Then** the OAuth login is linked to the existing account rather than creating a duplicate.
3. **Given** GitHub authorization is denied or cancelled, **Then** the user returns to the login/signup page with a clear cancellation message.

---

### User Story 3 - Existing User Logs In with Social Provider (Priority: P2)

A user who previously signed up via Google or GitHub returns to the platform and clicks the same social login button to authenticate — without entering any password.

**Why this priority**: Returning social login users must be able to sign back in seamlessly. Without this, the signup flow is useless for retention.

**Independent Test**: Can be tested by signing up via Google/GitHub in one session, then signing out and clicking the same provider button again — user should land on /dashboard.

**Acceptance Scenarios**:

1. **Given** a returning user who originally signed up with Google, **When** they click "Continue with Google", **Then** they are authenticated and redirected to /dashboard without any signup or onboarding steps.
2. **Given** a user signed up with GitHub, **When** they click "Continue with GitHub", **Then** they land on /dashboard authenticated.

---

### User Story 4 - Existing Email/Password User Continues to Work (Priority: P1)

A user who registered with email and password can still log in and use the platform exactly as before — the social login addition does not break or change the existing flow.

**Why this priority**: Zero regression on the existing auth flow is a hard requirement. Breaking existing users would be a critical failure.

**Independent Test**: Can be tested independently by attempting email/password login after OAuth changes are deployed — success means no regression.

**Acceptance Scenarios**:

1. **Given** an existing email/password user, **When** they visit /auth/login and submit their credentials, **Then** they are authenticated and land on /dashboard exactly as before.
2. **Given** the email/password signup form is open, **When** filled and submitted, **Then** the account is created exactly as before, with no changes to existing behavior.

---

### User Story 5 - User Onboarding After Social Signup (Priority: P2)

After signing up for the first time via a social provider, the user is prompted to complete the robotics background onboarding survey — the same onboarding flow existing email/password new users experience.

**Why this priority**: Social signup users arrive without a profile. Without onboarding, the personalization system cannot generate relevant content.

**Independent Test**: Can be tested by completing Google/GitHub signup for the first time and verifying the /auth/onboarding redirect.

**Acceptance Scenarios**:

1. **Given** a brand-new social signup, **When** authentication completes, **Then** the user is redirected to /auth/onboarding before accessing /dashboard.
2. **Given** a returning social login user (already onboarded), **When** they authenticate, **Then** they go directly to /dashboard — onboarding is not shown again.

---

### Edge Cases

- What happens when the provider returns an email that already exists in a different provider's account? → System silently auto-links to the existing account (no user confirmation required), then stores the new provider association. Provider email claims are treated as trusted proof of ownership.
- What happens when the provider does not return an email (e.g., GitHub with private email)? → Display a user-friendly error: "We couldn't retrieve your email from [Provider]. Please use email/password signup or make your GitHub email public."
- What happens when the OAuth callback URL is tampered with or the state parameter is invalid? → Reject the callback with a security error and redirect to /auth/login with an error message.
- What happens if the provider's OAuth service is temporarily unavailable? → Display a friendly fallback message and offer the email/password alternative.
- What happens when a user tries to sign up with a social provider using an email that is already associated with the same provider? → Log them in (no duplicate account created).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display "Continue with Google" and "Continue with GitHub" buttons on both /auth/login and /auth/signup pages, visually consistent with the existing UI style.
- **FR-002**: System MUST initiate Google and GitHub OAuth flows by calling Better Auth's server-side social sign-in endpoint. Better Auth handles all provider OAuth exchange (PKCE, state, code exchange) internally — the frontend does NOT construct provider authorization URLs manually.
- **FR-003**: Better Auth MUST handle OAuth callback routes for Google and GitHub on the auth server (`/api/auth/callback/google`, `/api/auth/callback/github`). After successful provider exchange, Better Auth redirects to the platform's OIDC authorize endpoint (`/api/auth/oauth2/authorize?...`) which validates the active session and issues a platform authorization code; the browser is then redirected to the frontend `/auth/callback` page to complete the PKCE token exchange. The full redirect chain is: Provider → `/api/auth/callback/:provider` → `/api/auth/oauth2/authorize` → `/auth/callback`.
- **FR-004**: System MUST create a new user record on first-time social login, populating: email (from provider), display name (provider `name` field; fallback to `login`/username if name is null), and profile picture (provider avatar URL stored in the `image` field).
- **FR-005**: System MUST silently auto-link incoming social logins to existing accounts when the provider-verified email matches an existing user record — no password confirmation or manual action required from the user. The provider's email claim is treated as trusted proof of ownership.
- **FR-006**: System MUST store the OAuth provider name ("google" or "github") and the provider's user ID for each social login, in the existing `account` table (which already has `providerId`, `accountId` fields).
- **FR-007**: System MUST issue the platform's standard access token and refresh token after successful social authentication, so the rest of the application behaves identically regardless of auth method.
- **FR-008**: System MUST redirect first-time social signup users to the onboarding flow (/auth/onboarding) before granting dashboard access.
- **FR-009**: System MUST preserve all existing email/password signup and login functionality without modification or regression.
- **FR-010**: System MUST read all OAuth client IDs, client secrets, and redirect URIs from environment variables — no secrets hardcoded in source.
- **FR-011**: System MUST add placeholder entries for all new OAuth environment variables to `.env.example` files.
- **FR-012**: System MUST display a clear, user-friendly error message when OAuth authorization is cancelled, denied, or fails.

### Key Entities

- **User**: Represents a registered platform user. Key attributes: id, name, email, emailVerified, image (profile picture URL), role, onboardingCompleted. On social signup: name populated from provider (GitHub login used as fallback), image populated from provider avatar URL.
- **Account (OAuth link)**: Represents an OAuth identity linked to a User. Key attributes: userId (FK), providerId (e.g., "google", "github"), accountId (provider's user ID), accessToken, refreshToken, expiresAt. This entity already exists in the schema.
- **OAuth Provider Configuration**: The Google and GitHub app credentials (client ID, client secret, redirect URI) stored in environment variables, consumed by the auth server.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can complete social signup (Google or GitHub) and reach the onboarding page in under 60 seconds from first clicking the provider button.
- **SC-002**: 100% of existing email/password login and signup test scenarios continue to pass after the feature is deployed — zero regression.
- **SC-003**: A user with an existing email/password account can log in via a matching social provider without a duplicate account being created — verified by checking user count before and after.
- **SC-004**: All OAuth client credentials are sourced exclusively from environment variables — no secrets appear in any committed source file (verifiable by scanning committed files).
- **SC-005**: Social login buttons are visible and functional on both the login and signup pages across desktop and mobile viewport sizes.
- **SC-006**: The onboarding redirect works for first-time social signups, and returning social logins bypass onboarding — both verifiable by navigating the flows end-to-end.

## Assumptions

- Better Auth (v1.2.0) supports adding Google and GitHub as social providers via its built-in plugin system without requiring a schema migration (the `account` table already stores provider information).
- Better Auth handles all provider-side OAuth exchange (PKCE, state, code exchange) server-side. The frontend social login buttons call Better Auth's social sign-in API (`POST /api/auth/sign-in/social`) passing a `callbackURL` that is a fresh PKCE OIDC authorize URL built using the existing `oauth.ts` `buildAuthorizationUrl` utility. This authorize URL acts as a relay: after Better Auth completes the provider exchange and establishes a session, the browser is sent to the OIDC authorize endpoint which issues a platform code and redirects to the frontend `/auth/callback` page. The `oauth.ts` PKCE utilities are used for the platform's OIDC relay URL — not for constructing the provider (Google/GitHub) authorization URLs, which Better Auth handles internally.
- Google and GitHub OAuth apps will be registered by the developer in their respective developer consoles; this spec covers the platform-side integration only.
- The platform treats email as the canonical identity key; if two providers return the same email, they are considered the same person.
- GitHub users with private emails who cannot share an email address are an out-of-scope edge case for MVP; they will receive an error message and be directed to use email/password signup.
- No changes to the Neon database schema are required for MVP — the existing `account` table schema is sufficient to store social provider associations.

## Clarifications

### Session 2026-03-24

- Q: When an email from a social provider matches an existing email/password account — should the system auto-link silently or require password confirmation? → A: Silent auto-link (Option A). Provider email claims from Google and GitHub are trusted as proof of ownership; no user confirmation required.
- Q: What profile data from the provider should be stored on the new user record? → A: All available (Option A) — name (with username/login as fallback), email, and profile picture URL stored in the `image` field.
- Q: Should social login use Better Auth server-side OAuth or the existing frontend PKCE pattern? → A: Better Auth server-side (Option A). Frontend triggers sign-in via Better Auth API; Better Auth handles all provider OAuth exchange internally and redirects back to `/auth/callback` with a platform session.

## Out of Scope

- Adding additional OAuth providers beyond Google and GitHub (e.g., Twitter/X, LinkedIn, Apple).
- "Account linking" UI within user settings (linking a second provider to an existing account via a settings page).
- Migrating existing email/password users to social login automatically.
- OAuth for the FastAPI backend directly — the backend continues to validate tokens through the existing auth server OIDC endpoint.
