#!/usr/bin/env python3
"""
Login Bug Detector — Static analysis for Better Auth / OAuth PKCE login issues.

Scans the project for the most common configuration bugs that prevent
successful login when using Better Auth with an OIDC/OAuth2 PKCE flow.

Usage:
    python3 detect_login_bugs.py [project_root]

    Defaults to current directory if project_root is not supplied.
"""

import re
import sys
import os
from pathlib import Path

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

findings = []


def check(label: str, passed: bool, detail: str, fix: str = ""):
    status = PASS if passed else FAIL
    findings.append((status, label, detail, fix))


def warn(label: str, detail: str, fix: str = ""):
    findings.append((WARN, label, detail, fix))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def find_file(root: Path, *patterns) -> Path | None:
    for pattern in patterns:
        matches = list(root.rglob(pattern))
        # Exclude node_modules, venv, .git
        matches = [m for m in matches if not any(
            part in m.parts for part in ("node_modules", "venv", ".git", "__pycache__")
        )]
        if matches:
            return matches[0]
    return None


def scan(root: Path):
    print(f"\n🔍 Scanning: {root}\n")

    # ── 1. Locate key files ──────────────────────────────────────────────────
    auth_js      = find_file(root, "auth.js", "auth.ts")
    docusaurus_cfg = find_file(root, "docusaurus.config.js", "docusaurus.config.ts")
    auth_context = find_file(root, "AuthContext.tsx", "AuthContext.ts")
    env_file     = find_file(root, ".env")
    oauth_lib    = find_file(root, "oauth.ts", "oauth.js")

    # ── 2. auth.js / auth.ts checks ─────────────────────────────────────────
    if auth_js:
        src = read(auth_js)

        # loginPage must be a full URL, not a relative path
        login_page_match = re.search(r'loginPage\s*:\s*["`\']([^"`\']+)["`\']', src)
        if login_page_match:
            lp = login_page_match.group(1)
            is_full_url = lp.startswith("http") or lp.startswith("${")
            check(
                "loginPage is a full URL",
                is_full_url,
                f"loginPage = '{lp}' in {auth_js.name}",
                "Change to: loginPage: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/login`"
            )
        else:
            warn("loginPage not found", f"Could not find loginPage in {auth_js}")

        # bearer() plugin present
        check(
            "bearer() plugin included",
            "bearer()" in src,
            f"Checked {auth_js.name}",
            "Add bearer() to the plugins array in auth.js"
        )

        # BETTER_AUTH_URL used
        check(
            "BETTER_AUTH_URL configured",
            "BETTER_AUTH_URL" in src or "baseURL" in src,
            f"Checked {auth_js.name}",
            "Set baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3002'"
        )

        # BETTER_AUTH_SECRET used
        check(
            "BETTER_AUTH_SECRET referenced",
            "BETTER_AUTH_SECRET" in src,
            f"Checked {auth_js.name}",
            "Add: secret: process.env.BETTER_AUTH_SECRET"
        )

        # trustedOrigins present
        check(
            "trustedOrigins configured",
            "trustedOrigins" in src,
            f"Checked {auth_js.name}",
            "Add trustedOrigins array with frontend origin"
        )

        # Password hash + verify must both be defined (custom PBKDF2)
        has_hash   = "hash:" in src or "hash :" in src
        has_verify = "verify:" in src or "verify :" in src
        check(
            "Custom password hash AND verify both defined",
            has_hash == has_verify,  # both present or both absent
            f"hash={'yes' if has_hash else 'no'}, verify={'yes' if has_verify else 'no'} in {auth_js.name}",
            "Ensure hash and verify functions use the same algorithm (both PBKDF2 or both bcrypt)"
        )

    else:
        warn("auth.js/ts not found", "Could not locate Better Auth config file")

    # ── 3. Docusaurus config checks ──────────────────────────────────────────
    if docusaurus_cfg:
        src = read(docusaurus_cfg)

        # baseUrl should be env-configurable, not hardcoded
        hardcoded_base = re.search(r"baseUrl\s*:\s*['\"][^'/][^'\"]+['\"]", src)
        check(
            "baseUrl is env-configurable (not hardcoded)",
            not hardcoded_base,
            f"Checked {docusaurus_cfg.name}",
            "Change to: baseUrl: process.env.BASE_URL || '/'"
        )

        # oauthRedirectUri present in customFields
        check(
            "oauthRedirectUri in customFields",
            "oauthRedirectUri" in src,
            f"Checked {docusaurus_cfg.name}",
            "Add oauthRedirectUri: process.env.OAUTH_REDIRECT_URI || 'http://localhost:3000/auth/callback'"
        )

        # authApiUrl present
        check(
            "authApiUrl in customFields",
            "authApiUrl" in src,
            f"Checked {docusaurus_cfg.name}",
            "Add authApiUrl: process.env.AUTH_API_URL || 'http://localhost:3002'"
        )

    else:
        warn("docusaurus.config.js not found", "Could not locate Docusaurus config")

    # ── 4. AuthContext checks ────────────────────────────────────────────────
    if auth_context:
        src = read(auth_context)

        # credentials: "include" for cookie auth
        check(
            "credentials: 'include' used in fetches",
            'credentials: "include"' in src or "credentials: 'include'" in src,
            f"Checked {auth_context.name}",
            "Add credentials: 'include' to cross-origin fetch calls to the auth server"
        )

        # handleOAuthCallback present
        check(
            "handleOAuthCallback implemented",
            "handleOAuthCallback" in src,
            f"Checked {auth_context.name}",
            "Implement handleOAuthCallback to exchange auth code for tokens"
        )

        # refreshSession or token refresh logic
        check(
            "Token refresh logic present",
            "refreshToken" in src or "refresh_token" in src,
            f"Checked {auth_context.name}",
            "Implement refresh token logic to renew access tokens before expiry"
        )

    else:
        warn("AuthContext not found", "Could not locate auth context file")

    # ── 5. oauth.ts / oauth.js checks ───────────────────────────────────────
    if oauth_lib:
        src = read(oauth_lib)

        # PKCE: code_verifier stored in sessionStorage
        check(
            "PKCE code_verifier stored in sessionStorage",
            "sessionStorage" in src and ("verifier" in src or "code_verifier" in src),
            f"Checked {oauth_lib.name}",
            "Store PKCE code_verifier in sessionStorage before the OAuth redirect"
        )

        # state stored before redirect
        check(
            "OAuth state stored before redirect",
            "sessionStorage.setItem" in src and "state" in src,
            f"Checked {oauth_lib.name}",
            "Store state nonce in sessionStorage BEFORE redirecting to the auth server"
        )

        # validateState present
        check(
            "validateState() implemented for CSRF protection",
            "validateState" in src,
            f"Checked {oauth_lib.name}",
            "Implement validateState() to compare returned state with stored nonce"
        )

    else:
        warn("oauth.ts/js not found", "Could not locate PKCE OAuth utility file")

    # ── 6. .env checks ───────────────────────────────────────────────────────
    if env_file:
        src = read(env_file)

        check(
            "BETTER_AUTH_SECRET set in .env",
            "BETTER_AUTH_SECRET" in src and not re.search(r"BETTER_AUTH_SECRET\s*=\s*$", src),
            f"Checked {env_file}",
            "Generate: openssl rand -hex 32"
        )

        check(
            "BETTER_AUTH_URL set in .env",
            "BETTER_AUTH_URL" in src,
            f"Checked {env_file}",
            "Add BETTER_AUTH_URL=http://localhost:3002"
        )

        # Secret length check (must be 32+ chars)
        secret_match = re.search(r"BETTER_AUTH_SECRET\s*=\s*(\S+)", src)
        if secret_match:
            secret_val = secret_match.group(1)
            check(
                "BETTER_AUTH_SECRET is at least 32 characters",
                len(secret_val) >= 32,
                f"Secret length: {len(secret_val)} chars",
                "Generate a longer secret: openssl rand -hex 32"
            )

    else:
        warn(".env not found", "Could not locate auth server .env file")

    # ── Print report ─────────────────────────────────────────────────────────
    passes  = sum(1 for f in findings if f[0] == PASS)
    fails   = sum(1 for f in findings if f[0] == FAIL)
    warns   = sum(1 for f in findings if f[0] == WARN)

    print(f"{'─'*60}")
    print(f" Login Bug Detector — Results")
    print(f"{'─'*60}")

    for status, label, detail, fix in findings:
        print(f"\n{status} {label}")
        print(f"   {detail}")
        if fix and status == FAIL:
            print(f"   💡 Fix: {fix}")

    print(f"\n{'─'*60}")
    print(f" Summary: {passes} passed  |  {fails} failed  |  {warns} warnings")
    print(f"{'─'*60}\n")

    if fails:
        print("⚠️  Bugs detected — see ❌ items above for fixes.\n")
        sys.exit(1)
    else:
        print("🎉 No login bugs detected!\n")


if __name__ == "__main__":
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    scan(project_root)
