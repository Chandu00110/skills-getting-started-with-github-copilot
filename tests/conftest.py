import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture: Returns TestClient for API testing."""
    return TestClient(app)


@pytest.fixture
def mock_activities():
    """Fixture: Returns fresh copy of activities for each test (Arrange step).
    
    This ensures test isolation - each test gets a clean state.
    """
    return deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(mock_activities, monkeypatch):
    """Fixture: Auto-resets global activities dict before each test.
    
    Uses monkeypatch to replace app.activities with clean copy.
    This runs automatically before every test.
    """
    monkeypatch.setattr("src.app.activities", mock_activities)
