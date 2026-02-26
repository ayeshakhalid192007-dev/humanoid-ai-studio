---
name: runtime-guard
description: Performs comprehensive frontend runtime verification including dev server status, dependency integrity, error scanning, asset validation, routing checks, and automatic fixes for common issues.
---

# Runtime Guard Skill

## Purpose

This skill performs comprehensive frontend runtime verification and validation for web applications. It systematically checks for and resolves common issues related to development servers, runtime errors, asset loading, routing, and build configurations that can prevent proper application functionality.

## When to Use

This skill should be used when:

- Development server is not responding correctly or using wrong port
- Node modules or dependencies appear to be corrupted or missing
- Runtime JavaScript errors are occurring during execution
- Assets are not loading properly or paths are broken
- Routing configurations are not rendering root routes
- Network or API requests are failing unexpectedly
- Environment variables are misconfigured
- Build configuration or base path issues are preventing proper deployment
- Need to validate index.html and root mounting element integrity
- Suspect broken imports or missing assets are causing runtime failures

## Validation Responsibilities

### 1. Dev Server Verification
- Verify development server is running on expected port
- Check if correct port is being used for development
- Validate server configuration settings
- Confirm server is properly responding to requests

### 2. Dependency Integrity Checks
- Check node_modules folder integrity and completeness
- Verify package.json and package-lock.json synchronization
- Detect missing or corrupted dependencies
- Validate dependency version compatibility

### 3. Runtime Error Scanning
- Scan browser console for JavaScript errors
- Identify React component rendering errors
- Detect unhandled promise rejections
- Find type errors or undefined references

### 4. HTML and Mounting Validation
- Verify index.html structure and integrity
- Check for proper root mounting element existence
- Validate script and link tag references in HTML
- Ensure correct meta tag and base URL configuration

### 5. Import and Asset Detection
- Detect broken import statements in code
- Identify missing assets (CSS, images, fonts, etc.)
- Validate asset path references in source files
- Check for module resolution issues

### 6. Routing Configuration Validation
- Verify routing configuration is properly set up
- Ensure root route renders correctly
- Check for missing route definitions or parameters
- Validate nested routing and parameter handling

### 7. Network and API Inspection
- Inspect failed network requests in browser tools
- Check API endpoints for connectivity issues
- Identify CORS configuration problems
- Validate service worker and cache status

### 8. Environment Configuration Check
- Verify environment variables are properly set
- Check for missing required environment variables
- Validate environment-specific configurations
- Suggest when server restart is required after changes

### 9. Build Configuration Validation
- Check for base path configuration issues
- Verify build output directory settings
- Validate static asset handling configuration
- Identify potential deployment issues

### 10. Automatic Fix Suggestions
- Apply safe automated fixes where possible
- Suggest remediation steps for detected issues
- Provide restart recommendations when necessary
- Recommend dependency reinstallation when appropriate

## Execution Process

### Initial Diagnosis
1. Check current server status and port availability
2. Examine node_modules and dependency status
3. Scan for console errors and warnings
4. Validate core HTML structure and mounting points

### Detailed Scanning
1. Perform systematic check of all validation responsibilities
2. Generate diagnostic report with severity levels
3. Identify blocking issues that prevent functionality
4. Categorize issues by remediation approach needed

### Fix Implementation
1. Apply automatic fixes for safe, routine issues
2. Provide specific commands for manual fixes
3. Suggest remediation sequences to avoid conflicts
4. Validate fix effectiveness after application

## Output Format

The skill produces a structured diagnostic report containing:

- **System Status Summary**: Overall health assessment
- **Issue Classification**: Blocking, warning, and informational issues
- **Priority Remediation**: Actionable steps ordered by impact
- **Fix Application Log**: Changes made and their results
- **Verification Results**: Confirmation of resolution status

## Automated Remediation

When possible, the skill applies the following automatic fixes:

- Clearing package-lock.json and reinstalling dependencies
- Restarting development server on correct port
- Regenerating missing index.html from template
- Updating broken asset path references
- Refreshing environment variable configuration
- Resetting invalid cache configurations

## Constraints

- Do not change backend logic or API implementations
- Do not introduce new technology stack elements
- Preserve existing functionality and configurations
- Focus only on frontend runtime issues, resource loading, and rendering problems
- Only apply automatic fixes that are known to be safe and non-destructive