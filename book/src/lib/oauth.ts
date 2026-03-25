/**
 * OAuth 2.1 / PKCE utility library
 *
 * Implements the Authorization Code + PKCE flow for the book SPA
 * against the Physical AI auth server (Better Auth + oidcProvider).
 *
 * Tokens are stored in localStorage:
 *   physical_ai_access_token   — short-lived (6h), sent as Bearer
 *   physical_ai_refresh_token  — long-lived (7d), used to renew access token
 *
 * PKCE code_verifier is stored in sessionStorage (cleared after exchange):
 *   pkce_code_verifier
 */

// ─── Constants ───────────────────────────────────────────────────────────────

export const ACCESS_TOKEN_KEY = "physical_ai_access_token";
export const REFRESH_TOKEN_KEY = "physical_ai_refresh_token";
export const PKCE_VERIFIER_KEY = "pkce_code_verifier";

// ─── PKCE helpers ────────────────────────────────────────────────────────────

function base64UrlEncode(buffer: ArrayBuffer | Uint8Array): string {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let str = "";
  for (let i = 0; i < bytes.length; i++) str += String.fromCharCode(bytes[i]);
  return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

export function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return base64UrlEncode(array);
}

export async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoded = new TextEncoder().encode(verifier);
  const hash = await crypto.subtle.digest("SHA-256", encoded);
  return base64UrlEncode(new Uint8Array(hash));
}

// ─── Authorization URL ───────────────────────────────────────────────────────

export interface AuthorizationUrlOptions {
  authServerUrl: string;
  clientId: string;
  redirectUri: string;
  scope?: string;
  /** Optional: extra params to forward (e.g. from an incoming OAuth relay) */
  extraParams?: Record<string, string>;
}

/**
 * Build the OAuth authorization URL with PKCE params.
 * Stores the code_verifier in sessionStorage for later exchange.
 * Returns both the URL and the state nonce for CSRF protection.
 */
export async function buildAuthorizationUrl(
  opts: AuthorizationUrlOptions
): Promise<{ url: string; state: string }> {
  const state = base64UrlEncode(crypto.getRandomValues(new Uint8Array(16)));
  const verifier = generateCodeVerifier();
  const challenge = await generateCodeChallenge(verifier);

  sessionStorage.setItem(PKCE_VERIFIER_KEY, verifier);
  sessionStorage.setItem("oauth_state", state);

  const params = new URLSearchParams({
    client_id: opts.clientId,
    redirect_uri: opts.redirectUri,
    response_type: "code",
    scope: opts.scope ?? "openid profile email",
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
    ...opts.extraParams,
  });

  return {
    url: `${opts.authServerUrl}/api/auth/oauth2/authorize?${params.toString()}`,
    state,
  };
}

// ─── Token exchange ───────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
  id_token?: string;
}

/**
 * Exchange an authorization code for tokens (PKCE — no client_secret).
 */
export async function exchangeCodeForTokens(
  authServerUrl: string,
  clientId: string,
  redirectUri: string,
  code: string,
  codeVerifier: string
): Promise<TokenResponse> {
  const resp = await fetch(`${authServerUrl}/api/auth/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: redirectUri,
      client_id: clientId,
      code_verifier: codeVerifier,
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.error_description ?? err.error ?? "Token exchange failed");
  }

  return resp.json();
}

/**
 * Use the refresh token to obtain a new access token.
 */
export async function refreshAccessToken(
  authServerUrl: string,
  clientId: string,
  refreshToken: string
): Promise<TokenResponse> {
  const resp = await fetch(`${authServerUrl}/api/auth/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: refreshToken,
      client_id: clientId,
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.error_description ?? err.error ?? "Token refresh failed");
  }

  return resp.json();
}

// ─── UserInfo ─────────────────────────────────────────────────────────────────

export interface OAuthUserInfo {
  sub: string;
  email: string;
  name?: string;
  picture?: string;
  role?: string;
  onboardingCompleted?: boolean;
  email_verified?: boolean;
}

/**
 * Fetch the authenticated user's info from the OIDC userinfo endpoint.
 */
export async function getUserInfo(
  authServerUrl: string,
  accessToken: string
): Promise<OAuthUserInfo> {
  const resp = await fetch(`${authServerUrl}/api/auth/oauth2/userinfo`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!resp.ok) {
    throw new Error("UserInfo request failed — token may be expired");
  }

  return resp.json();
}

// ─── Token storage helpers ───────────────────────────────────────────────────

export function storeTokens(tokens: TokenResponse): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  if (tokens.refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  }
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

// ─── State validation ─────────────────────────────────────────────────────────

export function validateState(returnedState: string): boolean {
  const storedState = sessionStorage.getItem("oauth_state");
  sessionStorage.removeItem("oauth_state");
  return !!storedState && storedState === returnedState;
}
