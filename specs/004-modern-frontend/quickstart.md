# Quickstart: Modern Frontend Homepage Development

## Prerequisites

- Node.js 18+ LTS installed
- Yarn or npm package manager
- Git for version control
- Basic familiarity with React, TypeScript, and Next.js

## Project Setup

### 1. Install Dependencies
```bash
cd book/  # Since we're working with the existing Docusaurus project
npm install next@latest react@latest react-dom@latest
npm install -D tailwindcss postcss autoprefixer
npm install framer-motion
npx tailwindcss init -p
```

### 2. Configure Tailwind CSS

Update `tailwind.config.js` in the book/ directory:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",  // Will be created for Next.js app
  ],
  darkMode: 'class',  // Using class-based dark mode
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0f0f14',
        'gradient-blue': '#3b82f6',
        'gradient-purple': '#8b5cf6',
        'gradient-indigo': '#6366f1',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'stagger': 'stagger 0.1s ease',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
```

### 3. Install Next.js App Router

Since we're working with an existing Docusaurus project, we need to set up Next.js in parallel:

```bash
mkdir -p app/
touch app/page.tsx  # This will be our Next.js homepage
```

## Development Workflow

### 1. Creating Components

All new modern frontend components will be created with the following structure:

**Component Name**: HeroSection
**File Location**: `app/components/HeroSection.tsx`
**Features**: Gradient background animation, CTA buttons with glow effects, staggered content reveal

### 2. Reusing Existing AuthContext

Since the project already has a working AuthContext in `book/src/context/AuthContext`, implement wrapper to make it compatible:

```tsx
'use client'

import { createContext, useContext, useEffect, useState } from 'react'

// Re-export existing auth context in Next.js compatible way
const AuthProviderWrapper = ({ children }: { children: React.ReactNode }) => {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return <div>Loading...</div> // Prevent hydration issues
  }

  // Import and wrap existing auth context
  return (
    <AuthWrapper>
      {children}
    </AuthWrapper>
  )
}
```

### 3. Animation System

Use Framer Motion for all entrance and hover animations:

```tsx
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2  // Delay between child animations
    }
  }
}

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
}

export const AnimatedCard = () => (
  <motion.div
    variants={container}
    initial="hidden"
    animate="show"
    className="bg-white/10 backdrop-blur-md rounded-2xl p-6"
  >
    {/* Card content */}
  </motion.div>
)
```

## Component Breakdown

### Hero Section
- Full-screen (min-h-screen) gradient background
- Animated text with stagger effect
- Two CTA buttons: "Get Started" and "Explore Features"
- Hover effects with button glow and scale transformation

### About Section
- Centered glassmorphism container
- Backdrop blur effect with white/10 opacity
- Professional explanation of platform value

### Core Learning Pillars Grid
- Responsive grid (3 columns desktop, 1 mobile)
- 6 cards with specific titles as required
- Card lift on hover with glowing border
- Staggered entrance animation

### Features Overview
- Display all 11 required features
- Subtle scroll-based reveal animation
- Clean, organized layout

### Footer
- Minimal design with project name and tagline
- Essential links (GitHub, community, contact)
- Clean typography aligned with aesthetic

## Color Palette

- **Background**: #0f0f14 (dark theme foundation)
- **Gradient**: Blue (0x3b82f6) → Purple (0x8b5cf6) → Indigo (0x6366f1)
- **Text**: text-white/90 for primary, text-white/70 for secondary
- **Glass Morphism**: bg-white/10 with backdrop-blur-lg for elevated elements

## Typography

- **Font**: Inter (loaded via next/font)
- **Hierarchy**:
  - H1: text-4xl for hero titles
  - H2: text-3xl for section headings
  - H3: text-2xl for card titles
  - Body: text-lg with leading-relaxed for readability
- **Spacing**: Consistent padding/margin using Tailwind spacing scale (p-6, p-8, etc.)

## Animation Guidelines

- **Entrance**: Fade in with slight translation for all content
- **Stagger**: For groups of elements, delay between 0.1-0.2s
- **Hover**: Lift Y-translation of -2px with 0.03-0.05 scale increase
- **Performance**: Keep animations under 0.5s for smooth performance

## Responsive Breakpoints

- **Mobile**: <640px - Single column layouts
- **Tablet**: 640px-1024px - Adjust columns to 2 where applicable
- **Desktop**: >1024px - Full 3-column experience for grids

## Environment Setup for Production

```bash
# Set required environment variables
NEXT_PUBLIC_BACKEND_URL=  # URL for backend API
NEXT_PUBLIC_SITE_URL=     # Main site URL
NEXT_PUBLIC_GA_ID=        # Google Analytics (optional)
```

## Running Development Server

Once components are created, start the Next.js development server:

```bash
# In book/ directory
npm run dev  # Using next dev command
```

Note: We'll need to carefully handle routing so that the Next.js app serves the homepage while keeping Docusaurus handling docs and other pages.