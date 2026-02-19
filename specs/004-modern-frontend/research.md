# Research: Modern Frontend Homepage Development

## Current Architecture Analysis

### Technology Stack
- **Framework**: Docusaurus 3.6.3 (based on existing project)
- **Language**: React 18 with TypeScript
- **Styling**: CSS Modules (currently used in the project)
- **Auth System**: Custom AuthContext with BrowserOnly wrapper
- **Routing**: Docusaurus routing system with @docusaurus/Link

### Current Homepage Components
1. **Hero Section**: Simple gradient header with site title/tagline and "Get Started" button
2. **Module Cards**: Grid of 4 course modules with icons and descriptions
3. **Learning Approach**: Three-card "Predict-Execute-Reflect" section
4. **AI Assistant**: Auth-protected assistant section with login modal

### Docusaurus Integration Points
- Layout components are swizzled (as per memory): Root.tsx, Navbar/Content already swizzled
- AuthContext provides authentication state
- BrowserOnly wrapper is used for client-side auth checks
- Layout is themed via @theme/Layout
- Custom CSS via index.module.css

## Challenges & Migration Path

### Challenge 1: Docusaurus to Next.js Migration
**Decision**: Migrate gradually by creating new homepage in Next.js while maintaining Docusaurus-based documentation sections
**Rationale**: Complete migration risky since the curriculum/docs area relies on Docusaurus features. A phased approach allows maintaining content while upgrading the homepage experience.
**Approach**: Create Next.js app at `/` that links to existing Docusaurus `/docs/*` routes

### Challenge 2: Styling & Design System
**Decision**: Develop Tailwind-based design system alongside Docusaurus CSS
**Rationale**: The project needs a modern, professional look with dark mode and animations as required by spec
**Approach**: Maintain Docusaurus styling for doc content while implementing new design language for homepage
- Implement dark mode first (default) using Tailwind's dark mode
- Create glassmorphism and gradient components using Tailwind classes
- Use Inter font via next/font

### Challenge 3: Framer Motion Integration
**Decision**: Animation system is independent and can be integrated separately
**Rationale**: Framer Motion works with React components regardless of framework
**Approach**: Add initial animations for page load, scroll triggers, and hover interactions

### Challenge 4: Auth Context Integration
**Decision**: Maintain the existing AuthContext system but wrap for Next.js compatibility
**Rationale**: User authentication system is working well and should be preserved
**Approach**: Create Next.js-compatible provider wrapper around existing auth context

## Design Implementation Strategy

### Color Palette Decision
- **Background**: #0f0f14 (dark theme foundation)
- **Accent Gradients**: Blue-purple-indigo (#3b82f6 → #8b5cf6 → #6366f1 linear gradient)
- **Glassmorphism**: bg-white/10 with backdrop-blur class
- **Card Elevation**: shadow-xl/2xl with soft glowing borders

### Typography System
- **Font**: Inter (as specified in feature spec for consistency across the project)
- **Hierarchy**:
  - H1: 2.5rem (32px) bold, leading-tight for hero titles
  - H2: 1.875rem (30px) semibold for section titles
  - H3: 1.5rem (24px) semibold for card headings
  - Body: 1rem (16px) with increased lineHeight (1.7) for readability
- **Colors**: Light text on dark background (text-white/90, text-white/70 for secondary)

### Responsive Grid Strategy
- **Hero**: Full width, full screen height (min-h-screen)
- **About Section**: Center aligned with max-width container
- **Core Learning Pillars**: 3 columns on desktop (md:grid-cols-3), 1 column on mobile (grid-cols-1)
- **Features Overview**: Responsive grid adapting to 1-3 columns based on screen size
- **Footer**: Minimal grid layout

### Animation & Motion Guidelines
- **Page Load**: Fade in with stagger for hero elements
- **Scroll Effects**: Animate elements into view with framer-motion viewport trigger
- **Hover Effects**: Card lift (translate-y-[-4px]), scale (scale-105), and glow
- **Button Effects**: Scale 1.03-1.05 with glowing border
- **Performance**: Limit animation complexity to maintain 60fps

## Implementation Prerequisites

### Dependencies to Install
- `next` (v14+ with App Router)
- `react` & `react-dom`
- `tailwindcss` (v3+)
- `framer-motion` (v10+)
- `next/font`
- `@headlessui/react` (if needed for focus management)

### Project Structure Recommendations
- Keep Docusaurus in `/book` directory
- Create new Next.js app in `/homepage` directory initially
- Gradually redirect homepage while maintaining `/docs/*` paths
- Set up shared auth context between systems

### Migration Steps
1. Create new Next.js project with App Router
2. Set up Tailwind with dark mode
3. Implement design system components
4. Build individual sections (hero, about, etc.)
5. Add Framer Motion animations
6. Integrate with existing auth system
7. Deploy alongside Docusaurus, ensuring proper routing