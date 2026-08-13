"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to their initial state before each test.
    This ensures test isolation by removing any participant changes.
    """
    # Store original state
    original_activities = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for name, details in activities.items()
    }

    yield  # Test runs here

    # Restore original state
    for name, original_details in original_activities.items():
        activities[name] = original_details
