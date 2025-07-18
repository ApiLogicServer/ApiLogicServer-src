#!/bin/bash

# PostgreSQL-only BLT test runner using the existing env.py configuration system
# This script leverages the built-in BLT configuration system

echo "🚀 PostgreSQL-only BLT Test Runner"
echo "=================================="
echo "Using the existing env.py configuration system for selective testing."
echo ""

# Navigate to the test directory
cd /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/tests/build_and_test

# Check if backup exists
if [ -f "env_backup.py" ]; then
    echo "⚠️  Found existing env_backup.py - restoring it first"
    cp env_backup.py env.py
fi

# Backup current env.py
echo "📋 Backing up current env.py to env_backup.py"
cp env.py env_backup.py

# Use PostgreSQL-only configuration
echo "🔧 Applying PostgreSQL-only configuration"
cp env_postgres_only.py env.py

# Run the BLT test (will only run PostgreSQL tests due to config)
echo "🚀 Running BLT with PostgreSQL-only configuration..."
echo ""
python3 build_load_and_test.py

# Restore original configuration
echo ""
echo "🔄 Restoring original env.py configuration"
cp env_backup.py env.py
rm env_backup.py

echo ""
echo "✅ PostgreSQL-only BLT test completed!"
echo ""
echo "Files used:"
echo "  - env_postgres_only.py (PostgreSQL-only configuration)"
echo "  - build_load_and_test.py (existing BLT system)"
echo ""
echo "The existing BLT system is much more comprehensive than custom scripts."
