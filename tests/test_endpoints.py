import pytest
from faker import Faker

fake = Faker()


# ============================================================================
# GET / (Root Redirect)
# ============================================================================

def test_root_redirects_to_static_index(client):
    """Test: GET / redirects to /static/index.html with 307 status."""
    # Arrange - no setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ============================================================================
# GET /activities
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """Test: GET /activities returns all activities with correct structure."""
    # Arrange - no setup needed, activities already populated by fixture
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure - check a known activity exists
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_get_activities_returns_correct_participant_count(client):
    """Test: GET /activities shows correct participant count."""
    # Arrange
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    chess_club = data["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


# ============================================================================
# POST /activities/{activity_name}/signup
# ============================================================================

def test_signup_success_adds_participant(client):
    """Test (AAA): Successful signup adds email to participants list."""
    # Arrange
    activity_name = "Chess Club"
    email = fake.email()
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert - response
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Assert - verify participant was added
    activities_response = client.get("/activities")
    updated_activities = activities_response.json()
    assert email in updated_activities[activity_name]["participants"]


def test_signup_duplicate_returns_400_error(client):
    """Test (AAA): Duplicate signup attempts return 400 error."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_invalid_activity_returns_404_error(client):
    """Test (AAA): Signup for non-existent activity returns 404 error."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = fake.email()
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("email", [
    "student1@mergington.edu",
    "student2@mergington.edu",
    "student3@mergington.edu",
])
def test_signup_multiple_different_students(client, email):
    """Test (AAA): Multiple students can sign up (parametrized)."""
    # Arrange
    activity_name = "Programming Class"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    activities_response = client.get("/activities")
    updated = activities_response.json()
    assert email in updated[activity_name]["participants"]


# ============================================================================
# DELETE /activities/{activity_name}/remove
# ============================================================================

def test_remove_participant_success(client):
    """Test (AAA): Successfully remove existing participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Exists in initial data
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert - response
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    
    # Assert - verify participant was removed
    activities_response = client.get("/activities")
    updated_activities = activities_response.json()
    assert email not in updated_activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_400_error(client):
    """Test (AAA): Remove non-existent participant returns 400 error."""
    # Arrange
    activity_name = "Chess Club"
    email = fake.email()  # Not registered
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_remove_from_invalid_activity_returns_404_error(client):
    """Test (AAA): Remove from non-existent activity returns 404 error."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = fake.email()
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_then_signup_again_succeeds(client):
    """Test (AAA): After removal, same participant can sign up again."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act 1: Remove
    remove_response = client.delete(
        f"/activities/{activity_name}/remove",
        params={"email": email}
    )
    assert remove_response.status_code == 200
    
    # Act 2: Sign up again
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert signup_response.status_code == 200
    activities_response = client.get("/activities")
    updated = activities_response.json()
    assert email in updated[activity_name]["participants"]
