"""Unit tests for error codes and response utilities"""
import pytest
from src.utils.response import ErrorCode, BaseResponse, ERROR_MESSAGES


class TestErrorCode:
    """Tests for ErrorCode enum"""
    
    def test_error_code_values(self):
        """Test that error codes have correct values"""
        assert ErrorCode.SUCCESS == 200
        assert ErrorCode.TASK_CREATE_FAIL == 301
        assert ErrorCode.FILE_MISSING == 302
        assert ErrorCode.FILE_UPLOAD_FAIL == 303
        assert ErrorCode.UNAUTHORIZED == 401
        assert ErrorCode.TASK_STOP_FAIL == 402
        assert ErrorCode.TASK_DELETE_FAIL == 403
        assert ErrorCode.NOT_FOUND == 404
        assert ErrorCode.ALGORITHM_ERROR == 500
    
    def test_error_messages_exist(self):
        """Test that all error codes have messages"""
        for code in ErrorCode:
            assert code in ERROR_MESSAGES


class TestBaseResponse:
    """Tests for BaseResponse"""
    
    def test_success_response(self):
        """Test creating success response"""
        response = BaseResponse.success(task_id="TEST001", message="OK")
        assert response.code == 200
        assert response.taskID == "TEST001"
        assert response.message == "OK"
    
    def test_success_response_default_message(self):
        """Test success response with default message"""
        response = BaseResponse.success()
        assert response.code == 200
        assert response.message == "操作成功"
    
    def test_error_response(self):
        """Test creating error response"""
        response = BaseResponse.error(
            ErrorCode.TASK_CREATE_FAIL,
            message="Custom error",
            task_id="TEST001"
        )
        assert response.code == 301
        assert response.taskID == "TEST001"
        assert response.message == "Custom error"
    
    def test_error_response_default_message(self):
        """Test error response with default message"""
        response = BaseResponse.error(ErrorCode.UNAUTHORIZED)
        assert response.code == 401
        assert response.message == ERROR_MESSAGES[ErrorCode.UNAUTHORIZED]
    
    def test_extra_fields(self):
        """Test adding extra fields to response"""
        response = BaseResponse.success(status="running", progress=50)
        assert response.code == 200
        data = response.model_dump()
        assert data["status"] == "running"
        assert data["progress"] == 50
