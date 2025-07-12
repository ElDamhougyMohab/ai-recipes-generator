"""
Tests for health check endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_check_success(self, client: TestClient):
        """Test health endpoint returns 200 with correct response"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_health_check_response_format(self, client: TestClient):
        """Test health response has correct format"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "healthy"
        
        # Check response headers
        assert response.headers["content-type"] == "application/json"
    
    def test_health_check_multiple_requests(self, client: TestClient):
        """Test health endpoint handles multiple requests"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client):
        """Test health endpoint with async client"""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
