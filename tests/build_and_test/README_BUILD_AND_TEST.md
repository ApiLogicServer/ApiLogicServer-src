# Build and Test (BLT) System

## Overview

The Build and Test (BLT) system is a comprehensive pre-release testing framework for ApiLogicServer. It ensures that the built environment works correctly without contamination from the development environment.

**Key Purpose**: Before release, this system builds the product into a clean environment and runs extensive tests to validate functionality across multiple database types and configurations.

## Architecture

The BLT system follows this structure:

```
ApiLogicServer-dev/
├── org_git/ApiLogicServer-src/           # Source code
│   └── tests/build_and_test/             # BLT scripts and configuration
├── build_and_test/ApiLogicServer/        # Clean build environment
│   ├── venv/                             # Isolated virtual environment
│   ├── tests/                            # Created test projects
│   │   ├── ApiLogicProject/              # Main NW+ project
│   │   ├── postgres/                     # PostgreSQL projects
│   │   ├── classicmodels/                # MySQL projects
│   │   └── ...                           # Other test projects
│   └── dockers/                          # Docker test artifacts
└── clean/ApiLogicServer/                 # Additional clean environment
```

## Core Components

### 1. Main Test Script: `build_load_and_test.py`

The primary test orchestrator that:
- Builds ApiLogicServer from source into a clean environment
- Creates multiple test projects with different database configurations
- Runs comprehensive validation tests
- Generates test reports and logs

### 2. Configuration System: `env.py`

Centralized configuration controlling which tests run:

```python
# Essential tests
do_install_api_logic_server = True    # Build and install from source
do_create_api_logic_project = True    # Create main NW+ project
do_test_api_logic_project = True      # Run Behave tests

# Database-specific tests
do_docker_postgres = True             # PostgreSQL tests
do_docker_mysql = True                # MySQL tests
do_docker_sqlserver = False           # SQL Server tests

# Application tests
do_allocation_test = True             # Allocation sample
do_budget_app_test = True             # Budget app sample
do_other_sqlite_databases = True      # Various SQLite tests
```

### 3. Platform-Specific Configurations

- `env_mac.py` - macOS defaults
- `env_win.py` - Windows defaults  
- `env_linux.py` - Linux defaults
- `env_postgres_only.py` - PostgreSQL-only testing

### 4. Build Scripts

- `build_install.sh` - Unix/Linux/macOS build script
- `cmd_venv.sh` - Virtual environment activation wrapper

## Test Categories

### Core Framework Tests
- **Project Creation**: Validates `ApiLogicServer create` command
- **Model Generation**: Tests database introspection and model creation
- **API Generation**: Validates REST API generation
- **Admin App**: Tests admin interface generation
- **Logic Framework**: Validates business logic execution

### Database Tests
- **SQLite**: Northwind, Allocation, Budget samples
- **PostgreSQL**: Multiple database configurations
- **MySQL**: ClassicModels and other schemas
- **SQL Server**: Enterprise database features
- **Oracle**: Advanced database features

### Advanced Features
- **Multi-Database**: Projects with multiple database connections
- **Authentication**: Security and authorization
- **Optimistic Locking**: Concurrent access control
- **Kafka Integration**: Message queue functionality
- **Docker**: Container-based deployment
- **GenAI**: AI-powered project generation

## Running Tests

### Full Test Suite
```bash
cd tests/build_and_test
python3 build_load_and_test.py
```

### Selective Testing
```bash
# 1. Copy desired configuration
cp env_postgres_only.py env.py

# 2. Run normal BLT (will only run configured tests)
python3 build_load_and_test.py

# 3. Restore original configuration
cp env_backup.py env.py
```

### Quick PostgreSQL-Only Test
```bash
./run_postgres_blt.sh
```

## Test Environment Isolation

### Why Clean Environment Matters
- **No Dev Contamination**: Tests run in isolated environment
- **Realistic Conditions**: Simulates actual user installation
- **Dependency Validation**: Ensures all requirements are properly specified
- **Version Testing**: Validates specific Python/package versions

### Virtual Environment Management
```bash
# The system creates isolated venvs:
build_and_test/ApiLogicServer/venv/     # Main test environment
clean/ApiLogicServer/venv/              # Additional clean environment
```

### Path Management
```python
# Key paths used by BLT system
install_api_logic_server_path = "build_and_test/ApiLogicServer"
api_logic_server_tests_path = "ApiLogicServer-src/tests"
set_venv = "source ${install_api_logic_server_path}/venv/bin/activate"
```

## Pre-Release Validation

The BLT system validates:

1. **Build Process**: Source → wheel → installation
2. **CLI Commands**: All `ApiLogicServer` commands work correctly
3. **Project Templates**: Base templates and customizations
4. **Database Connectivity**: All supported database types
5. **Generated Code**: APIs, models, and admin interfaces
6. **Business Logic**: Rule execution and validation
7. **Security**: Authentication and authorization
8. **Performance**: Basic load and stress testing

## Key Learnings and Best Practices

### Environment Management
- Always use isolated virtual environments
- Never run tests in development environment
- Use `cmd_venv.sh` for consistent environment activation
- Validate Python version compatibility (3.8-3.13)

### Database Testing
- Test with actual database servers, not just SQLite
- Use Docker containers for consistent database environments
- Test both local and remote database connections
- Validate URL format conversions (e.g., PostgreSQL dialect changes)

### Version Compatibility
- Test across multiple Python versions
- Validate package version compatibility
- Test conditional dependencies (e.g., psycopg2 vs psycopg3)
- Ensure backward compatibility

### Error Handling
- Comprehensive error checking in `check_command()`
- Detailed logging for debugging failures
- Graceful handling of missing dependencies
- Clear error messages for common issues

## Troubleshooting

### Common Issues

1. **Virtual Environment Problems**
   ```bash
   # Check if venv is properly activated
   which python
   pip freeze
   ```

2. **Database Connection Issues**
   ```bash
   # Verify database servers are running
   docker ps
   # Check network connectivity
   ping localhost
   ```

3. **Build Failures**
   ```bash
   # Check for missing dependencies
   pip install --upgrade pip setuptools wheel
   # Verify source code integrity
   git status
   ```

### Test Configuration
- Review `env.py` settings for your environment
- Ensure required databases are running
- Check disk space for test artifacts
- Verify network connectivity for external services

## Customization

### Adding New Tests
1. Add configuration flag to `env.py`
2. Implement test function in `build_load_and_test.py`
3. Add conditional execution logic
4. Update this documentation

### Platform-Specific Adaptations
- Create platform-specific `env_*.py` files
- Adjust path separators and commands
- Handle platform-specific dependencies
- Test on target platforms before release

## Integration with CI/CD

The BLT system is designed to integrate with continuous integration:

```yaml
# Example CI configuration
- name: Run BLT Tests
  run: |
    cd tests/build_and_test
    cp env_ci.py env.py
    python3 build_load_and_test.py
```

## Performance Considerations

- Full test suite takes 30-60 minutes
- Use selective testing for faster iterations
- Parallel test execution where possible
- Clean up test artifacts to manage disk space

## Security Testing

- Authentication and authorization validation
- SQL injection prevention testing
- Cross-site scripting (XSS) protection
- Secure credential handling in tests

## Future Enhancements

- Parallel test execution
- Cloud database testing
- Performance benchmarking
- Automated report generation
- Integration with external monitoring

---

## Appendix: Python Version Upgrades

### Overview

**Python version upgrades are extremely complex and time-consuming** - historically taking a week or more to complete. The BLT system is absolutely critical for validating these upgrades across the entire stack.

### Why Version Upgrades Are So Challenging

1. **Dependency Chain Reactions**: One package change can break dozens of others
2. **Breaking Changes**: New Python versions often deprecate or remove features
3. **Package Compatibility**: Not all packages immediately support new Python versions
4. **Deep Integration**: ApiLogicServer integrates with SQLAlchemy, Flask, database drivers, etc.
5. **Multiple Database Support**: Each database driver may have different compatibility timelines
6. **Template Propagation**: Changes must be applied to all project templates

### Python 3.13 Compatibility Example (July 2025)

The Python 3.13 upgrade required changes across **multiple layers** of the system:

#### 1. **Database Driver Changes**
```python
# OLD (Python < 3.13)
psycopg2-binary>=2.9.5

# NEW (Python >= 3.13) 
psycopg2-binary>=2.9.5; python_version < '3.13'
psycopg[binary]>=3.1.0; python_version >= '3.13'
```

#### 2. **SQLAlchemy Framework Upgrade**
```python
# OLD
SQLAlchemy==1.4.29

# NEW (required for psycopg3 support)
SQLAlchemy>=2.0.15
```

#### 3. **Database URL Dialect Changes**
```python
# OLD URL format
postgresql://user:pass@host/db

# NEW URL format (Python 3.13+)
postgresql+psycopg://user:pass@host/db
```

#### 4. **Package Import Modernization**
```python
# OLD (deprecated)
from pkg_resources import get_distribution

# NEW (Python 3.13+)
from importlib.metadata import version
```

#### 5. **Multi-Layer URL Conversion Logic**

The URL conversion had to be implemented in **4 different places**:

1. **CLI Project Creation** (`api_logic_server.py`)
   ```python
   if sys.version_info >= (3, 13) and db_uri.startswith('postgresql://'):
       db_uri = db_uri.replace('postgresql://', 'postgresql+psycopg://')
   ```

2. **Template Configuration** (`prototypes/base/config/config.py`)
   ```python
   if sys.version_info >= (3, 13) and SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
       SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'postgresql+psycopg://')
   ```

3. **Schema Introspection** (`sqlacodegen_wrapper.py`)
   ```python
   if sys.version_info >= (3, 13) and engine_url.startswith('postgresql://'):
       engine_url = engine_url.replace('postgresql://', 'postgresql+psycopg://')
   ```

4. **Embedded Libraries** (`sqlacodegen/main.py`)
   ```python
   if sys.version_info >= (3, 13) and engine_url.startswith('postgresql://'):
       engine_url = engine_url.replace('postgresql://', 'postgresql+psycopg://')
   ```

#### 6. **Template Requirements Updates**

All project templates required SQLAlchemy version updates:
- `prototypes/base/requirements.txt`
- `prototypes/nw_plus/requirements.txt`
- `prototypes/allocation/requirements.txt`
- `prototypes/BudgetApp/requirements.txt`
- And many more...

#### 7. **Version Number and Documentation Updates**
```python
__version__ = "15.00.50"
recent_changes = "07/17/2024 - 15.00.50: Python 3.13 compatibility fixes - psycopg2→psycopg3, SQLAlchemy 2.0+, pkg_resources→importlib.metadata"
```

**Version Update Convention for `api_logic_server_cli/api_logic_server.py` (lines 15-17):**

1. **Update `__version__`**: Increment version number following semantic versioning
   - Major version (15.x.x): Breaking changes or major new features
   - Minor version (x.00.x): New features, significant enhancements
   - Patch version (x.x.50): Bug fixes, small improvements

2. **Update `recent_changes`**: Add new entry **at the top** of the changelog
   - Format: `"MM/DD/YYYY - VERSION: Brief description of changes"`
   - Keep the most recent ~20 entries for visibility
   - Include key technical details (e.g., "psycopg2→psycopg3, SQLAlchemy 2.0+")

3. **Version Numbering Examples**:
   - `15.00.49` → `15.00.50` (patch: bug fixes)
   - `15.00.50` → `15.01.00` (minor: new features)
   - `15.01.00` → `16.00.00` (major: breaking changes)

**Example update for Python 3.13 compatibility:**
```python
__version__ = "15.00.50"  # Incremented from 15.00.49
recent_changes = \
    f'\n\nRecent Changes:\n' +\
    "\t07/17/2024 - 15.00.50: Python 3.13 compatibility fixes - psycopg2→psycopg3, SQLAlchemy 2.0+, pkg_resources→importlib.metadata \n"\
    "\t07/17/2024 - 15.00.49: venv fix+, ext bldr * fix, copilot vibe tweaks - creation, mcp logic, basic_demo autonums \n"\
    # ... existing entries continue ...
```

### BLT System Validation Process

The BLT system was essential for validating these changes:

1. **Clean Environment Testing**: Ensured no dev environment contamination
2. **Multi-Database Validation**: Tested PostgreSQL, MySQL, SQLite, SQL Server
3. **Project Template Testing**: Validated all templates work with new versions
4. **Backward Compatibility**: Ensured older Python versions still work
5. **Integration Testing**: Full end-to-end project creation and execution

### Lessons Learned from Python 3.13 Upgrade

1. **Conditional Dependencies Are Critical**: Use version-specific requirements
2. **URL Formats Can Change**: Database connection strings may need updates
3. **Package APIs Evolve**: Standard library changes require code updates
4. **Template Propagation**: Changes must cascade through all templates
5. **Multi-Layer Testing**: Test at CLI, template, and runtime levels

### Best Practices for Future Version Upgrades

1. **Start Early**: Begin testing with alpha/beta Python releases
2. **Dependency Mapping**: Create a full dependency tree diagram
3. **Incremental Updates**: Update one major component at a time
4. **Extensive Testing**: Use BLT system for comprehensive validation
5. **Documentation**: Document all changes for future reference
6. **Rollback Plan**: Always have a way to revert changes
7. **Communication**: Coordinate with users about breaking changes

### Version Upgrade Checklist

- [ ] Update main `requirements.txt` with conditional dependencies
- [ ] Update all template `requirements.txt` files
- [ ] Update core framework imports and APIs
- [ ] Update database connection logic
- [ ] Update project templates and prototypes
- [ ] **Update version numbers**: 
  - [ ] Increment `__version__` in `api_logic_server_cli/api_logic_server.py` (line 15)
  - [ ] Add new changelog entry to `recent_changes` (line 17) **at the top**
  - [ ] Follow semantic versioning convention (major.minor.patch)
- [ ] Run full BLT test suite
- [ ] Test on multiple platforms (macOS, Windows, Linux)
- [ ] Test with multiple database types
- [ ] Validate backward compatibility
- [ ] Update CI/CD configurations
- [ ] Prepare migration guide for users

### Timeline Expectations

- **Traditional Approach**: 1-2 weeks of developer time
- **With BLT System**: Still complex, but systematic validation
- **Critical Success Factor**: Comprehensive testing prevents post-release issues

**Remember**: The time invested in thorough version upgrades prevents weeks of post-release bug fixes and user support issues.

## Backward Compatibility Considerations

### Overview

When implementing new Python version support, maintaining backward compatibility is crucial for user adoption and minimizing disruption. The Python 3.13 compatibility implementation serves as a model for handling version transitions gracefully.

### Key Backward Compatibility Principles

#### 1. **Conditional Dependencies**
Use Python version markers in `requirements.txt` to specify different packages for different Python versions:

```python
# Backward compatible dependency specification
psycopg2-binary>=2.9.5; python_version < '3.13'
psycopg[binary]>=3.1.0; python_version >= '3.13'
```

This ensures:
- Python 3.12 systems automatically get `psycopg2-binary`
- Python 3.13+ systems automatically get `psycopg3`
- No manual intervention required during installation

#### 2. **Runtime Version Detection**
Use `sys.version_info` checks to apply version-specific logic only when needed:

```python
import sys

# Only apply PostgreSQL URL conversion for Python 3.13+
if sys.version_info >= (3, 13) and db_uri.startswith('postgresql://'):
    db_uri = db_uri.replace('postgresql://', 'postgresql+psycopg://')
```

This ensures:
- Legacy Python versions continue using existing behavior
- New Python versions get required compatibility changes
- No breaking changes for existing installations

#### 3. **Import Fallbacks**
Implement graceful fallbacks for changed imports:

```python
# Support both old and new import patterns
try:
    from importlib.metadata import version as get_version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import version as get_version
```

#### 4. **Minimum Python Version Policy**
- **Current Policy**: `requires-python = ">=3.10"`
- **Future Updates**: Only increase minimum version with major releases
- **Deprecation Notice**: Provide 6-month warning before dropping support

### Testing Backward Compatibility

#### 1. **Multi-Version Testing**
Test the same branch on multiple Python versions:

```bash
# Python 3.12 testing
python3.12 -m pytest tests/

# Python 3.13 testing  
python3.13 -m pytest tests/

# BLT testing on both versions
python3.12 tests/build_and_test/build_load_and_test.py
python3.13 tests/build_and_test/build_load_and_test.py
```

#### 2. **Dependency Validation**
Verify that conditional dependencies resolve correctly:

```bash
# Test Python 3.12 dependency resolution
python3.12 -c "import psycopg2; print('✓ psycopg2 imported')"

# Test Python 3.13 dependency resolution  
python3.13 -c "import psycopg; print('✓ psycopg3 imported')"
```

#### 3. **Feature Parity Testing**
Ensure all features work identically across Python versions:

```bash
# Test project creation on both versions
python3.12 ApiLogicServer create --project_name=test_312 --db_url=postgresql://...
python3.13 ApiLogicServer create --project_name=test_313 --db_url=postgresql://...

# Compare generated projects
diff -r test_312 test_313
```

### Migration Strategy

#### 1. **Phased Rollout**
- **Phase 1**: Release with backward compatibility maintained
- **Phase 2**: Provide migration tools and documentation
- **Phase 3**: Deprecate old versions with clear timeline

#### 2. **User Communication**
- **Release Notes**: Document compatibility changes clearly
- **Migration Guide**: Provide step-by-step upgrade instructions
- **Support Policy**: Maintain support for previous versions during transition

#### 3. **Fallback Plans**
- **Branch Strategy**: Maintain separate branches for different Python versions if needed
- **Hotfix Policy**: Ensure critical fixes can be backported
- **User Support**: Provide clear guidance for users who cannot upgrade immediately

### Common Pitfalls to Avoid

#### 1. **Hard Python Version Requirements**
❌ **Don't do this:**
```python
# This breaks backward compatibility
if sys.version_info < (3, 13):
    raise RuntimeError("Python 3.13+ required")
```

✅ **Do this instead:**
```python
# Graceful handling with informative messages
if sys.version_info >= (3, 13):
    # Use new features
    pass
else:
    # Use legacy approach
    pass
```

#### 2. **Unconditional New Imports**
❌ **Don't do this:**
```python
# This breaks on older Python versions
from importlib.metadata import version
```

✅ **Do this instead:**
```python
# Backward compatible imports
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
```

#### 3. **Breaking API Changes**
❌ **Don't do this:**
```python
# This breaks existing user code
def create_project(name, db_url, python_version):  # Added required parameter
    pass
```

✅ **Do this instead:**
```python
# Backward compatible API
def create_project(name, db_url, python_version=None):  # Optional parameter
    if python_version is None:
        python_version = detect_python_version()
    pass
```

### Validation Checklist

Before releasing version compatibility changes:

- [ ] **Dependency Resolution**: Verify pip resolves correct packages for each Python version
- [ ] **Import Testing**: Ensure all imports work on target Python versions
- [ ] **Feature Testing**: Validate core functionality works identically
- [ ] **Template Testing**: Check that generated projects work on all versions
- [ ] **Documentation**: Update all relevant documentation
- [ ] **Migration Guide**: Provide clear upgrade instructions
- [ ] **Support Policy**: Define support timeline for previous versions
- [ ] **Rollback Plan**: Ensure ability to revert if issues discovered

### Long-term Considerations

#### 1. **Version Support Policy**
- Support current Python version + 2 previous versions
- Provide 6-month deprecation notice before dropping support
- Maintain LTS branches for enterprise users

#### 2. **Automated Testing**
- Set up CI/CD to test multiple Python versions automatically
- Include backward compatibility tests in standard test suite
- Monitor dependency updates for breaking changes

#### 3. **Community Communication**
- Announce compatibility changes well in advance
- Provide migration tools where possible
- Maintain clear documentation of supported versions

**Key Takeaway**: Backward compatibility is not just about making old code work—it's about providing a smooth upgrade path that respects users' existing investments and timelines.

---

**Note**: This system is critical for ensuring ApiLogicServer quality. Always run full BLT tests before any release, and investigate any failures thoroughly.
