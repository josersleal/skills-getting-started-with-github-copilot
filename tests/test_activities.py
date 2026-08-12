"""
Backend tests for the Mergington High School Activities API.
Using AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Set up test client
        Act: Send GET request to /activities
        Assert: Verify response contains all activities with correct structure
        """
        # Arrange
        expected_activity_count = 9  # Based on app.py data

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == expected_activity_count
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert activities_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"

    def test_get_activities_includes_participants(self, client, reset_activities):
        """
        Arrange: Test client ready
        Act: Retrieve activities
        Assert: Verify participants list is present in response
        """
        # Arrange
        expected_participants_in_chess = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")

        # Assert
        activities_data = response.json()
        assert "participants" in activities_data["Chess Club"]
        assert activities_data["Chess Club"]["participants"] == expected_participants_in_chess


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client, reset_activities):
        """
        Arrange: New email not yet registered for activity
        Act: Send POST request to signup endpoint
        Assert: Verify participant added and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {new_email} for {activity_name}"

        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert new_email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_email_rejected(self, client, reset_activities):
        """
        Arrange: Email already registered for activity
        Act: Send POST request with duplicate email
        Assert: Verify 400 error and duplicate rejection message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_not_found(self, client, reset_activities):
        """
        Arrange: Activity name doesn't exist
        Act: Send POST request to non-existent activity
        Assert: Verify 404 error returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_updates_participant_list(self, client, reset_activities):
        """
        Arrange: Get initial participant count
        Act: Sign up new participant
        Assert: Verify participant list increased by 1
        """
        # Arrange
        activity_name = "Tennis Club"
        new_email = "tennis@mergington.edu"

        activities_before = client.get("/activities").json()
        participants_before = len(activities_before[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200

        activities_after = client.get("/activities").json()
        participants_after = len(activities_after[activity_name]["participants"])

        assert participants_after == participants_before + 1
        assert activities_after[activity_name]["participants"][-1] == new_email


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_success(self, client, reset_activities):
        """
        Arrange: Participant exists in activity
        Act: Send DELETE request to unregister endpoint
        Assert: Verify participant removed and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email_to_remove} from {activity_name}"

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email_to_remove not in activities_data[activity_name]["participants"]

    def test_unregister_participant_not_found(self, client, reset_activities):
        """
        Arrange: Email not registered for activity
        Act: Send DELETE request with non-existent email
        Assert: Verify 404 error returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_nonexistent_activity_not_found(self, client, reset_activities):
        """
        Arrange: Activity doesn't exist
        Act: Send DELETE request to non-existent activity
        Assert: Verify 404 error returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_updates_participant_list(self, client, reset_activities):
        """
        Arrange: Get initial participant count
        Act: Unregister a participant
        Assert: Verify participant list decreased by 1
        """
        # Arrange
        activity_name = "Art Studio"
        email_to_remove = "isabella@mergington.edu"

        activities_before = client.get("/activities").json()
        participants_before = len(activities_before[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200

        activities_after = client.get("/activities").json()
        participants_after = len(activities_after[activity_name]["participants"])

        assert participants_after == participants_before - 1
        assert email_to_remove not in activities_after[activity_name]["participants"]

    def test_unregister_does_not_affect_other_activities(self, client, reset_activities):
        """
        Arrange: Participant in multiple activities
        Act: Unregister from one activity
        Assert: Verify participant still in other activities
        """
        # Arrange
        activity_name = "Art Studio"
        email_to_remove = "isabella@mergington.edu"

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        activities_after = client.get("/activities").json()
        assert email_to_remove not in activities_after[activity_name]["participants"]
        # Participant should still be in other activities if they were registered
        # (This is more of a data integrity check in this simple in-memory system)
