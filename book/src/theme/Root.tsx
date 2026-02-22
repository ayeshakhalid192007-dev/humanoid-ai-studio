/**
 * Root theme component - wraps entire Docusaurus site
 *
 * Provides:
 * - AuthProvider for authentication state (SSR-safe)
 * - RouteGuard for auth-based route protection (client-only)
 * - ChatbotWidget on all pages (client-only)
 * - Proper hydration handling to prevent layout shifts
 * - Consistent layout foundation with background management
 *
 * Route Protection Rules:
 * - Protected routes: /dashboard, /auth/onboarding, /profile, /notes, /progress, /enroll (require authentication)
 * - Auth routes: /auth/login, /auth/signup (redirect to /dashboard if authenticated)
 * - Everything else (docs, features, home, etc.) is publicly accessible
 */
import React, { useState, useEffect, Suspense } from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";
import { AuthProvider } from "../context/AuthContext";
import { motion, AnimatePresence } from 'framer-motion';
import ChatbotWidget from "../components/ChatbotWidget/FuturisticChatbotWidget";

/**
 * RouteGuard — client-only component that enforces auth redirects.
 * Imported dynamically inside BrowserOnly to avoid SSR issues with useHistory/useLocation.
 */
function ClientRouteGuard({ children }: { children: React.ReactNode }) {
  // These hooks are only available client-side in Docusaurus
  const { useHistory, useLocation } =
    require("@docusaurus/router") as typeof import("@docusaurus/router");
  const { useAuth } =
    require("../context/AuthContext") as typeof import("../context/AuthContext");

  const { isAuthenticated, isLoading } = useAuth();
  const history = useHistory();
  const location = useLocation();

  const PROTECTED_ROUTES = ["/dashboard", "/auth/onboarding", "/profile", "/notes", "/progress", "/enroll"];
  const AUTH_ROUTES = ["/auth/login", "/auth/signup"];

  useEffect(() => {
    if (isLoading) return;

    const path = location.pathname;

    // Authenticated user on auth pages -> dashboard
    if (isAuthenticated && AUTH_ROUTES.some((r) => path.startsWith(r))) {
      history.replace("/dashboard");
      return;
    }

    // Unauthenticated user on protected route -> login (with redirect-back)
    const isProtected = PROTECTED_ROUTES.some((r) => path.startsWith(r));
    if (!isAuthenticated && isProtected) {
      sessionStorage.setItem("auth_redirect", path);
      history.replace("/auth/login");
      return;
    }
  }, [isAuthenticated, isLoading, location.pathname, history]);

  // Show a consistent loading state that matches the overall layout
  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900"
      >
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-400"></div>
        </div>
      </motion.div>
    );
  }

  return <>{children}</>;
}

export default function Root({ children }): JSX.Element {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // AuthProvider wraps everything (SSR-safe — it just provides default context during SSR).
  // RouteGuard is client-only.
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
        {isMounted ? (
          <BrowserOnly fallback={<div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900"></div>}>
            {() => (
              <AnimatePresence mode="wait">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900"
                >
                  <ClientRouteGuard>
                    {children}
                    <Suspense fallback={null}>
                      <ChatbotWidget />
                    </Suspense>
                  </ClientRouteGuard>
                </motion.div>
              </AnimatePresence>
            )}
          </BrowserOnly>
        ) : (
          <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-400"></div>
          </div>
        )}
      </div>
    </AuthProvider>
  );
}