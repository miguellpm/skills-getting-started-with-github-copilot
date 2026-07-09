import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def restore_activity_state():
    # Arrange
    original_participants = {
        activity_name: activity_data["participants"].copy()
        for activity_name, activity_data in activities.items()
    }

    yield

    # Teardown
    for activity_name, activity_data in activities.items():
        activity_data["participants"] = original_participants[activity_name].copy()


def test_get_activities_returns_seeded_data(client):
    # Arrange
    # No setup required for this endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_for_activity_rejects_duplicate_participant(client):
    # Arrange
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"


def test_unregister_participant_returns_not_found_for_missing_participant(client):
    # Arrange
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
