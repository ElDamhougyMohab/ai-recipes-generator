# 🧪 Test Automation Suite

Comprehensive test automation scripts for the AI Recipe Generator application.

## 🚀 Quick Start

### Option 1: Simple Batch File (Windows)
```bash
# Double-click or run from command prompt
run_tests.bat
```

### Option 2: PowerShell Script (Windows)
```powershell
# Basic run
.\run_tests.ps1

# Quick test with coverage and HTML dashboard
.\run_tests.ps1 -Quick -Coverage -HTML

# Parallel execution with verbose output
.\run_tests.ps1 -Parallel -Verbose
```

### Option 3: Python Script (Cross-platform)
```bash
# Basic comprehensive test run
python run_comprehensive_tests.py

# Quick test with coverage and PDF report
python run_comprehensive_tests.py --quick --coverage --pdf

# Full test suite with all reports
python run_comprehensive_tests.py --coverage --html --pdf --verbose
```

## 📊 What Gets Tested

### Core Functionality
- ✅ **Health Checks** - API endpoint availability
- ✅ **Recipe Generation** - AI service integration
- ✅ **CRUD Operations** - Create, read, update, delete recipes
- ✅ **Search & Filtering** - Recipe search functionality
- ✅ **Dietary Restrictions** - Vegetarian, vegan, gluten-free filtering

### Data Validation
- ✅ **Input Validation** - Ingredient lists, dietary preferences
- ✅ **Output Validation** - Recipe format, required fields
- ✅ **Error Handling** - Invalid inputs, API failures
- ✅ **Edge Cases** - Empty inputs, special characters

### Integration Testing
- ✅ **Frontend-Backend** - API endpoint integration
- ✅ **Database Operations** - SQLite CRUD operations
- ✅ **AI Service** - Gemini API integration
- ✅ **External APIs** - Third-party service calls

### Performance Testing
- ✅ **Response Times** - API endpoint latency
- ✅ **Concurrent Users** - Multiple simultaneous requests
- ✅ **Memory Usage** - Resource consumption monitoring
- ✅ **Stress Testing** - High-load scenarios

## 📋 Generated Reports

### Automatic Reports
- 📊 **HTML Test Report** - Interactive test results
- 📈 **Coverage Report** - Code coverage analysis
- 📄 **PDF Summary** - Executive summary report
- 📊 **Interactive Dashboard** - Visual test metrics
- 📝 **Detailed Logs** - Complete execution logs

### Report Locations
```
test_reports/
├── test_summary_YYYYMMDD_HHMMSS.json      # JSON test results
├── basic_test_report_YYYYMMDD_HHMMSS.html # HTML test report
├── dashboard_YYYYMMDD_HHMMSS.html         # Interactive dashboard
├── test_report_YYYYMMDD_HHMMSS.pdf        # PDF summary
├── test_run_YYYYMMDD_HHMMSS.log          # Execution log
└── coverage/
    └── index.html                          # Coverage report
```

## 🎯 Test Scenarios

### Scenario 1: Full Health Check
```bash
python run_comprehensive_tests.py --quick
```
- Runs core functionality tests (3-5 minutes)
- Validates API endpoints
- Checks basic AI integration
- **Best for**: Quick validation

### Scenario 2: Coverage Analysis
```bash
python run_comprehensive_tests.py --coverage --html
```
- Full test suite with coverage metrics
- Interactive HTML dashboard
- Line-by-line coverage analysis
- **Best for**: Code quality assessment

### Scenario 3: Pre-deployment Validation
```bash
python run_comprehensive_tests.py --coverage --pdf --parallel
```
- Complete test suite
- Executive PDF report
- Parallel execution for speed
- **Best for**: Production readiness

### Scenario 4: Performance Benchmarking
```bash
python run_comprehensive_tests.py --verbose
```
- Includes performance and stress tests
- Detailed execution logging
- Memory and response time analysis
- **Best for**: Performance optimization

## 🔧 Command Line Options

### Python Script Options
| Option | Description | Example |
|--------|-------------|---------|
| `--quick` | Run only fast tests | `--quick` |
| `--coverage` | Generate coverage reports | `--coverage` |
| `--pdf` | Generate PDF report | `--pdf` |
| `--html` | Generate HTML dashboard | `--html` |
| `--parallel` | Run tests in parallel | `--parallel` |
| `--failures-only` | Show only failed tests | `--failures-only` |
| `--verbose` | Detailed output | `--verbose` |
| `--docker` | Test Docker deployment | `--docker` |
| `--staging` | Test staging environment | `--staging` |

### PowerShell Script Options
| Option | Description | Example |
|--------|-------------|---------|
| `-Quick` | Run only fast tests | `-Quick` |
| `-Coverage` | Generate coverage reports | `-Coverage` |
| `-PDF` | Generate PDF report | `-PDF` |
| `-HTML` | Generate HTML dashboard | `-HTML` |
| `-Parallel` | Run tests in parallel | `-Parallel` |
| `-Verbose` | Detailed output | `-Verbose` |
| `-Help` | Show help message | `-Help` |

## 📈 Understanding Results

### Success Metrics
- **90%+ Pass Rate**: Excellent, ready for deployment
- **80-89% Pass Rate**: Good, minor issues to address
- **70-79% Pass Rate**: Needs attention, review failures
- **<70% Pass Rate**: Critical issues, major fixes needed

### Coverage Targets
- **80%+ Coverage**: Excellent test coverage
- **60-79% Coverage**: Good coverage, some gaps
- **40-59% Coverage**: Moderate coverage, needs improvement
- **<40% Coverage**: Poor coverage, significant gaps

### Performance Benchmarks
- **API Response Time**: < 200ms for simple requests
- **Recipe Generation**: < 5 seconds with AI
- **Database Queries**: < 50ms for basic operations
- **Concurrent Users**: 10+ simultaneous users

## 🚨 Common Issues & Solutions

### Issue: Tests Fail with Connection Errors
**Cause**: Backend service not running
**Solution**: 
```bash
# Start the backend service first
cd backend
python -m app.main
```

### Issue: AI Service Tests Fail
**Cause**: Gemini API key not configured
**Solution**: 
```bash
# Set the API key environment variable
set GEMINI_API_KEY=your_api_key_here
```

### Issue: Database Tests Fail
**Cause**: Database file permissions or corruption
**Solution**:
```bash
# Reset the test database
cd backend
rm -f test_recipes.db
python -c "from app.database import init_db; init_db()"
```

### Issue: Performance Tests Fail
**Cause**: System under load or insufficient resources
**Solution**: 
- Close other applications
- Run with `--quick` option
- Use `--parallel` for faster execution

## 🔄 Continuous Integration

### GitHub Actions Integration
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: python run_comprehensive_tests.py --coverage --html
```

### Local Pre-commit Hook
```bash
#!/bin/sh
# Add to .git/hooks/pre-commit
python run_comprehensive_tests.py --quick
```

## 📞 Support

### If Tests Keep Failing
1. **Check the failure analysis**: Review `DETAILED_TEST_FAILURE_ANALYSIS.md`
2. **Verify deployment**: Ensure FastAPI backend is deployed, not nginx mock
3. **Check logs**: Review `test_run_*.log` files
4. **Run specific tests**: `python -m pytest tests/test_specific.py -v`

### Environment Issues
1. **Python version**: Ensure Python 3.8+
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Virtual environment**: Use `python -m venv venv` and activate
4. **Permissions**: Ensure write access to test_reports directory

---

🎯 **Goal**: Achieve 90%+ test pass rate with comprehensive coverage for production-ready deployment.
