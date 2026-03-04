"""Pytest Configuration"""
import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create temporary database path for testing"""
    return str(tmp_path_factory.mktemp("data") / "test.db")


@pytest.fixture(scope="function")
def db_session(test_db_path):
    """Create database session for testing"""
    from src.database.db import init_db, get_session
    
    # Initialize test database
    init_db(test_db_path)
    
    session = get_session()
    yield session
    session.close()


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from src.main import app
    
    with TestClient(app) as c:
        yield c
