# Common Frontend Runtime Issues Reference

## Dev Server Issues

### Port Already in Use
**Symptoms:** Server fails to start with "EADDRINUSE" error
**Diagnosis:** Another process is using the target port
**Fix:**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Server Not Responding
**Symptoms:** Server starts but doesn't respond to requests
**Diagnosis:** Firewall blocking, wrong host binding, or configuration issue
**Fix:**
- Check firewall settings
- Ensure server binds to `0.0.0.0` or `localhost`
- Verify `vite.config.js` or `webpack.config.js` server settings

## Dependency Issues

### Missing node_modules
**Symptoms:** Import errors, module not found
**Diagnosis:** Dependencies not installed
**Fix:**
```bash
npm install
# or
yarn install
```

### Corrupted Dependencies
**Symptoms:** Unexpected errors, version mismatches
**Diagnosis:** node_modules out of sync with package-lock.json
**Fix:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Peer Dependency Conflicts
**Symptoms:** Warnings about unmet peer dependencies
**Diagnosis:** Version incompatibilities between packages
**Fix:**
```bash
npm install --legacy-peer-deps
# or update conflicting packages
```

## Runtime JavaScript Errors

### Undefined is not an object
**Symptoms:** TypeError in console
**Diagnosis:** Accessing property on undefined/null object
**Fix:**
- Add null checks: `obj?.property`
- Ensure data is loaded before rendering
- Check async data fetching logic

### Cannot read property of undefined
**Symptoms:** Runtime error when accessing nested properties
**Diagnosis:** Object structure doesn't match expected shape
**Fix:**
- Use optional chaining: `obj?.nested?.property`
- Add default values: `const value = obj?.property ?? defaultValue`
- Validate data structure after API calls

### React Component Errors
**Symptoms:** "Error: Minified React error #..."
**Diagnosis:** React-specific runtime errors
**Fix:**
- Check component lifecycle methods
- Ensure hooks are called in correct order
- Verify props are passed correctly
- Check for missing keys in lists

## Asset Loading Issues

### 404 for Static Assets
**Symptoms:** Images, CSS, or JS files return 404
**Diagnosis:** Incorrect asset paths or base URL misconfiguration
**Fix:**
- Check `base` in `vite.config.js` or `publicPath` in webpack
- Verify asset paths are relative or use correct base URL
- Ensure assets are in `public/` or properly imported

### MIME Type Errors
**Symptoms:** "Refused to execute script... MIME type"
**Diagnosis:** Server serving wrong content type
**Fix:**
- Configure server to serve correct MIME types
- Check `.htaccess` or server configuration
- Verify file extensions are correct

### Font Loading Failures
**Symptoms:** Fonts not displaying, fallback fonts used
**Diagnosis:** CORS issues or incorrect font paths
**Fix:**
- Add CORS headers for font files
- Verify font file paths in CSS
- Check font-face declarations

## Routing Issues

### Blank Page on Root Route
**Symptoms:** Application loads but shows blank page
**Diagnosis:** Root route not configured or component not rendering
**Fix:**
- Check router configuration for `/` route
- Verify root component is exported correctly
- Check for errors in root component render method
- Ensure mounting element exists in index.html

### 404 on Page Refresh
**Symptoms:** Direct URL access or refresh returns 404
**Diagnosis:** Server not configured for SPA routing
**Fix:**
- Configure server to serve index.html for all routes
- Add rewrite rules in `.htaccess` or nginx config
- For Netlify: add `_redirects` file with `/* /index.html 200`

### Nested Routes Not Working
**Symptoms:** Child routes don't render
**Diagnosis:** Missing `<Outlet />` or incorrect route nesting
**Fix:**
- Add `<Outlet />` in parent route component
- Verify route hierarchy in router configuration
- Check for conflicting route paths

## Network and API Issues

### CORS Errors
**Symptoms:** "Access-Control-Allow-Origin" error in console
**Diagnosis:** Backend not allowing frontend origin
**Fix:**
- Configure CORS on backend server
- Add proxy in `vite.config.js` or `webpack.config.js`
- Use development proxy for local testing

### Failed API Requests
**Symptoms:** Network errors, 500/502/503 responses
**Diagnosis:** Backend not running or incorrect API URL
**Fix:**
- Verify backend server is running
- Check API base URL in environment variables
- Validate API endpoint paths
- Check network tab for request details

### Timeout Errors
**Symptoms:** Requests hang or timeout
**Diagnosis:** Slow backend or network issues
**Fix:**
- Increase timeout settings
- Add loading states in UI
- Implement request cancellation
- Check backend performance

## Environment Configuration

### Missing Environment Variables
**Symptoms:** Undefined values, features not working
**Diagnosis:** .env file missing or not loaded
**Fix:**
- Create `.env` file with required variables
- Ensure variables are prefixed correctly (e.g., `VITE_`, `REACT_APP_`)
- Restart development server after changes
- Check `.env.example` for required variables

### Wrong Environment Loaded
**Symptoms:** Production config in development or vice versa
**Diagnosis:** Environment mode not set correctly
**Fix:**
- Check `NODE_ENV` value
- Use correct `.env` file (`.env.development`, `.env.production`)
- Verify build scripts set correct mode

## Build Configuration Issues

### Incorrect Base Path
**Symptoms:** Assets 404 in production, routing broken
**Diagnosis:** Base URL not matching deployment path
**Fix:**
- Set `base` in `vite.config.js` to match deployment path
- For GitHub Pages: `base: '/repo-name/'`
- For subdirectory: `base: '/subdirectory/'`

### Build Output Issues
**Symptoms:** Build succeeds but deployment fails
**Diagnosis:** Output directory misconfigured
**Fix:**
- Verify `build.outDir` in config matches deployment expectations
- Check `.gitignore` doesn't exclude build files
- Ensure build artifacts are committed or uploaded correctly

### Module Resolution Errors
**Symptoms:** "Cannot find module" in production build
**Diagnosis:** Import paths not resolved correctly
**Fix:**
- Use path aliases consistently
- Configure `resolve.alias` in build config
- Avoid mixing default and named imports incorrectly

## HTML and Mounting Issues

### Root Element Not Found
**Symptoms:** "Target container is not a DOM element"
**Diagnosis:** Mounting element missing or wrong ID
**Fix:**
- Verify `<div id="root">` exists in index.html
- Check mounting code uses correct selector
- Ensure scripts load after DOM is ready

### Script Loading Order
**Symptoms:** "X is not defined" errors
**Diagnosis:** Scripts loading in wrong order
**Fix:**
- Use `type="module"` for ES modules
- Add `defer` or `async` attributes appropriately
- Ensure dependencies load before dependent code

## Cache and Service Worker Issues

### Stale Content After Deploy
**Symptoms:** Old version loads after deployment
**Diagnosis:** Browser or service worker caching
**Fix:**
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Update service worker to skip waiting
- Add cache-busting query parameters

### Service Worker Conflicts
**Symptoms:** Unexpected caching behavior
**Diagnosis:** Service worker intercepting requests incorrectly
**Fix:**
- Unregister service worker in dev tools
- Update service worker cache strategy
- Clear application cache in dev tools