# ADR 001: Layout, Authentication, and Navigation System Refactoring

## Status
Accepted

## Date
2026-02-21

## Context
The Physical AI Platform had inconsistent layout structures across pages, leading to:
- Spacing issues and layout shifts
- Authentication state confusion
- Navigation problems
- Inconsistent user experience

The Docusaurus theme was properly swizzled with authentication context at the root, but individual pages used different layout approaches causing visual inconsistencies.

## Decision
We decided to implement a comprehensive refactoring of the layout, authentication, and navigation systems by:

### 1. Creating Standardized Layout Components
- **AppLayout Component**: Main layout wrapper with consistent spacing, backgrounds, and container structure
- **Layout Variants**: Specialized layouts for different page types (landing, docs, dashboard, auth)
- **Global Styling**: Consistent spacing, padding, and background management

### 2. Enhancing Authentication System
- **Improved AuthContext**: Better loading states and error handling
- **Auth State Visualization**: Clear UI indicators for auth status with loading states
- **Protected Route System**: Robust route protection with proper redirects

### 3. Updating Navigation System
- **Navbar Improvements**: Enhanced navbar with active link highlighting and better responsiveness
- **Hydration Handling**: Addressed potential hydration mismatches
- **Smooth Transitions**: Maintained existing Framer Motion transitions

## Technical Implementation

### Layout Standardization
```tsx
interface AppLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  showAuthIndicator?: boolean;
  showNavbar?: boolean;
  background?: 'default' | 'auth' | 'docs';
}
```

### New Component Structures
- Created standardized `max-w-7xl mx-auto px-6` container system
- Added Framer Motion animations for better UX transitions
- Implemented proper background management with layered gradients

### File Organization
- `components/Layout/` directory with reusable layout components
- `components/Auth/AuthStateIndicator.tsx` for auth status visualization
- `components/Navigation/ActiveLink.tsx` for active link highlighting
- Updated all page-level components to use new layouts

## Consequences

### Positive
- Eliminated layout shifts and top spacing issues
- Consistent authentication state visualization
- Improved navigation with active link highlighting
- Standardized layout structure across all pages
- Production-ready code architecture with proper state management
- Better user experience with consistent spacing and responsive design

### Neutral
- Additional dependencies on motion components
- New component hierarchy to maintain

### Negative
- Some initial complexity due to abstraction layers
- Migration effort required for existing pages

## Alternatives Considered
- Keep existing ad-hoc layout system (rejected due to maintenance issues)
- Use third-party layout libraries (rejected to maintain consistency with existing architecture)

## Implementation Notes
This refactoring follows Docusaurus theme swizzling best practices and maintains compatibility with existing documentation systems. The new layout system is backwards compatible with existing pages and provides a solid foundation for future development.

## Verification
The implementation has been tested across:
- All major pages (homepage, features, dashboard, enrollment, etc.)
- Different authentication states (authenticated, unauthenticated, loading)
- Responsive behavior across different screen sizes
- SSR hydration handling

## Team Approval
This decision has been reviewed and approved by the development team as an improvement to the codebase architecture.