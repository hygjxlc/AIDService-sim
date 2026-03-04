"""Integration tests for task lifecycle"""
import pytest
from fastapi.testclient import TestClient


class TestTaskLifecycle:
    """Integration tests for complete task lifecycle"""
    
    @pytest.fixture
    def api_key(self):
        return "11111111"
    
    def test_create_task_success(self, client, api_key):
        """Test successful task creation"""
        response = client.post("/api/v1/newTaskCreate", json={
            "simulateType": "LaWan",
            "taskName": "test_task_001",
            "api_key": api_key
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["taskID"] is not None
        assert data["taskID"].startswith("LaWan")
    
    def test_create_task_invalid_type(self, client, api_key):
        """Test task creation with invalid simulate type"""
        response = client.post("/api/v1/newTaskCreate", json={
            "simulateType": "InvalidType",
            "taskName": "test_task",
            "api_key": api_key
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 301
    
    def test_create_task_invalid_name(self, client, api_key):
        """Test task creation with invalid task name"""
        response = client.post("/api/v1/newTaskCreate", json={
            "simulateType": "LaWan",
            "taskName": "invalid name with spaces!",
            "api_key": api_key
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 301
    
    def test_create_task_unauthorized(self, client):
        """Test task creation without valid API key"""
        response = client.post("/api/v1/newTaskCreate", json={
            "simulateType": "LaWan",
            "taskName": "test_task",
            "api_key": "wrong_key"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 401
    
    def test_verify_task_not_found(self, client, api_key):
        """Test verify task that doesn't exist"""
        response = client.post("/api/v1/newTaskverify", json={
            "TaskID": "NonExistent123",
            "api_key": api_key
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404
    
    def test_query_status_not_exist(self, client, api_key):
        """Test query status for non-existent task"""
        response = client.post("/api/v1/queryTaskStatus", json={
            "TaskID": "NonExistent123",
            "api_key": api_key
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_exist"
    
    def test_health_check_no_auth(self, client):
        """Test health check doesn't require auth"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["OK", "DEGRADED"]
        assert "version" in data
