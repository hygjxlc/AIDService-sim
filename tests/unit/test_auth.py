"""Unit tests for authentication module"""
import pytest
from src.services.auth import ApiKeyAuthProvider


class TestApiKeyAuthProvider:
    """Tests for ApiKeyAuthProvider"""
    
    def test_validate_correct_key(self):
        """Test validation with correct API key"""
        provider = ApiKeyAuthProvider("11111111")
        assert provider.validate("11111111") is True
    
    def test_validate_incorrect_key(self):
        """Test validation with incorrect API key"""
        provider = ApiKeyAuthProvider("11111111")
        assert provider.validate("wrong_key") is False
    
    def test_validate_empty_key(self):
        """Test validation with empty API key"""
        provider = ApiKeyAuthProvider("11111111")
        assert provider.validate("") is False
    
    def test_validate_none_key(self):
        """Test validation with None API key"""
        provider = ApiKeyAuthProvider("11111111")
        assert provider.validate(None) is False
