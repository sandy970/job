#!/usr/bin/env python3
"""
Simple test runner for the Job Dashboard Backend API

This test runner doesn't require pytest and can be used to quickly verify
the basic functionality of the API endpoints.
"""

from fastapi.testclient import TestClient
from main import app
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create test client
client = TestClient(app)

def test_health_endpoint():
    """Test the root health check endpoint"""
    print("Testing health endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed: {data['message']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_config_endpoint():
    """Test the config endpoint"""
    print("\nTesting config endpoint...")
    response = client.get("/config")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Config endpoint working")
        print(f"Available job types: {list(data['job_types'].keys())}")
        print(f"Supported sources: {data['supported_sources']}")
        return True
    else:
        print(f"❌ Config endpoint failed: {response.status_code}")
        return False

def test_software_engineer_endpoint():
    """Test the software engineer jobs endpoint"""
    print("\nTesting software engineer endpoint...")
    response = client.get("/jobs/software-engineer?limit=3")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Software engineer endpoint working")
        print(f"Jobs returned: {len(data)}")
        if data:
            print(f"Sample job: {data[0]['job_title']} at {data[0]['company_name']}")
        return True
    else:
        print(f"❌ Software engineer endpoint failed: {response.status_code}")
        return False

def test_security_engineer_endpoint():
    """Test the security engineer jobs endpoint"""
    print("\nTesting security engineer endpoint...")
    response = client.get("/jobs/security-engineer?limit=3")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Security engineer endpoint working")
        print(f"Jobs returned: {len(data)}")
        if data:
            print(f"Sample job: {data[0]['job_title']} at {data[0]['company_name']}")
        return True
    else:
        print(f"❌ Security engineer endpoint failed: {response.status_code}")
        return False

def test_data_engineer_endpoint():
    """Test the data engineer jobs endpoint"""
    print("\nTesting data engineer endpoint...")
    response = client.get("/jobs/data-engineer?limit=3")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Data engineer endpoint working")
        print(f"Jobs returned: {len(data)}")
        if data:
            print(f"Sample job: {data[0]['job_title']} at {data[0]['company_name']}")
        return True
    else:
        print(f"❌ Data engineer endpoint failed: {response.status_code}")
        return False

def test_all_jobs_endpoint():
    """Test the all jobs endpoint"""
    print("\nTesting all jobs endpoint...")
    response = client.get("/jobs/all?limit_per_type=2")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ All jobs endpoint working")
        print(f"Total jobs: {data['total_count']}")
        return True
    else:
        print(f"❌ All jobs endpoint failed: {response.status_code}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\nTesting stats endpoint...")
    response = client.get("/stats")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stats endpoint working")
        print(f"Total jobs in database: {data['total_jobs']}")
        return True
    else:
        print(f"❌ Stats endpoint failed: {response.status_code}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\nTesting error handling...")
    
    # Test invalid job type
    response = client.get("/jobs/invalid-job-type")
    if response.status_code == 400:
        print("✅ Invalid job type error handling working")
    else:
        print(f"❌ Invalid job type error handling failed: {response.status_code}")
    
    # Test invalid source
    response = client.get("/jobs/software-engineer?source=invalid-source")
    if response.status_code == 400:
        print("✅ Invalid source error handling working")
    else:
        print(f"❌ Invalid source error handling failed: {response.status_code}")

def run_all_tests():
    """Run all tests and return summary"""
    print("=" * 60)
    print("🚀 Job Dashboard Backend API Tests")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_config_endpoint,
        test_software_engineer_endpoint,
        test_security_engineer_endpoint,
        test_data_engineer_endpoint,
        test_all_jobs_endpoint,
        test_stats_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Test error handling separately (doesn't return True/False)
    test_error_handling()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)