#!/usr/bin/env python3
"""
PostgreSQL-only BLT test using the existing env.py configuration system.
This script temporarily swaps the env.py file to use PostgreSQL-only settings.
"""

import os
import sys
import shutil
from pathlib import Path

# Set up paths
script_dir = Path(__file__).parent
original_env = script_dir / "env.py"
postgres_env = script_dir / "env_postgres_only.py"
backup_env = script_dir / "env_backup.py"

def run_postgres_only_blt():
    """Run BLT tests with PostgreSQL-only configuration"""
    
    print("🚀 Starting PostgreSQL-only BLT tests for Python 3.13 compatibility")
    print("=" * 70)
    
    # Backup original env.py
    if original_env.exists():
        shutil.copy2(original_env, backup_env)
        print(f"✅ Backed up original env.py to {backup_env}")
    
    try:
        # Replace env.py with PostgreSQL-only version
        shutil.copy2(postgres_env, original_env)
        print(f"✅ Replaced env.py with PostgreSQL-only configuration")
        
        # Import and run the main BLT test
        print("\n🔧 Running BLT tests...")
        print("-" * 40)
        
        # Add the directory to Python path so we can import
        sys.path.insert(0, str(script_dir))
        
        # Import the main BLT module
        import build_load_and_test
        
        print("\n✅ PostgreSQL-only BLT tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error running PostgreSQL-only BLT tests: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restore original env.py
        if backup_env.exists():
            shutil.copy2(backup_env, original_env)
            backup_env.unlink()  # Remove backup
            print(f"\n✅ Restored original env.py")
        
    return True

if __name__ == "__main__":
    print("PostgreSQL-only BLT Test Runner")
    print("This will run only PostgreSQL-related tests from the full BLT suite.")
    print()
    
    # Check if PostgreSQL-only config exists
    if not postgres_env.exists():
        print(f"❌ Error: {postgres_env} not found")
        sys.exit(1)
    
    success = run_postgres_only_blt()
    sys.exit(0 if success else 1)
