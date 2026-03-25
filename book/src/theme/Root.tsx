/**
 * Root theme component - wraps entire Docusaurus site
 *
 * Provides:
 * - AuthProvider for authentication state (SSR-safe)
 * - RouteGuard for auth-based route protection (client-only)
 * - ChatbotWidget on all pages (client-only)
 *
 * Route Protection Rules:
 * - Protected routes: /dashboard, /auth/onboarding, /profile, /notes, /progress, /enroll
 * - Auth routes: /auth/login, /auth/signup (redirect to /dashboard if authenticated)
 * - Public: everything else
 */
import React, { useEffect, Suspense } from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";
import { AuthProvider } from "../context/AuthContext";
import ChatbotWidget from "../components/ChatbotWidget/FuturisticChatbotWidget";

const PROTECTED_ROUTES = ["/dashboard", "/auth/onboarding", "/profile", "/notes", "/progress", "/enroll"];
const AUTH_ROUTES = ["/auth/login", "/auth/signup"];

/**
 * RouteGuard — client-only component that enforces auth redirects.
 * Hooks are called at the top level of this component — no violations.
 */
function ClientRouteGuard({ children }: { children: React.ReactNode }) {
  const { useHistory, useLocation } =
    require("@docusaurus/router") as typeof import("@docusaurus/router");
  const { useAuth } =
    require("../context/AuthContext") as typeof import("../context/AuthContext");

  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();
  const location = useLocation();

  useEffect(() => {
    if (isLoading) return;

    const path = location.pathname;

    if (isAuthenticated && AUTH_ROUTES.some((r) => path.startsWith(r))) {
      history.replace("/dashboard");
      return;
    }

    const isProtected = PROTECTED_ROUTES.some((r) => path.startsWith(r));
    if (!isAuthenticated && isProtected) {
      sessionStorage.setItem("auth_redirect", path);
      history.replace("/auth/login");
    }
  }, [isAuthenticated, isLoading, location.pathname, history]);

  return <>{children}</>;
}

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <AuthProvider>
      {/* Render children immediately — no mount spinner blocking the page */}
      {children}

      {/* ChatbotWidget is client-only */}
      <BrowserOnly fallback={<></>}>
        {() => (
          <>
            <ClientRouteGuard>{null}</ClientRouteGuard>
            <Suspense fallback={null}>
              <ChatbotWidget />
            </Suspense>
          </>
        )}
      </BrowserOnly>
    </AuthProvider>
  );
}
