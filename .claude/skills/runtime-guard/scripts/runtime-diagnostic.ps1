# runtime-guard diagnostic script (PowerShell version)
# Performs comprehensive frontend runtime verification

Write-Output "🔍 Runtime Guard - Frontend Diagnostic Tool"
Write-Output "=========================================="

# Check 1: Dev Server Status
Write-Output ""
Write-Output "📋 1. Checking Dev Server Status"

# Check if ports are in use
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($port3000) {
    Write-Output "✅ Port 3000 is in use (likely development server running)"
    # Try to check if it's responding (simplified - would need proper HTTP test in real implementation)
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Output "✅ Development server responding on port 3000"
    }
    catch {
        Write-Output "❌ Development server not responding on port 3000"
    }
} else {
    Write-Output "❌ Port 3000 is not in use"
}

if ($port8080) {
    Write-Output "✅ Port 8080 is in use"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -ErrorAction Stop
        Write-Output "✅ Server responding on port 8080"
    }
    catch {
        Write-Output "❌ Server not responding on port 8080"
    }
} else {
    Write-Output "❌ Port 8080 is not in use"
}

# Check 2: Node Modules Integrity
Write-Output ""
Write-Output "📋 2. Checking Dependency Integrity"

if (Test-Path "node_modules") {
    Write-Output "✅ node_modules directory exists"
    $moduleCount = (Get-ChildItem "node_modules" | Measure-Object).Count
    Write-Output "📊 Found $moduleCount top-level packages in node_modules"
} else {
    Write-Output "❌ node_modules directory missing - dependencies may need to be installed"
}

if (Test-Path "package.json" -PathType Leaf -and Test-Path "package-lock.json" -PathType Leaf) {
    Write-Output "✅ package.json and package-lock.json both exist"
    $pkgSize = (Get-Item "package.json").Length
    $lockSize = (Get-Item "package-lock.json").Length
    if ($pkgSize -gt 10 -and $lockSize -gt 10) {
        Write-Output "✅ Both package files have content"
    } else {
        Write-Output "⚠️ package.json or package-lock.json appears to be empty"
    }
} else {
    Write-Output "❌ Missing package.json or package-lock.json files"
}

# Check 3: Check for build artifacts
Write-Output ""
Write-Output "📋 3. Checking Build Artifacts"

$commonIndexPaths = @("dist/index.html", "build/index.html", "public/index.html")
$indexFound = $false
foreach ($indexPath in $commonIndexPaths) {
    if (Test-Path $indexPath) {
        Write-Output "✅ index.html found at $indexPath"
        $indexFound = $true
    }
}

if (-not $indexFound) {
    Write-Output "⚠️ index.html not found in common build directories"
}

# Check 4: Environment Variables
Write-Output ""
Write-Output "📋 4. Checking Environment Variables"

if (Test-Path ".env") {
    Write-Output "✅ .env file exists"
    $envVars = Get-Content .env | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | Measure-Object
    Write-Output "📊 Found $($envVars.Count) environment variable definitions in .env"
} else {
    Write-Output "⚠️ .env file not found or in a different location"
}

# Check 5: Common Configuration Files
Write-Output ""
Write-Output "📋 5. Checking Configuration Files"

$configFiles = @("package.json", "webpack.config.js", "vite.config.js", "rollup.config.js", "babel.config.js")
foreach ($config in $configFiles) {
    if (Test-Path $config) {
        Write-Output "✅ $config found"
    } else {
        Write-Output "💡 $config not found (not necessarily an issue depending on your stack)"
    }
}

# Check 6: Frontend Framework Detection
Write-Output ""
Write-Output "📋 6. Detecting Frontend Framework"

$frameworks = @("@angular/core", "react", "vue", "svelte", "preact")
if (Test-Path "package.json") {
    $pkgContent = Get-Content "package.json" -Raw | ConvertFrom-Json

    foreach ($framework in $frameworks) {
        $hasDep = $false
        if ($pkgContent.dependencies) {
            $hasDep = $pkgContent.dependencies.PSObject.Properties.Name -contains $framework
        }
        if (-not $hasDep -and $pkgContent.devDependencies) {
            $hasDep = $pkgContent.devDependencies.PSObject.Properties.Name -contains $framework
        }

        if ($hasDep) {
            Write-Output "✅ $framework detected in package.json"
        }
    }
}

Write-Output ""
Write-Output "✅ Initial diagnostic complete!"
Write-Output "⚠️  This is a high-level check - deeper inspection would need to check browser console logs and detailed runtime errors."