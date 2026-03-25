/**
 * SocialLoader — Orbital arc spinner for social auth buttons.
 *
 * Design: A comet-arc on a dim track ring with a neon glow tail.
 * Provider-aware accent colors that match the glassmorphism palette.
 */

import React from "react";

interface SocialLoaderProps {
  provider: "google" | "github";
  size?: number;
}

const PROVIDER_COLORS: Record<string, { arc: string; glow: string }> = {
  google: {
    arc: "url(#google-grad)",
    glow: "rgba(99,102,241,0.8)",   // indigo neon
  },
  github: {
    arc: "url(#github-grad)",
    glow: "rgba(0,255,255,0.7)",    // cyan neon
  },
};

export function SocialLoader({ provider, size = 18 }: SocialLoaderProps) {
  const { glow } = PROVIDER_COLORS[provider];
  const r = (size - 3) / 2;
  const circ = 2 * Math.PI * r;
  // Arc covers ~75% of the ring
  const arcLen = circ * 0.75;
  const id = `social-loader-${provider}`;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      fill="none"
      aria-hidden="true"
      style={{
        animation: "social-loader-spin 0.9s cubic-bezier(0.4,0,0.2,1) infinite",
        filter: `drop-shadow(0 0 4px ${glow})`,
        flexShrink: 0,
      }}
    >
      <defs>
        {/* Google: indigo → violet → magenta sweep */}
        <linearGradient id="google-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#6366f1" stopOpacity="0" />
          <stop offset="40%"  stopColor="#8b5cf6" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#ec4899" stopOpacity="1" />
        </linearGradient>
        {/* GitHub: deep blue → cyan sharp tip */}
        <linearGradient id="github-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#3b82f6" stopOpacity="0" />
          <stop offset="50%"  stopColor="#06b6d4" stopOpacity="0.7" />
          <stop offset="100%" stopColor="#00ffff" stopOpacity="1" />
        </linearGradient>
      </defs>

      {/* Dim track ring */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        stroke="rgba(255,255,255,0.1)"
        strokeWidth="2"
      />

      {/* Comet arc — gradient stroke */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        stroke={PROVIDER_COLORS[provider].arc}
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray={`${arcLen} ${circ - arcLen}`}
        strokeDashoffset={circ * 0.25}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </svg>
  );
}

/**
 * Inject the keyframe once into the document head.
 * Works in both SSR-safe BrowserOnly context and client.
 */
if (typeof document !== "undefined") {
  const STYLE_ID = "social-loader-keyframes";
  if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      @keyframes social-loader-spin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      @keyframes social-btn-shimmer {
        0%   { background-position: -200% center; }
        100% { background-position:  200% center; }
      }
      @keyframes social-btn-glow-pulse {
        0%, 100% { box-shadow: 0 0 0 0 transparent; }
        50%       { box-shadow: 0 0 12px 2px rgba(99,102,241,0.35); }
      }
    `;
    document.head.appendChild(style);
  }
}
