# Runtime Guard - Quick Reference Card

## 🚀 Quick Commands

### Run Full Diagnostic
```bash
# PowerShell (Windows)
.\.claude\skills\engineering\runtime-guard\scripts\runtime-diagnostic.ps1

# Bash (Linux/Mac)
./.claude/skills/engineering/runtime-guard/scripts/runtime-diagnostic.sh

# Python (Cross-platform)
python .claude/skills/engineering/runtime-guard/scripts/runtime-guard.py
```

## 🔍 Common Issue Quick Fixes

### Dev Server Won't Start
```bash
# Check what's using the port
netstat -ano | findstr :3000        # Windows
lsof -ti:3000                       # Linux/Mac

# Kill the process
taskkill /PID <PID> /F              # Windows
kill -9 <PID>                       # Linux/Mac
```

### Dependencies Broken
```bash
# Clean reinstall
rm -rf node_modules package-lock.json
npm install

# Or with cache clear
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Environment Variables Missing
```bash
# Copy from example
cp .env.example .env

# Then edit .env with your values
```

### Blank Page / White Screen
1. Check browser console for errors
2. Verify root element exists in index.html
3. Check routing configuration
4. Ensure dev server is running

### Assets Not Loading (404)
1. Check base path in config
2. Verify asset paths are correct
3. Ensure assets are in public/ or properly imported
4. Check build output directory

### CORS Errors
```javascript
// Add proxy in vite.config.js
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

## 📋 Diagnostic Checklist

- [ ] Dev server running on correct port
- [ ] node_modules exists and complete
- [ ] package.json and package-lock.json in sync
- [ ] .env file exists with required variables
- [ ] index.html exists with root element
- [ ] Build config file present
- [ ] No console errors in browser
- [ ] Assets loading correctly
- [ ] Routes rendering properly
- [ ] API requests succeeding

## 🎯 Priority Order for Fixes

1. **Critical (Blocking)**
   - Missing node_modules
   - Missing package.json
   - Dev server not running
   - Missing index.html

2. **High (Functionality Broken)**
   - Runtime JavaScript errors
   - Assets not loading
   - Routes not working
   - API requests failing

3. **Medium (Degraded Experience)**
   - Console warnings
   - Missing environment variables
   - Performance issues
   - Cache problems

4. **Low (Cosmetic)**
   - Linting warnings
   - Unused dependencies
   - Documentation issues

## 🛠️ Safe Auto-Fix Commands

```bash
# Install missing dependencies
npm install

# Copy environment template
cp .env.example .env

# Regenerate lock file
rm package-lock.json && npm install

# Clear cache and reinstall
npm cache clean --force && npm install
```

## ⚠️ Manual Fix Commands (Use with Caution)

```bash
# Force kill process on port
taskkill /F /PID <PID>              # Windows
kill -9 <PID>                       # Linux/Mac

# Delete and reinstall everything
rm -rf node_modules package-lock.json && npm install

# Reset git changes (DESTRUCTIVE)
git reset --hard HEAD

# Clean build artifacts
rm -rf dist build .cache
```

## 📊 Interpreting Diagnostic Output

### ✅ Green Check - Passed
Everything is working correctly for this check.

### ❌ Red X - Failed
Issue detected that needs attention.

### ⚠️ Yellow Warning - Caution
Potential issue or non-critical problem.

### 💡 Blue Info - Suggestion
Helpful information or optimization opportunity.

### 🤖 AUTO - Safe Automatic Fix
Can be applied automatically without risk.

### 👤 MANUAL - Requires User Action
Needs manual intervention or confirmation.

## 🔗 Reference Documentation

- **Common Issues**: `references/common-issues.md`
  - Dev server problems
  - Dependency conflicts
  - Runtime errors
  - Asset loading
  - Routing issues
  - Network problems
  - Environment config
  - Build configuration

- **Console Error Patterns**: `references/console-error-patterns.md`
  - React-specific errors
  - Module resolution
  - Network errors
  - Type errors
  - Memory issues
  - Build-time errors
  - Framework-specific errors

## 💻 Framework-Specific Notes

### React
- Check for hydration mismatches
- Verify hooks are called correctly
- Ensure keys on list items
- Watch for state updates during render

### Docusaurus
- Use BrowserOnly for client-only code
- Check swizzled components
- Verify MDX syntax in markdown
- Ensure proper base URL config

### Vite
- Check vite.config.js for base path
- Verify proxy configuration
- Ensure environment variables use VITE_ prefix
- Check for ESM compatibility

### Webpack
- Verify webpack.config.js exists
- Check publicPath setting
- Ensure loaders are configured
- Verify resolve.alias settings

## 🎓 Best Practices

1. **Run diagnostics first** - Don't guess, measure
2. **Fix one thing at a time** - Easier to identify what worked
3. **Restart after changes** - Many fixes need server restart
4. **Check browser console** - Frontend errors show there
5. **Read error messages** - They usually tell you what's wrong
6. **Use version control** - Commit before major changes
7. **Document fixes** - Help future you and teammates

## 📞 When to Escalate

If after running diagnostics and applying fixes you still have issues:

1. Check project-specific documentation
2. Review recent code changes (git log)
3. Ask team members if they've seen similar issues
4. Search error messages online
5. Check framework/library issue trackers
6. Consider filing a bug report if it's a tool issue

---

**Last Updated**: 2026-02-24
**Skill Version**: 1.0.0