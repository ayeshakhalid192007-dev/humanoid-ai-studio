---
name: Fix Frontend Layout and Placement Issues
description: Live visual audit via Playwright MCP at 3 viewports — fixed navbar responsive breakage (Tailwind not working), hamburger menu dropdown, features/tech grids orphan cards, and chatbot button confirmation
type: general
stage: general
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
labels: ["frontend", "layout", "navbar", "responsive", "css", "playwright"]
---

## Prompt

Use the playwright mcp server and live run the project and see all the placement issues and use /frontend-design skill to fix the issues also fix the chatbot widget button as it moves with scrolling of the content. Audit visually at 3 viewports (375px / 768px / 1280px) — take screenshots and identify all layout/placement issues. Fix everything found, starting with the hamburger menu: Navbar overlapping content, Wrong z-index / positioning, Any broken layout, overflow, clipping, or misalignment. Apply minimal surgical fixes directly in source files. Screenshot before & after each fix.

## Root Cause Discovered

**No `@tailwind` directives exist anywhere in the CSS files.** The Tailwind CSS utility classes used in FuturisticNavbar.tsx (`md:hidden`, `hidden md:flex`, `flex items-center gap-2`, etc.) produced **zero CSS output**, causing all responsive show/hide logic to silently fail.

## Issues Found & Fixed

| # | Issue | File Changed | Fix Applied |
|---|-------|-------------|-------------|
| 1 | Hamburger icon visible on desktop (1280px) | `FuturisticNavbar.tsx` + `futuristic-minimalism.css` | Replaced `md:hidden` div wrapper with `fm-navbar__mobile-toggle` CSS class; set `display: none` on desktop |
| 2 | Desktop nav links + auth showing on mobile | `FuturisticNavbar.tsx` + `futuristic-minimalism.css` | Replaced `hidden md:flex items-center gap-2` with `fm-navbar__nav`; replaced `hidden md:flex fm-navbar__auth-container` with `fm-navbar__auth-container`; added `display: none` at ≤768px |
| 3 | Mobile menu dropdown colliding in flex row | `FuturisticNavbar.tsx` + `futuristic-minimalism.css` | Added `.fm-navbar__mobile-menu { position: absolute; top: 100%; left: 0; right: 0; }` to pop dropdown below navbar |
| 4 | Mobile menu Tailwind classes non-functional | `FuturisticNavbar.tsx` | Replaced all Tailwind classes inside menu with `fm-navbar__link-mobile`, `fm-navbar__mobile-menu-inner`, `fm-navbar__mobile-menu-auth`, etc. |
| 5 | Features grid: 4 cards → 3+1 orphan layout | `neon-brutalism.css` | Changed `repeat(auto-fit, minmax(300px, 1fr))` → `repeat(2, 1fr)` for clean 2×2 |
| 6 | Tech stack grid: 6 cards → 5+1 orphan layout | `neon-brutalism.css` | Changed `repeat(auto-fit, minmax(200px, 1fr))` → `repeat(3, 1fr)` for clean 3×2 |
| 7 | Chatbot button position | N/A | Confirmed `position: fixed; bottom: 28px; right: 28px` working correctly; no transformed ancestors |

## Files Modified

- `book/src/components/Navigation/FuturisticNavbar.tsx`
- `book/src/css/futuristic-minimalism.css`
- `book/src/css/neon-brutalism.css`

## Verification

Screenshots confirmed via Playwright MCP:
- `after-navbar-1280.png`: Desktop — logo + nav links + auth buttons, NO hamburger
- `after-navbar-375.png`: Mobile — logo + hamburger only
- `after-hamburger-fixed.png`: Mobile menu drops below navbar with full link list
- `after-features-grid.png`: Clean 2×2 feature cards
- `after-tech-grid.png`: Clean 3×2 tech stack cards
- `after-768-features.png`: Single-column at 768px (responsive breakpoint working)
