#!/usr/bin/env python3
"""
Runtime Guard - Automated Fix Suggester
Analyzes common frontend issues and suggests automated fixes
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class RuntimeGuard:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.fixes = []

    def check_node_modules(self) -> Tuple[bool, str]:
        """Check if node_modules exists and is healthy"""
        node_modules = self.project_root / "node_modules"

        if not node_modules.exists():
            return False, "node_modules directory missing"

        # Check if it has reasonable content
        try:
            module_count = len(list(node_modules.iterdir()))
            if module_count < 5:
                return False, f"node_modules appears incomplete ({module_count} packages)"
            return True, f"node_modules exists with {module_count} packages"
        except Exception as e:
            return False, f"Error reading node_modules: {str(e)}"

    def check_package_files(self) -> Tuple[bool, str]:
        """Check package.json and package-lock.json"""
        pkg_json = self.project_root / "package.json"
        pkg_lock = self.project_root / "package-lock.json"

        if not pkg_json.exists():
            return False, "package.json missing"

        if not pkg_lock.exists():
            return False, "package-lock.json missing"

        # Check if files have content
        try:
            with open(pkg_json) as f:
                pkg_data = json.load(f)
                if not pkg_data.get("dependencies") and not pkg_data.get("devDependencies"):
                    return False, "package.json has no dependencies"

            return True, "Package files exist and valid"
        except json.JSONDecodeError:
            return False, "package.json is not valid JSON"
        except Exception as e:
            return False, f"Error reading package files: {str(e)}"

    def check_env_file(self) -> Tuple[bool, str]:
        """Check for .env file"""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_file.exists():
            if env_example.exists():
                return False, ".env missing but .env.example exists"
            return False, ".env file missing"

        try:
            with open(env_file) as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                var_count = len([l for l in lines if '=' in l])
                return True, f".env exists with {var_count} variables"
        except Exception as e:
            return False, f"Error reading .env: {str(e)}"

    def check_index_html(self) -> Tuple[bool, str]:
        """Check for index.html in common locations"""
        common_paths = [
            self.project_root / "index.html",
            self.project_root / "public" / "index.html",
            self.project_root / "dist" / "index.html",
            self.project_root / "build" / "index.html",
        ]

        for path in common_paths:
            if path.exists():
                # Check for root element
                try:
                    with open(path) as f:
                        content = f.read()
                        if 'id="root"' in content or 'id="app"' in content:
                            return True, f"index.html found at {path.relative_to(self.project_root)}"
                        else:
                            return False, f"index.html found but missing root element at {path.relative_to(self.project_root)}"
                except Exception as e:
                    return False, f"Error reading index.html: {str(e)}"

        return False, "index.html not found in common locations"

    def check_build_config(self) -> Tuple[bool, str]:
        """Check for build configuration files"""
        config_files = [
            "vite.config.js",
            "vite.config.ts",
            "webpack.config.js",
            "rollup.config.js",
            "docusaurus.config.js",
        ]

        found_configs = []
        for config in config_files:
            if (self.project_root / config).exists():
                found_configs.append(config)

        if not found_configs:
            return False, "No build configuration file found"

        return True, f"Build config found: {', '.join(found_configs)}"

    def suggest_fixes(self):
        """Generate fix suggestions based on detected issues"""
        for issue in self.issues:
            if "node_modules" in issue.lower() and "missing" in issue.lower():
                self.fixes.append({
                    "issue": issue,
                    "fix": "npm install",
                    "description": "Install dependencies",
                    "safe_auto": True
                })

            elif "node_modules" in issue.lower() and "incomplete" in issue.lower():
                self.fixes.append({
                    "issue": issue,
                    "fix": "rm -rf node_modules package-lock.json && npm install",
                    "description": "Clean reinstall dependencies",
                    "safe_auto": False
                })

            elif ".env missing" in issue.lower() and ".env.example" in issue.lower():
                self.fixes.append({
                    "issue": issue,
                    "fix": "cp .env.example .env",
                    "description": "Copy .env.example to .env",
                    "safe_auto": True
                })

            elif "package-lock.json missing" in issue.lower():
                self.fixes.append({
                    "issue": issue,
                    "fix": "npm install",
                    "description": "Generate package-lock.json",
                    "safe_auto": True
                })

    def run_diagnostics(self) -> Dict:
        """Run all diagnostic checks"""
        print("🔍 Running Runtime Guard Diagnostics...\n")

        checks = [
            ("Node Modules", self.check_node_modules),
            ("Package Files", self.check_package_files),
            ("Environment", self.check_env_file),
            ("Index HTML", self.check_index_html),
            ("Build Config", self.check_build_config),
        ]

        results = {
            "passed": [],
            "failed": [],
            "total": len(checks)
        }

        for name, check_func in checks:
            success, message = check_func()

            if success:
                print(f"✅ {name}: {message}")
                results["passed"].append({"check": name, "message": message})
            else:
                print(f"❌ {name}: {message}")
                results["failed"].append({"check": name, "message": message})
                self.issues.append(message)

        print(f"\n📊 Results: {len(results['passed'])}/{results['total']} checks passed\n")

        if self.issues:
            print("🔧 Generating fix suggestions...\n")
            self.suggest_fixes()

            if self.fixes:
                print("💡 Suggested Fixes:\n")
                for i, fix in enumerate(self.fixes, 1):
                    auto_label = "🤖 AUTO" if fix["safe_auto"] else "👤 MANUAL"
                    print(f"{i}. {auto_label} - {fix['description']}")
                    print(f"   Issue: {fix['issue']}")
                    print(f"   Fix: {fix['fix']}\n")
        else:
            print("✅ All checks passed! No issues detected.\n")

        return results

def main():
    """Main entry point"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    guard = RuntimeGuard(project_root)
    results = guard.run_diagnostics()

    # Exit with error code if any checks failed
    sys.exit(0 if not results["failed"] else 1)

if __name__ == "__main__":
    main()
