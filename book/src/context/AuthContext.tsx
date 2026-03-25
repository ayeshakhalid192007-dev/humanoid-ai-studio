/**
 * Authentication Context — OAuth 2.1 / PKCE
 *
 * Uses the Physical AI auth server as an OIDC provider.
 * Tokens (access + refresh) are stored in localStorage.
 * Sessions are validated via the /api/auth/oauth2/userinfo endpoint.
 *
 * Backwards-compatible API surface: all existing consumers of useAuth()
 * continue to work without changes.
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import {
  buildAuthorizationUrl,
  exchangeCodeForTokens,
  refreshAccessToken,
  getUserInfo,
  storeTokens,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  validateState,
  PKCE_VERIFIER_KEY,
  type OAuthUserInfo,
} from "../lib/oauth";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  role: string;
  emailVerified: boolean;
  onboardingCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: string;
}

export interface UserProfile {
  softwareBackground: string;
  hardwareBackground: string;
  roboticsKnowledge: string;
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  needsOnboarding: boolean;
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signUp: (email: string, password: string, name: string) => Promise<{ success: boolean; error?: string }>;
  signUpWithProfile: (
    email: string,
    password: string,
    name: string,
    profile: UserProfile
  ) => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
  saveProfile: (profile: UserProfile) => Promise<{ success: boolean; error?: string }>;
  fetchProfile: () => Promise<void>;
  /** Called by /auth/callback page after the auth server redirects back */
  handleOAuthCallback: (code: string, state: string) => Promise<{ success: boolean; error?: string }>;
  /** Initiates social OAuth sign-in via Google or GitHub */
  signInWithSocial: (provider: 'google' | 'github') => Promise<void>;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ─── Helpers ──────────────────────────────────────────────────────────────────

function mapUserInfoToUser(info: OAuthUserInfo): User {
  return {
    id: info.sub,
    email: info.email,
    name: info.name ?? null,
    image: info.picture ?? null,
    role: info.role ?? "student",
    emailVerified: info.email_verified ?? false,
    onboardingCompleted: info.onboardingCompleted ?? false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const { siteConfig } = useDocusaurusContext();
  const AUTH_API_URL =
    (siteConfig.customFields?.authApiUrl as string) || "http://localhost:3002";
  const CLIENT_ID =
    (siteConfig.customFields?.oauthClientId as string) || "physical-ai-book";
  const REDIRECT_URI =
    (siteConfig.customFields?.oauthRedirectUri as string) ||
    "http://localhost:3000/auth/callback";

  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;
  const needsOnboarding = isAuthenticated && !user.onboardingCompleted;

  // ── Refresh session from stored access token ──────────────────────────────

  const refreshSession = useCallback(async () => {
    setError(null);
    const accessToken = getAccessToken();

    if (!accessToken) {
      // Try refreshing with the refresh token before giving up
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const tokens = await refreshAccessToken(AUTH_API_URL, CLIENT_ID, refreshToken);
          storeTokens(tokens);
          const info = await getUserInfo(AUTH_API_URL, tokens.access_token);
          setUser(mapUserInfoToUser(info));
          // Synthetic session object for backwards compat
          setSession({ id: tokens.access_token, userId: info.sub, token: tokens.access_token, expiresAt: "" });
        } catch {
          clearTokens();
          setUser(null);
          setSession(null);
        }
      } else {
        setUser(null);
        setSession(null);
      }
      setIsLoading(false);
      return;
    }

    try {
      const info = await getUserInfo(AUTH_API_URL, accessToken);
      setUser(mapUserInfoToUser(info));
      setSession({ id: accessToken, userId: info.sub, token: accessToken, expiresAt: "" });
    } catch {
      // Access token expired — try refresh
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const tokens = await refreshAccessToken(AUTH_API_URL, CLIENT_ID, refreshToken);
          storeTokens(tokens);
          const info = await getUserInfo(AUTH_API_URL, tokens.access_token);
          setUser(mapUserInfoToUser(info));
          setSession({ id: tokens.access_token, userId: info.sub, token: tokens.access_token, expiresAt: "" });
        } catch {
          clearTokens();
          setUser(null);
          setSession(null);
        }
      } else {
        clearTokens();
        setUser(null);
        setSession(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, [AUTH_API_URL, CLIENT_ID]);

  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  // ── OAuth callback handler ────────────────────────────────────────────────

  const handleOAuthCallback = useCallback(
    async (code: string, state: string): Promise<{ success: boolean; error?: string }> => {
      setIsLoading(true);
      setError(null);
      try {
        if (!validateState(state)) {
          throw new Error("Invalid state parameter — possible CSRF attack.");
        }

        const verifier = sessionStorage.getItem(PKCE_VERIFIER_KEY);
        if (!verifier) {
          throw new Error("PKCE code verifier missing. Please start the login flow again.");
        }
        sessionStorage.removeItem(PKCE_VERIFIER_KEY);

        const tokens = await exchangeCodeForTokens(
          AUTH_API_URL,
          CLIENT_ID,
          REDIRECT_URI,
          code,
          verifier
        );

        storeTokens(tokens);

        const info = await getUserInfo(AUTH_API_URL, tokens.access_token);
        setUser(mapUserInfoToUser(info));
        setSession({ id: tokens.access_token, userId: info.sub, token: tokens.access_token, expiresAt: "" });

        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "OAuth callback failed";
        setError(message);
        return { success: false, error: message };
      } finally {
        setIsLoading(false);
      }
    },
    [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]
  );

  // ── Sign in — initiates OAuth PKCE redirect ───────────────────────────────

  const signIn = useCallback(
    async (_email: string, _password: string): Promise<{ success: boolean; error?: string }> => {
      // OAuth flow: we redirect to the auth server's login page.
      // The auth server authenticates the user and redirects back to REDIRECT_URI.
      try {
        const { url } = await buildAuthorizationUrl({
          authServerUrl: AUTH_API_URL,
          clientId: CLIENT_ID,
          redirectUri: REDIRECT_URI,
        });
        window.location.href = url;
        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to start sign-in";
        setError(message);
        return { success: false, error: message };
      }
    },
    [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]
  );

  // ── Sign up — creates account, then initiates OAuth redirect ─────────────

  const signUp = useCallback(
    async (
      email: string,
      password: string,
      name: string
    ): Promise<{ success: boolean; error?: string }> => {
      setIsLoading(true);
      setError(null);
      try {
        const resp = await fetch(`${AUTH_API_URL}/api/auth/sign-up/email`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name }),
        });

        const data = await resp.json();

        if (!resp.ok) {
          const msg = data.message ?? data.error ?? "Sign up failed";
          setError(msg);
          return { success: false, error: msg };
        }

        // Account created — now start OAuth flow to get tokens
        const { url } = await buildAuthorizationUrl({
          authServerUrl: AUTH_API_URL,
          clientId: CLIENT_ID,
          redirectUri: REDIRECT_URI,
        });
        window.location.href = url;
        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Sign up failed";
        setError(message);
        return { success: false, error: message };
      } finally {
        setIsLoading(false);
      }
    },
    [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]
  );

  // ── Sign up with profile ──────────────────────────────────────────────────

  const signUpWithProfile = useCallback(
    async (
      email: string,
      password: string,
      name: string,
      profileData: UserProfile
    ): Promise<{ success: boolean; error?: string }> => {
      setIsLoading(true);
      setError(null);
      try {
        // Step 1: create account
        const resp = await fetch(`${AUTH_API_URL}/api/auth/sign-up/email`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name }),
        });

        const data = await resp.json();

        if (!resp.ok) {
          const msg = data.message ?? data.error ?? "Sign up failed";
          setError(msg);
          return { success: false, error: msg };
        }

        // Better Auth returns a session token on sign-up — use it as Bearer for
        // the profile call so it works cross-origin (GitHub Pages → auth server)
        // where third-party cookies are blocked by the browser.
        // Newer Better Auth versions nest the token under session.token.
        const signUpToken: string | null = data.token ?? data.session?.token ?? null;

        // Step 2: save profile using Bearer token (cross-origin safe) + cookie fallback
        const profileResp = await fetch(`${AUTH_API_URL}/api/profile`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            ...(signUpToken ? { Authorization: `Bearer ${signUpToken}` } : {}),
          },
          body: JSON.stringify(profileData),
        });

        if (!profileResp.ok) {
          // Account created but profile failed — user can finish onboarding later
          console.warn("Profile save failed after signup — user can complete onboarding later");
        }

        // Step 3: start OAuth flow to get tokens
        const { url } = await buildAuthorizationUrl({
          authServerUrl: AUTH_API_URL,
          clientId: CLIENT_ID,
          redirectUri: REDIRECT_URI,
        });
        window.location.href = url;
        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Sign up failed";
        setError(message);
        return { success: false, error: message };
      } finally {
        setIsLoading(false);
      }
    },
    [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]
  );

  // ── Sign out ──────────────────────────────────────────────────────────────

  const signOut = useCallback(async (): Promise<void> => {
    // Revoke the server-side session (cookie + token) before clearing local state.
    // Without this the Better Auth session cookie remains active even after the
    // user "logs out", allowing stale cookie-based requests to succeed.
    const accessToken = getAccessToken();
    await fetch(`${AUTH_API_URL}/api/auth/sign-out`, {
      method: "POST",
      credentials: "include",
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
    }).catch(() => {
      // Best-effort: clear local state even if the server call fails
    });

    clearTokens();
    setUser(null);
    setSession(null);
    setProfile(null);
    setError(null);
  }, [AUTH_API_URL]);

  // ── Profile helpers ───────────────────────────────────────────────────────

  const fetchProfile = useCallback(async () => {
    const accessToken = getAccessToken();
    if (!accessToken) return;

    try {
      const resp = await fetch(`${AUTH_API_URL}/api/profile`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.profile) {
          setProfile({
            softwareBackground: data.profile.software_background,
            hardwareBackground: data.profile.hardware_background,
            roboticsKnowledge: data.profile.robotics_knowledge,
          });
        }
      }
    } catch (err) {
      console.error("Fetch profile error:", err);
    }
  }, [AUTH_API_URL]);

  const saveProfile = useCallback(
    async (profileData: UserProfile): Promise<{ success: boolean; error?: string }> => {
      const accessToken = getAccessToken();
      if (!accessToken) {
        return { success: false, error: "Not authenticated" };
      }

      try {
        const resp = await fetch(`${AUTH_API_URL}/api/profile`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(profileData),
        });

        const data = await resp.json();

        if (resp.ok) {
          setProfile(profileData);
          setUser((prev) => prev ? { ...prev, onboardingCompleted: true } : prev);
          return { success: true };
        }

        const msg = data.error ?? "Failed to save profile";
        setError(msg);
        return { success: false, error: msg };
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Network error";
        setError(msg);
        return { success: false, error: msg };
      }
    },
    [AUTH_API_URL]
  );

  // ── Social sign-in — PKCE relay through Better Auth social provider ──────

  const signInWithSocial = useCallback(async (provider: 'google' | 'github') => {
    // Build a fresh PKCE authorize URL (pure local crypto — no network call).
    // After social auth completes, Better Auth redirects to this URL so the
    // OIDC provider can issue a PKCE code and complete the token flow.
    const { url: authorizeUrl } = await buildAuthorizationUrl({
      authServerUrl: AUTH_API_URL,
      clientId: CLIENT_ID,
      redirectUri: REDIRECT_URI,
    });

    // Navigate the browser directly to the auth server's social sign-in endpoint.
    // Using window.location.href (browser navigation) instead of fetch avoids
    // CORS restrictions — XHR/fetch is blocked cross-origin, but browser
    // navigations are not subject to CORS.
    // Better Auth's social sign-in uses provider as a path segment:
    //   GET /api/auth/sign-in/social/:provider?callbackURL=...
    const params = new URLSearchParams({ callbackURL: authorizeUrl });
    window.location.href = `${AUTH_API_URL}/api/auth/sign-in/social/${provider}?${params.toString()}`;
  }, [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]);

  // ─────────────────────────────────────────────────────────────────────────

  const value: AuthContextType = {
    user,
    session,
    profile,
    isLoading,
    error,
    isAuthenticated,
    needsOnboarding,
    signIn,
    signUp,
    signUpWithProfile,
    signOut,
    refreshSession,
    saveProfile,
    fetchProfile,
    handleOAuthCallback,
    signInWithSocial,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
