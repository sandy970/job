import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "timestamp" in data
    assert "version" in data
    assert data["message"] == "Job Dashboard API is running"

def test_config_endpoint():
    """Test the config endpoint"""
    response = client.get("/config")
    assert response.status_code == 200
    
    data = response.json()
    assert "job_types" in data
    assert "supported_sources" in data
    
    # Check that all expected job types are present
    expected_job_types = ["software-engineer", "security-engineer", "data-engineer"]
    for job_type in expected_job_types:
        assert job_type in data["job_types"]
    
    # Check supported sources
    assert "linkedin" in data["supported_sources"]
    assert "indeed" in data["supported_sources"]

def test_software_engineer_endpoint():
    """Test the software engineer jobs endpoint"""
    response = client.get("/jobs/software-engineer?limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # If jobs are returned, validate their structure
    if data:
        job = data[0]
        required_fields = ["job_title", "company_name", "location", "job_url", "source"]
        for field in required_fields:
            assert field in job

def test_security_engineer_endpoint():
    """Test the security engineer jobs endpoint"""
    response = client.get("/jobs/security-engineer?limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # If jobs are returned, validate their structure
    if data:
        job = data[0]
        required_fields = ["job_title", "company_name", "location", "job_url", "source"]
        for field in required_fields:
            assert field in job

def test_data_engineer_endpoint():
    """Test the data engineer jobs endpoint"""
    response = client.get("/jobs/data-engineer?limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # If jobs are returned, validate their structure
    if data:
        job = data[0]
        required_fields = ["job_title", "company_name", "location", "job_url", "source"]
        for field in required_fields:
            assert field in job

def test_invalid_job_type():
    """Test requesting an invalid job type"""
    response = client.get("/jobs/invalid-job-type")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "Invalid job type" in data["detail"]

def test_invalid_source():
    """Test requesting an invalid source"""
    response = client.get("/jobs/software-engineer?source=invalid-source")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "Invalid source" in data["detail"]

def test_all_jobs_endpoint():
    """Test the all jobs endpoint"""
    response = client.get("/jobs/all?limit_per_type=3")
    assert response.status_code == 200
    
    data = response.json()
    assert "jobs" in data
    assert "total_count" in data
    assert "timestamp" in data
    
    # Check that all job types are included
    jobs_data = data["jobs"]
    expected_job_types = ["software-engineer", "security-engineer", "data-engineer"]
    for job_type in expected_job_types:
        assert job_type in jobs_data
        assert isinstance(jobs_data[job_type], list)

def test_stats_endpoint():
    """Test the statistics endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    
    data = response.json()
    expected_fields = ["total_jobs", "jobs_by_type", "jobs_by_source", "recent_jobs_24h", "last_updated"]
    for field in expected_fields:
        assert field in data

def test_job_endpoint_with_different_sources():
    """Test job endpoints with different sources"""
    # Test LinkedIn
    response = client.get("/jobs/software-engineer?source=linkedin&limit=2")
    assert response.status_code == 200
    
    # Test Indeed
    response = client.get("/jobs/software-engineer?source=indeed&limit=2")
    assert response.status_code == 200

def test_job_endpoint_with_limits():
    """Test job endpoints with different limits"""
    # Test with small limit
    response = client.get("/jobs/software-engineer?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 1
    
    # Test with larger limit
    response = client.get("/jobs/software-engineer?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10

def test_concurrent_requests():
    """Test that the API can handle concurrent requests"""
    import concurrent.futures
    import threading
    
    def make_request():
        response = client.get("/jobs/software-engineer?limit=2")
        return response.status_code
    
    # Make 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    assert all(status == 200 for status in results)

def run_manual_tests():
    """
    Run manual tests to verify the scraper functionality
    
    This function can be run independently to test the actual scraping
    without relying on pytest
    """
    print("Running manual API tests...")
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test config endpoint
    print("\n2. Testing config endpoint...")
    response = client.get("/config")
    print(f"Status: {response.status_code}")
    print(f"Job types: {list(response.json()['job_types'].keys())}")
    
    # Test software engineer jobs
    print("\n3. Testing software engineer jobs...")
    response = client.get("/jobs/software-engineer?limit=3")
    print(f"Status: {response.status_code}")
    jobs = response.json()
    print(f"Number of jobs returned: {len(jobs)}")
    if jobs:
        print(f"Sample job: {jobs[0]}")
    
    # Test stats endpoint
    print("\n4. Testing stats endpoint...")
    response = client.get("/stats")
    print(f"Status: {response.status_code}")
    stats = response.json()
    print(f"Stats: {stats}")
    
    # Test all jobs endpoint
    print("\n5. Testing all jobs endpoint...")
    response = client.get("/jobs/all?limit_per_type=2")
    print(f"Status: {response.status_code}")
    all_jobs = response.json()
    print(f"Total jobs count: {all_jobs.get('total_count', 0)}")
    
    print("\nManual tests completed!")

if __name__ == "__main__":
    # Run manual tests if this file is executed directly
    run_manual_tests()