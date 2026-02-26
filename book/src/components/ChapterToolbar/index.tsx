/**
 * ChapterToolbar Component
 *
 * Provides "Personalized Version" and "Translate to Urdu" buttons
 * at the top of each chapter page. Manages content state transitions
 * and API calls for personalization and translation.
 */

import React, { useState, useCallback, useRef, useEffect } from "react";
import BrowserOnly from "@docusaurus/BrowserOnly";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { marked } from "marked";
import DOMPurify from "dompurify";
import ContentSkeleton from "../ui/ContentSkeleton";
import styles from "./styles.module.css";

function getErrorMessage(err: unknown, action: string): string {
  if (err instanceof TypeError && err.message === "Failed to fetch") {
    return "Cannot connect to the server. Please ensure the backend is running.";
  }
  if (err instanceof Error) {
    const msg = err.message;
    if (msg.includes("401")) return "Session expired. Please log in again.";
    if (msg.includes("404")) return "Chapter content not found in the curriculum database.";
    if (msg.includes("429")) return "Rate limit reached. Please wait a few minutes and try again.";
    if (msg.includes("503")) return "AI service temporarily unavailable. Please try again in a moment.";
    return msg;
  }
  return `Unable to ${action}. Please try again later.`;
}

type ContentState = "original" | "personalized" | "urdu" | "personalized-urdu";

interface ChapterToolbarProps {
  chapterSlug: string;
  children: React.ReactNode;
}

function ChapterToolbarInner({ chapterSlug, children }: ChapterToolbarProps) {
  const { siteConfig } = useDocusaurusContext();
  const BACKEND_URL = (siteConfig?.customFields?.backendUrl as string) || "http://localhost:8000";

  const { useAuth } =
    require("../../context/AuthContext") as typeof import("../../context/AuthContext");
  const { AuthModal } =
    require("../Auth/AuthModal") as typeof import("../Auth/AuthModal");

  const { isAuthenticated, profile, refreshSession, fetchProfile } = useAuth();

  const [contentState, setContentState] = useState<ContentState>("original");
  const [personalizedHtml, setPersonalizedHtml] = useState<string>("");
  const [urduHtml, setUrduHtml] = useState<string>("");
  const [personalizedUrduHtml, setPersonalizedUrduHtml] = useState<string>("");
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastFailedAction, setLastFailedAction] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const pendingPersonalize = useRef(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // Auto-trigger personalization after login
  useEffect(() => {
    if (pendingPersonalize.current && isAuthenticated) {
      pendingPersonalize.current = false;
      handlePersonalize();
    }
  }, [isAuthenticated]);

  const handlePersonalize = useCallback(async () => {
    if (!isAuthenticated) {
      pendingPersonalize.current = true;
      setShowAuthModal(true);
      return;
    }

    setLoading("personalize");
    setError(null);
    setLastFailedAction(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/personalize`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chapter_slug: chapterSlug }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${response.status}`);
      }

      const data = await response.json();
      setPersonalizedHtml(data.content);
      setContentState("personalized");
    } catch (err: unknown) {
      console.error("[ChapterToolbar] personalize failed:", err);
      setError(getErrorMessage(err, "personalize"));
      setLastFailedAction("personalize");
    } finally {
      setLoading(null);
    }
  }, [isAuthenticated, chapterSlug, BACKEND_URL]);

  const handleTranslate = useCallback(async () => {
    setLoading("translate");
    setError(null);
    setLastFailedAction(null);

    try {
      const isFromPersonalized = contentState === "personalized";
      const requestBody: Record<string, string> = { chapter_slug: chapterSlug };

      // If currently viewing personalized content, translate that instead
      if (isFromPersonalized && personalizedHtml) {
        requestBody.content = personalizedHtml;
      }

      const response = await fetch(`${BACKEND_URL}/api/translate`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${response.status}`);
      }

      const data = await response.json();

      if (isFromPersonalized) {
        setPersonalizedUrduHtml(data.content);
        setContentState("personalized-urdu");
      } else {
        setUrduHtml(data.content);
        setContentState("urdu");
      }
    } catch (err: unknown) {
      console.error("[ChapterToolbar] translate failed:", err);
      setError(getErrorMessage(err, "translate"));
      setLastFailedAction("translate");
    } finally {
      setLoading(null);
    }
  }, [contentState, chapterSlug, personalizedHtml, BACKEND_URL]);

  const handleRevert = useCallback(() => {
    setContentState("original");
    setError(null);
    setLastFailedAction(null);
  }, []);

  const handleRegenerate = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading("personalize");
    setError(null);
    setLastFailedAction(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/personalize`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chapter_slug: chapterSlug, regenerate: true }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${response.status}`);
      }

      const data = await response.json();
      setPersonalizedHtml(data.content);
      setContentState("personalized");
    } catch (err: unknown) {
      console.error("[ChapterToolbar] regenerate failed:", err);
      setError(getErrorMessage(err, "regenerate"));
      setLastFailedAction("regenerate");
    } finally {
      setLoading(null);
    }
  }, [isAuthenticated, chapterSlug, BACKEND_URL]);

  const handleRetry = useCallback(() => {
    if (lastFailedAction === "personalize") handlePersonalize();
    else if (lastFailedAction === "translate") handleTranslate();
    else if (lastFailedAction === "regenerate") handleRegenerate();
  }, [lastFailedAction, handlePersonalize, handleTranslate, handleRegenerate]);

  const isOriginal = contentState === "original";
  const isPersonalized = contentState === "personalized";
  const isUrdu = contentState === "urdu";
  const isPersonalizedUrdu = contentState === "personalized-urdu";
  const isRtl = isUrdu || isPersonalizedUrdu;

  // Determine which content to display
  let displayContent: string | null = null;
  if (isPersonalized) displayContent = personalizedHtml;
  else if (isUrdu) displayContent = urduHtml;
  else if (isPersonalizedUrdu) displayContent = personalizedUrduHtml;

  // Sanitize markdown content for safe rendering
  const sanitizedHtml = displayContent
    ? DOMPurify.sanitize(marked.parse(displayContent) as string)
    : null;

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.buttonGroup}>
          {/* Personalize button — only from original state */}
          {isOriginal && (
            <button
              className={`${styles.toolbarButton} ${styles.personalizeButton}`}
              onClick={handlePersonalize}
              disabled={loading !== null}
            >
              {loading === "personalize" ? (
                <>
                  <span className={styles.spinner} />
                  {" Personalizing..."}
                </>
              ) : (
                "\u2728 Personalized Version"
              )}
            </button>
          )}

          {/* Translate to Urdu button */}
          {(isOriginal || isPersonalized) && (
            <button
              className={`${styles.toolbarButton} ${styles.translateButton}`}
              onClick={handleTranslate}
              disabled={loading !== null}
            >
              {loading === "translate" ? (
                <>
                  <span className={styles.spinner} />
                  {" Translating..."}
                </>
              ) : (
                "\uD83C\uDF10 Translate to Urdu"
              )}
            </button>
          )}

          {/* Revert to Original */}
          {!isOriginal && (
            <button
              className={`${styles.toolbarButton} ${styles.revertButton}`}
              onClick={handleRevert}
              disabled={loading !== null}
            >
              {isUrdu || isPersonalizedUrdu
                ? "View Original (English)"
                : "Revert to Original"}
            </button>
          )}

          {/* Regenerate (personalized state only) */}
          {isPersonalized && (
            <button
              className={`${styles.toolbarButton} ${styles.regenerateButton}`}
              onClick={handleRegenerate}
              disabled={loading !== null}
            >
              Regenerate
            </button>
          )}
        </div>

        {error && (
          <div className={styles.errorBar}>
            <span>{error}</span>
            <button
              className={styles.retryButton}
              onClick={handleRetry}
            >
              Retry
            </button>
          </div>
        )}
      </div>

      {/* Content area */}
      <div
        ref={contentRef}
        className={isRtl ? styles.rtlContent : undefined}
        dir={isRtl ? "rtl" : undefined}
        lang={isRtl ? "ur" : undefined}
      >
        {loading ? (
          <ContentSkeleton type="full" />
        ) : sanitizedHtml ? (
          <div
            className="markdown"
            dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
          />
        ) : (
          children
        )}
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => {
            setShowAuthModal(false);
            pendingPersonalize.current = false;
          }}
          initialView="login"
        />
      )}
    </>
  );
}

export default function ChapterToolbar(props: ChapterToolbarProps) {
  return (
    <BrowserOnly fallback={<>{props.children}</>}>
      {() => <ChapterToolbarInner {...props} />}
    </BrowserOnly>
  );
}
