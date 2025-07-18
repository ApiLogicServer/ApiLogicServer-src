#!/usr/bin/env python3
"""
Test script to verify that the PostgreSQL driver compatibility fix works correctly.
This script tests the conditional imports for different Python versions.
"""

import sys
import importlib.util

def test_psycopg_imports():
    """Test that the correct PostgreSQL driver is available based on Python version."""
    
    python_version = sys.version_info
    print(f"Python version: {python_version}")
    
    # Check if we're on Python 3.13 or higher
    if python_version >= (3, 13):
        print("Python 3.13+ detected - testing psycopg3 import...")
        
        try:
            import psycopg
            print("✓ psycopg3 imported successfully")
            
            # Test basic functionality
            print(f"✓ psycopg version: {psycopg.__version__}")
            
            # Test that psycopg2 is NOT available (should fail)
            try:
                import psycopg2
                print("✗ ERROR: psycopg2 should not be available on Python 3.13+")
                return False
            except ImportError:
                print("✓ psycopg2 correctly not available on Python 3.13+")
                
        except ImportError as e:
            print(f"✗ ERROR: psycopg3 import failed: {e}")
            return False
            
    else:
        print("Python <3.13 detected - testing psycopg2 import...")
        
        try:
            import psycopg2
            print("✓ psycopg2 imported successfully")
            
            # Test basic functionality
            print(f"✓ psycopg2 version: {psycopg2.__version__}")
            
        except ImportError as e:
            print(f"✗ ERROR: psycopg2 import failed: {e}")
            return False
    
    return True

def test_requirements_format():
    """Test that requirements files have the correct conditional format."""
    
    requirements_files = [
        "requirements.txt",
        "api_logic_server_cli/prototypes/base/venv_setup/requirements-no-cli.txt",
        "api_logic_server_cli/prototypes/manager/system/app_model_editor/venv_setup/requirements-no-cli.txt",
        "api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_docs_logic/venv_setup/requirements-no-cli.txt"
    ]
    
    expected_lines = [
        "psycopg2-binary>=2.9.5; python_version < '3.13'",
        "psycopg[binary]>=3.1.0; python_version >= '3.13'"
    ]
    
    print("\nTesting requirements files format...")
    
    for req_file in requirements_files:
        try:
            with open(req_file, 'r') as f:
                content = f.read()
            
            has_both_lines = all(line in content for line in expected_lines)
            
            if has_both_lines:
                print(f"✓ {req_file} has correct conditional psycopg dependencies")
            else:
                print(f"✗ {req_file} missing conditional psycopg dependencies")
                return False
                
        except FileNotFoundError:
            print(f"✗ {req_file} not found")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing PostgreSQL driver compatibility fix...")
    print("=" * 60)
    
    success = True
    
    # Test imports
    success &= test_psycopg_imports()
    
    # Test requirements format
    success &= test_requirements_format()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! PostgreSQL driver compatibility fix is working.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)
