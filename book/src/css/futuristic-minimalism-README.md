# Futuristic Minimalism Design System

This design system implements a futuristic minimalism aesthetic with strategic use of whitespace, clean lines, sophisticated typography, and controlled color usage.

## Core Philosophy

- **Minimalist approach**: Emphasis on whitespace and clean, uncluttered interfaces
- **Strategic color usage**: Limited color palette with strategic accents
- **Sophisticated typography**: Careful font hierarchy and text treatment
- **Subtle animations**: Smooth transitions to enhance the user experience
- **Geometric patterns**: Clean, structured visual elements

## Color Palette

### Primary Colors
- `--fm-bg-primary`: #0a0a0a (Primary background)
- `--fm-bg-secondary`: #111111 (Secondary background)
- `--fm-bg-tertiary`: #1a1a1a (Tertiary background)

### Text Colors
- `--fm-text-primary`: #ffffff (Primary text)
- `--fm-text-secondary`: #b8b8b8 (Secondary text)
- `--fm-text-tertiary`: #666666 (Tertiary/Disabled text)

### Accent Colors
- `--fm-accent-primary`: #00ffff (Cyan for tech feel)
- `--fm-accent-secondary`: #00ffaa (Spring green)
- `--fm-accent-tertiary`: #ff00cc (Magenta)
- `--fm-accent-warm`: #ff7700 (Orange)

## Typography

### Fonts
- `--fm-font-display`: 'Inter Tight', 'Inter', system fonts (for headings)
- `--fm-font-body`: 'Inter', system fonts (for body copy)
- `--fm-font-mono`: 'JetBrains Mono', monospace fonts (for code)

### Heading Classes
- `.fm-h1`: 3.5rem, bold, -0.02em tracking
- `.fm-h2`: 2.5rem, semibold, -0.015em tracking
- `.fm-h3`: 2rem, medium, -0.01em tracking
- `.fm-h4`: 1.5rem, medium

## Layout Classes

### Container
- `.fm-container`: Max-width 1200px with 2rem horizontal padding

### Sections
- `.fm-section`: 6rem vertical padding
- `.fm-section--lg`: 8rem vertical padding
- `.fm-section--xl`: 12rem vertical padding

### Grids
- `.fm-grid--2`: Two columns (min 300px each)
- `.fm-grid--3`: Three columns (min 280px each)
- `.fm-grid--4`: Four columns (min 250px each)

## Component Classes

### Cards
- `.fm-card`: Default card with backdrop blur
- `.fm-card--glass`: More transparent card
- `.fm-card--solid`: Solid background card
- `.fm-card--elevated`: Gradient background card
- `.fm-card--accent`: With accent border

### Buttons
- `.fm-button`: Base button
- `.fm-button--primary`: Gradient accent button
- `.fm-button--secondary`: Dark background button
- `.fm-button--outline`: Bordered button
- `.fm-button--ghost`: Ghost button
- `.fm-button--small`, `.fm-button--large`, `.fm-button--block`: Size variants

### Hover Effects
- `.fm-hover-lift`: Raises card with shadow on hover
- `.fm-hover-glow`: Adds glow effect
- `.fm-hover-border`: Changes border color
- `.fm-hover-scale`: Slightly scales up

## Animation Classes
- `.fm-fade-in`: Fade in effect
- `.fm-slide-up`: Slide up from bottom
- `.fm-scale-in`: Scale in effect
- `.fm-pulse`: Pulsing animation

## Integration

To integrate this design system:

1. Add the CSS file to your Docusaurus config:
```js
// In docusaurus.config.js
presets: [
  [
    'classic',
    {
      theme: {
        customCss: [
          require.resolve('./src/css/futuristic-minimalism.css'),
        ],
      },
    },
  ],
],
```

2. The design system includes classes that can be applied directly to your JSX elements following the naming pattern `fm-{component}`.

3. For components using Framer Motion (like animated transitions), the CSS classes work together with motion component classes.