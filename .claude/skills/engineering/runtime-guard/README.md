# Runtime Guard Skill

## Overview

The Runtime Guard skill provides comprehensive frontend runtime verification and validation for web applications. It systematically checks for and resolves common issues related to development servers, runtime errors, asset loading, routing, and build configurations.

## Quick Start

### Using the Skill

Invoke the skill when you encounter frontend runtime issues:

```
Use runtime-guard to diagnose the application
```

### Running Diagnostic Scripts

#### PowerShell (Windows)
```powershell
.\.claude\skills\engineering\runtime-guard\scripts\runtime-diagnostic.ps1
```

#### Bash (Linux/Mac)
```bash
./.claude/skills/engineering/runtime-guard/scripts/runtime-diagnostic.sh
```

#### Python Script
```bash
python .claude/skills/engineering/runtime-guard/scripts/runtime-guard.py
```

## What It Checks

### 1. Development Server
- Port availability and usage
- Server response status
- Configuration validation

### 2. Dependencies
- node_modules integrity
- package.json/package-lock.json sync
- Missing or corrupted packages

### 3. Runtime Errors
- JavaScript console errors
- React component errors
- Unhandled promise rejections

### 4. HTML Structure
- index.html existence and validity
- Root mounting element presence
- Script and link tag references

### 5. Assets
- Broken import statements
- Missing assets (CSS, images, fonts)
- Path reference validation

### 6. Routing
- Route configuration
- Root route rendering
- Nested routing issues

### 7. Network
- Failed API requests
- CORS configuration
- Service worker status

### 8. Environment
- Environment variable presence
- Configuration completeness
- Restart requirements

### 9. Build Configuration
- Base path settings
- Output directory configuration
- Static asset handling

### 10. Automated Fixes
- Safe automatic remediation
- Manual fix suggestions
- Restart recommendations

## Reference Documentation

### Common Issues
See `references/common-issues.md` for detailed information about:
- Dev server problems
- Dependency conflicts
- Runtime JavaScript errors
- Asset loading failures
- Routing configuration issues
- Network and API problems
- Environment variable issues
- Build configuration problems
- Cache and service worker issues

### Console Error Patterns
See `references/console-error-patterns.md` for:
- React-specific errors
- Module resolution errors
- Network errors
- Type errors
- Asset loading errors
- Memory and performance issues
- Build-time errors
- Docusaurus-specific errors

## Output Format

The skill produces a structured diagnostic report:

```
🔍 Runtime Guard - Frontend Diagnostic Tool
==========================================

📋 1. Checking Dev Server Status
✅ Port 3000 is in use (likely development server running)
✅ Development server responding on port 3000

📋 2. Checking Dependency Integrity
✅ node_modules directory exists
📊 Found 847 top-level packages in node_modules
✅ package.json and package-lock.json both exist

📋 3. Checking Build Artifacts
✅ index.html found at public/index.html

📋 4. Checking Environment Variables
✅ .env file exists
📊 Found 5 environment variable definitions in .env

📋 5. Checking Configuration Files
✅ package.json found
✅ vite.config.js found

📋 6. Detecting Frontend Framework
✅ react detected in package.json

✅ Initial diagnostic complete!
```

## Automated Fixes

The skill can automatically apply safe fixes:

- ✅ **Safe Auto Fixes:**
  - Installing missing dependencies
  - Copying .env.example to .env
  - Regenerating package-lock.json
  - Clearing and reinstalling node_modules

- ⚠️ **Manual Fixes (requires confirmation):**
  - Killing processes on occupied ports
  - Modifying build configurations
  - Updating routing configurations
  - Changing environment variables

## Best Practices

1. **Run diagnostics before debugging** - Get a complete picture of issues
2. **Apply fixes in order** - Start with blocking issues first
3. **Restart server after fixes** - Many fixes require server restart
4. **Check browser console** - Some issues only appear in browser
5. **Verify after fixes** - Run diagnostics again to confirm resolution

## Integration with Development Workflow

### When to Use Runtime Guard

- Development server won't start
- Blank page or white screen of death
- Assets not loading (404 errors)
- Routes not working correctly
- Console showing errors
- After pulling new code
- After dependency updates
- Before deployment

### Typical Workflow

1. **Detect Issue** - Notice something not working
2. **Run Diagnostics** - Use runtime-guard skill or scripts
3. **Review Report** - Understand what's wrong
4. **Apply Fixes** - Start with safe auto-fixes
5. **Verify** - Test that issue is resolved
6. **Document** - Note any manual steps taken

## Troubleshooting

### Script Won't Run

**PowerShell:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Bash:**
```bash
chmod +x ./.claude/skills/engineering/runtime-guard/scripts/runtime-diagnostic.sh
```

### Python Script Issues

Ensure Python 3.7+ is installed:
```bash
python --version
```

### False Positives

Some checks may report issues that aren't actually problems for your specific setup. Review the context and use judgment about which fixes to apply.

## Contributing

To improve this skill:

1. Add new diagnostic checks to scripts
2. Document new error patterns in references
3. Add automated fix suggestions for common issues
4. Update SKILL.md with new capabilities

## License

Part of the Claude Code skills library.