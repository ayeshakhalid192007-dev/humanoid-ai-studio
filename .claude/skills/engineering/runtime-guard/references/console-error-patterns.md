# Browser Console Error Patterns

## React-Specific Errors

### Hydration Mismatch
**Pattern:** "Hydration failed because the initial UI does not match what was rendered on the server"
**Cause:** Server-rendered HTML differs from client-rendered HTML
**Common Triggers:**
- Using browser-only APIs during SSR (window, document, localStorage)
- Date/time rendering without timezone handling
- Random values or IDs generated differently on server/client
- Conditional rendering based on client-only state

**Fix:**
```jsx
// Bad
const Component = () => {
  const data = localStorage.getItem('key');
  return <div>{data}</div>;
};

// Good
const Component = () => {
  const [data, setData] = useState(null);
  useEffect(() => {
    setData(localStorage.getItem('key'));
  }, []);
  return <div>{data}</div>;
};
```

### Invalid Hook Call
**Pattern:** "Invalid hook call. Hooks can only be called inside of the body of a function component"
**Cause:** Hooks called outside React component or in wrong order
**Common Triggers:**
- Multiple React versions in node_modules
- Hooks called conditionally or in loops
- Hooks called in regular functions

**Fix:**
```jsx
// Bad
if (condition) {
  useState(0);
}

// Good
const [state, setState] = useState(0);
if (condition) {
  setState(1);
}
```

### Missing Key Prop
**Pattern:** "Warning: Each child in a list should have a unique 'key' prop"
**Cause:** Array items rendered without unique keys
**Fix:**
```jsx
// Bad
{items.map(item => <div>{item.name}</div>)}

// Good
{items.map(item => <div key={item.id}>{item.name}</div>)}
```

### Cannot Update During Render
**Pattern:** "Cannot update a component while rendering a different component"
**Cause:** State update triggered during render phase
**Fix:**
```jsx
// Bad
const Component = () => {
  setParentState(value); // Called during render
  return <div>Content</div>;
};

// Good
const Component = () => {
  useEffect(() => {
    setParentState(value);
  }, []);
  return <div>Content</div>;
};
```

## Module Resolution Errors

### Cannot Find Module
**Pattern:** "Module not found: Error: Can't resolve 'module-name'"
**Cause:** Missing dependency or incorrect import path
**Diagnosis Steps:**
1. Check if package is in package.json
2. Verify node_modules contains the package
3. Check import path spelling and case sensitivity
4. Verify file extension if importing local file

**Fix:**
```bash
npm install module-name
# or fix import path
```

### Unexpected Token
**Pattern:** "Unexpected token '<' or 'export'"
**Cause:** Non-transpiled code or incorrect file type
**Common Triggers:**
- Importing HTML file as JavaScript
- ES6 syntax in non-transpiled environment
- Missing babel/webpack configuration

**Fix:**
- Check import statements for correct file types
- Verify babel configuration includes necessary presets
- Ensure webpack loaders are configured for file types

## Network Errors

### Failed to Fetch
**Pattern:** "TypeError: Failed to fetch"
**Cause:** Network request failed (CORS, network down, wrong URL)
**Diagnosis:**
- Check Network tab for request details
- Verify API endpoint URL
- Check CORS headers
- Confirm backend is running

**Fix:**
```javascript
// Add error handling
fetch(url)
  .then(res => res.json())
  .catch(err => {
    console.error('Fetch failed:', err);
    // Handle error appropriately
  });
```

### CORS Policy Error
**Pattern:** "Access to fetch at 'URL' from origin 'ORIGIN' has been blocked by CORS policy"
**Cause:** Backend not allowing frontend origin
**Fix Options:**
1. Configure CORS on backend
2. Use development proxy
3. Add CORS headers to API responses

## Type Errors

### Cannot Read Property of Undefined
**Pattern:** "TypeError: Cannot read property 'X' of undefined"
**Cause:** Accessing property on undefined/null object
**Common Scenarios:**
- API data not loaded yet
- Optional chaining not used
- Incorrect data structure assumptions

**Fix:**
```javascript
// Bad
const value = obj.nested.property;

// Good
const value = obj?.nested?.property ?? defaultValue;
```

### X is Not a Function
**Pattern:** "TypeError: X is not a function"
**Cause:** Calling non-function as function
**Common Triggers:**
- Incorrect import (default vs named)
- Overwriting function with non-function value
- Calling method on wrong object type

**Fix:**
```javascript
// Check import type
import { namedExport } from 'module'; // Named export
import defaultExport from 'module';   // Default export

// Verify function exists
if (typeof obj.method === 'function') {
  obj.method();
}
```

## Asset Loading Errors

### Failed to Load Resource
**Pattern:** "GET http://localhost:3000/path/to/asset 404 (Not Found)"
**Cause:** Asset path incorrect or file missing
**Diagnosis:**
- Check file exists in expected location
- Verify path is correct (relative vs absolute)
- Check base URL configuration
- Ensure asset is in public folder or properly imported

**Fix:**
```javascript
// For images in public folder
<img src="/images/logo.png" />

// For images in src folder (Vite/Webpack)
import logo from './assets/logo.png';
<img src={logo} />
```

### MIME Type Mismatch
**Pattern:** "Refused to execute script from 'URL' because its MIME type ('text/html') is not executable"
**Cause:** Server returning HTML instead of expected file type
**Common Triggers:**
- SPA routing not configured (404 returns index.html)
- Incorrect base path in production
- Server misconfiguration

**Fix:**
- Configure server for SPA routing
- Set correct base path in build config
- Verify server MIME type configuration

## Memory and Performance

### Maximum Call Stack Size Exceeded
**Pattern:** "RangeError: Maximum call stack size exceeded"
**Cause:** Infinite recursion or very deep call stack
**Common Triggers:**
- Recursive function without base case
- Circular dependencies
- Infinite re-render loop

**Fix:**
```javascript
// Bad - infinite recursion
const Component = () => {
  setState(value); // Causes re-render, which calls setState again
  return <div>Content</div>;
};

// Good
const Component = () => {
  useEffect(() => {
    setState(value);
  }, []); // Only runs once
  return <div>Content</div>;
};
```

### Memory Leak Warning
**Pattern:** "Warning: Can't perform a React state update on an unmounted component"
**Cause:** Async operation completing after component unmounts
**Fix:**
```javascript
useEffect(() => {
  let isMounted = true;

  fetchData().then(data => {
    if (isMounted) {
      setState(data);
    }
  });

  return () => {
    isMounted = false;
  };
}, []);
```

## Build-Time Errors

### Out of Memory
**Pattern:** "JavaScript heap out of memory"
**Cause:** Build process exceeding memory limit
**Fix:**
```bash
# Increase Node memory limit
NODE_OPTIONS=--max_old_space_size=4096 npm run build
```

### Syntax Error in Build
**Pattern:** "SyntaxError: Unexpected token"
**Cause:** Invalid JavaScript syntax or unsupported feature
**Fix:**
- Check for syntax errors in code
- Verify babel configuration supports used features
- Ensure target browsers support features or add polyfills

## Docusaurus-Specific Errors

### BrowserOnly Required
**Pattern:** "ReferenceError: window is not defined"
**Cause:** Using browser APIs during SSR
**Fix:**
```jsx
import BrowserOnly from '@docusaurus/BrowserOnly';

<BrowserOnly>
  {() => <ComponentUsingBrowserAPIs />}
</BrowserOnly>
```

### Theme Component Not Found
**Pattern:** "Error: Unable to find theme component"
**Cause:** Swizzled component path incorrect
**Fix:**
- Verify swizzled component is in correct location
- Check component name matches exactly
- Ensure proper export from swizzled component

### MDX Compilation Error
**Pattern:** "Error: MDX compilation failed"
**Cause:** Invalid MDX syntax in markdown files
**Fix:**
- Check for unclosed JSX tags
- Verify JSX expressions are valid
- Ensure proper escaping of special characters