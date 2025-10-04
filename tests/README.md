# Functional Testing Guide for Core-Backend

This guide explains how to use the functional tests I've created for your Core-Backend FastAPI application.

## 📁 Test Files Created

```
tests/
├── __init__.py                     # Package initialization
├── test_config.py                  # Test configuration and utilities
├── test_auth_functions.py          # Authentication endpoint tests
├── test_analytics_functions.py     # Analytics endpoint tests
├── test_prediction_functions.py    # Prediction service tests
├── run_functional_tests.py         # Complete test suite runner
├── simple_test_runner.py           # Simple test runner (no pytest)
└── README.md                       # This guide
```

## 🚀 How to Run the Tests

### Method 1: Simple Test Runner (Recommended for beginners)

1. **Start your server first:**

   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Run all tests:**

   ```powershell
   cd "c:\Users\User\Desktop\Data Science Project\XXX\Core-Backend"
   python tests\simple_test_runner.py
   ```

3. **Run specific test categories:**

   ```powershell
   # Authentication tests only
   python tests\simple_test_runner.py auth

   # Analytics tests only
   python tests\simple_test_runner.py analytics

   # Prediction tests only
   python tests\simple_test_runner.py predictions
   ```

### Method 2: Complete Test Suite

1. **Install testing dependencies:**

   ```powershell
   pip install requests pytest
   ```

2. **Start your server:**

   ```powershell
   uvicorn app.main:app --reload
   ```

3. **Run complete test suite:**
   ```powershell
   python tests\run_functional_tests.py
   ```

### Method 3: Individual Test Files

You can also run individual test files directly:

```powershell
# Run authentication tests
python tests\test_auth_functions.py

# Run analytics tests
python tests\test_analytics_functions.py

# Run prediction tests
python tests\test_prediction_functions.py
```

## 🧪 What the Tests Do

### Authentication Tests (`test_auth_functions.py`)

- ✅ Checks if server is running and accessible
- ✅ Tests route discovery endpoint
- ✅ Tests login endpoint functionality
- ✅ Tests nurse registration endpoint
- ✅ Tests doctor registration endpoint
- ✅ Tests invalid login handling

### Analytics Tests (`test_analytics_functions.py`)

- ✅ Tests analytics endpoint accessibility
- ✅ Tests analytics with various filters
- ✅ Tests analytics summary endpoint
- ✅ Tests filter options endpoint

### Prediction Tests (`test_prediction_functions.py`)

- ✅ Tests hospital stay prediction service
- ✅ Tests transfer probability prediction
- ✅ Tests SARIMA forecast prediction
- ✅ Checks prediction endpoint accessibility

## 📊 Understanding Test Results

### Test Output Symbols:

- ✅ **PASSED** - Test completed successfully
- ❌ **FAILED** - Test encountered an error
- ⚠️ **WARNING** - Test completed but with issues
- ℹ️ **INFO** - Additional information

### Success Rates:

- **85%+** - Excellent, ready for production
- **70-84%** - Good, minor issues to address
- **50-69%** - Needs work, review failed tests
- **<50%** - Critical issues, requires attention

## 🛠️ Troubleshooting

### Common Issues and Solutions:

#### 1. "Server is not running" Error

**Problem:** Tests can't connect to your server
**Solution:**

```powershell
# Start your server in a separate terminal
uvicorn app.main:app --reload
```

#### 2. "Import Error" or Module Not Found

**Problem:** Missing dependencies
**Solution:**

```powershell
pip install -r requirements.txt
```

#### 3. Authentication Errors

**Problem:** Tests failing due to authentication
**Solution:**

- Check your database is connected
- Verify user registration endpoints work
- Check Supabase configuration

#### 4. Prediction Tests Failing

**Problem:** Model files not found
**Solution:**

- Ensure model files exist in `trained_models/`
- Check file paths in prediction services
- Verify model loading code

## 🎯 Test Configuration

You can modify test settings in `tests/test_config.py`:

```python
# Change base URL if running on different port
BASE_URL = "http://localhost:8000"

# Adjust timeout for slow endpoints
TEST_TIMEOUT = 30

# Modify test credentials
def setup_auth(self, email: str = "doctor@example.com", password: str = "password123"):
```

## 📈 Adding New Tests

To add new functional tests:

1. **Create a new test file** (e.g., `test_hospital_functions.py`):

```python
from tests.test_config import test_config

class TestHospitalFunctions:
    def test_your_new_function(self):
        response = test_config.make_request('GET', '/hospital/list')
        assert response.status_code == 200
        print("✅ Hospital list test passed")
```

2. **Add to the test runner** in `simple_test_runner.py`

## 🔍 What to Look For

### Successful Test Run Should Show:

- Server accessibility confirmed
- All endpoints responding (even if with auth errors)
- Proper error handling for invalid data
- Expected response formats

### Red Flags to Investigate:

- Connection timeouts
- 500 Internal Server Errors
- Missing endpoints (404 errors)
- Unexpected response formats

## 📝 Next Steps After Testing

1. **Review Failed Tests** - Fix any critical issues
2. **Check Server Logs** - Look for detailed error messages
3. **Verify Database** - Ensure all tables and data exist
4. **Test Real Scenarios** - Try actual user workflows
5. **Performance Testing** - Test with larger datasets
6. **Security Testing** - Verify authentication and authorization

## 🆘 Need Help?

If tests are failing:

1. **Check the terminal output** for specific error messages
2. **Look at your FastAPI server logs** for backend errors
3. **Verify your `.env` file** has correct database settings
4. **Ensure all required model files** are in place
5. **Test endpoints manually** using your browser or Postman

Remember: These tests validate that your API endpoints work as expected. They're designed to catch issues early and ensure your system is ready for real users!
