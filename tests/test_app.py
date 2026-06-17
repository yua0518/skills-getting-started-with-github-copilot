import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield


def test_get_activities_returns_activity_list():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert data[activity_name]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert isinstance(data[activity_name]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    before = client.get(f"/activities").json()[activity_name]["participants"]
    assert email not in before

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    updated = client.get(f"/activities").json()[activity_name]["participants"]
    assert email in updated
    assert len(updated) == len(before) + 1


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    before = client.get(f"/activities").json()[activity_name]["participants"]
    assert email in before

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    updated = client.get(f"/activities").json()[activity_name]["participants"]
    assert email not in updated
    assert len(updated) == len(before) - 1
