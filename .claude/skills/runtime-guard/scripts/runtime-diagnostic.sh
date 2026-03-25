#!/bin/bash
# runtime-guard diagnostic script
# Performs comprehensive frontend runtime verification

echo "🔍 Runtime Guard - Frontend Diagnostic Tool"
echo "=========================================="

# Check 1: Dev Server Status
echo
echo "📋 1. Checking Dev Server Status"
if lsof -i :3000 > /dev/null; then
    echo "✅ Port 3000 is in use (likely development server running)"
    # Try to check if it's responding
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Development server responding on port 3000"
    else
        echo "❌ Development server not responding on port 3000"
    fi
else
    echo "❌ Port 3000 is not in use"
fi

if lsof -i :8080 > /dev/null; then
    echo "✅ Port 8080 is in use"
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ Server responding on port 8080"
    else
        echo "❌ Server not responding on port 8080"
    fi
else
    echo "❌ Port 8080 is not in use"
fi

# Check 2: Node Modules Integrity
echo
echo "📋 2. Checking Dependency Integrity"
if [ -d "node_modules" ]; then
    echo "✅ node_modules directory exists"
    MODULE_COUNT=$(ls node_modules | wc -l)
    echo "📊 Found ${MODULE_COUNT} top-level packages in node_modules"
else
    echo "❌ node_modules directory missing - dependencies may need to be installed"
fi

if [ -f "package.json" ] && [ -f "package-lock.json" ]; then
    echo "✅ package.json and package-lock.json both exist"
    # Quick check if they're reasonably synchronized (both files exist and have content)
    PKG_SIZE=$(wc -c < package.json)
    LOCK_SIZE=$(wc -c < package-lock.json)
    if [ $PKG_SIZE -gt 10 ] && [ $LOCK_SIZE -gt 10 ]; then
        echo "✅ Both package files have content"
    else
        echo "⚠️ package.json or package-lock.json appears to be empty"
    fi
else
    echo "❌ Missing package.json or package-lock.json files"
fi

# Check 3: Check for build artifacts
echo
echo "📋 3. Checking Build Artifacts"
if [ -f "dist/index.html" ] || [ -f "build/index.html" ] || [ -f "public/index.html" ]; then
    echo "✅ index.html found in common build directories"
else
    echo "⚠️ index.html not found in common build directories"
fi

# Check 4: Environment Variables
echo
echo "📋 4. Checking Environment Variables"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    ENV_VARS=$(grep -v '^#' .env | grep '=' | wc -l)
    echo "📊 Found ${ENV_VARS} environment variable definitions in .env"
else
    echo "⚠️ .env file not found or in a different location"
fi

# Check 5: Common Configuration Files
echo
echo "📋 5. Checking Configuration Files"
CONFIG_FILES=("package.json" "webpack.config.js" "vite.config.js" "rollup.config.js" "babel.config.js")
for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ ${config} found"
    else
        echo "💡 ${config} not found (not necessarily an issue depending on your stack)"
    fi
done

# Check 6: Frontend Framework Detection
echo
echo "📋 6. Detecting Frontend Framework"
FRAMEWORKS=("@angular/core" "react" "vue" "svelte" "preact")
for framework in "${FRAMEWORKS[@]}"; do
    if grep -q "$framework" package.json 2>/dev/null; then
        echo "✅ ${framework} detected in package.json"
    fi
done

echo
echo "✅ Initial diagnostic complete!"
echo "⚠️  This is a high-level check - deeper inspection would need to check browser console logs and detailed runtime errors."