"""
Configuration and utilities for functional testing
"""
import os
import requests
from typing import Dict, Any

# Base configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class TestConfig:
    """Test configuration and common utilities"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {}
        self.auth_token = None
        
    def setup_auth(self, email: str = "doctor@doctor.com", password: str = "doctor123"):
        """Setup authentication for tests"""
        login_data = {"email": email, "password": password}
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.auth_token}"}
                print(f"✅ Authentication successful for {email}")
                return True
            else:
                print(f"⚠️ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error during auth: {e}")
            return False
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request"""
        kwargs.setdefault('timeout', TEST_TIMEOUT)
        kwargs.setdefault('headers', self.headers)
        
        url = f"{self.base_url}{endpoint}"
        return requests.request(method, url, **kwargs)
    
    def check_server_status(self) -> bool:
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code in [200, 404]  # 404 is fine, means server is up
        except:
            return False
    
    def get_test_credentials(self, user_type: str = "doctor") -> dict:
        """Get test credentials for different user types"""
        credentials = {
            "doctor": {"email": "doctor@doctor.com", "password": "doctor123"},
            "government": {"email": "a@gmail.com", "password": "111111"},
            "nurse": {"email": "jom@example.com", "password": "secret123"},
            "hospital_admin": {"email": "vijay@gmail.com", "password": "111111"}
        }
        return credentials.get(user_type, credentials["doctor"])
    
    def setup_auth_for_user_type(self, user_type: str = "doctor"):
        """Setup authentication for specific user type"""
        creds = self.get_test_credentials(user_type)
        return self.setup_auth(creds["email"], creds["password"])

# Global test configuration instance
test_config = TestConfig()