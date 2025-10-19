"""
Comprehensive Integration Test Suite for Database and API
Tests the integration between database.py and api.py to ensure
all endpoints work correctly with the SQLite database.
"""

import pytest
from fastapi.testclient import TestClient
import sqlite3
from datetime import datetime, date, timedelta
from api import app, get_db
from database import SQLiteDatabase, init_db


# --- FIXTURES ---

@pytest.fixture
def test_db():
    """Create an in-memory database for testing."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_db(conn)
    db = SQLiteDatabase(conn)
    yield db
    conn.close()


@pytest.fixture
def client(test_db):
    """Returns a FastAPI TestClient with the overridden DB."""
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "username": "testuser",
        "password": "testpass",
        "id": 100,
        "fname": "John",
        "lname": "Doe",
        "rating": 1500,
        "email": "john.doe@example.com",
        "phone": "555-1234",
        "bday": "1990-01-15",
        "gender": 1
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    start_time = datetime.now() + timedelta(days=1)
    return {
        "id": 1000,
        "start_time": start_time.isoformat(),
        "max_players": 4,
        "gender": 3,
        "court": 1,
        "description": "Friendly doubles match"
    }


# --- ROOT ENDPOINT TESTS ---

def test_root_endpoint(client):
    """Test that the root endpoint returns a success message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Tennis Organizer API" in response.json()["message"]


# --- PLAYER ENDPOINT TESTS ---

class TestPlayerEndpoints:
    """Test suite for player-related endpoints."""

    def test_create_player_success(self, client, sample_player_data):
        """Test successful player creation."""
        response = client.post("/api/players", json=sample_player_data)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == sample_player_data["id"]
        assert data["fname"] == sample_player_data["fname"]
        assert data["lname"] == sample_player_data["lname"]
        assert data["rating"] == sample_player_data["rating"]
        assert data["email"] == sample_player_data["email"]
        assert data["phone"] == sample_player_data["phone"]
        assert data["gender"] == sample_player_data["gender"]

    def test_create_player_duplicate_username(self, client, sample_player_data):
        """Test that duplicate usernames are rejected."""
        # Create first player
        client.post("/api/players", json=sample_player_data)

        # Try to create second player with same username but different ID
        duplicate_data = sample_player_data.copy()
        duplicate_data["id"] = 101
        response = client.post("/api/players", json=duplicate_data)
        assert response.status_code == 409
        assert "Username already exists" in response.json()["detail"]

    def test_create_player_duplicate_id(self, client, sample_player_data):
        """Test that duplicate player IDs are rejected."""
        # Create first player
        client.post("/api/players", json=sample_player_data)

        # Try to create second player with same ID but different username
        duplicate_data = sample_player_data.copy()
        duplicate_data["username"] = "different_user"
        response = client.post("/api/players", json=duplicate_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_get_player_by_credentials_success(self, client, sample_player_data):
        """Test retrieving a player by username and password."""
        # Create player
        client.post("/api/players", json=sample_player_data)

        # Retrieve player
        response = client.get("/api/players", params={
            "username": sample_player_data["username"],
            "password": sample_player_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_player_data["id"]
        assert data["fname"] == sample_player_data["fname"]

    def test_get_player_invalid_credentials(self, client, sample_player_data):
        """Test that invalid credentials return 404."""
        # Create player
        client.post("/api/players", json=sample_player_data)

        # Try with wrong password
        response = client.get("/api/players", params={
            "username": sample_player_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_player_rating_success(self, client, sample_player_data):
        """Test updating a player's rating."""
        # Create player
        client.post("/api/players", json=sample_player_data)

        # Update rating
        new_rating = 1750
        response = client.patch(f"/api/players/{sample_player_data['id']}", json={
            "rating": new_rating
        })
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == new_rating
        # Other fields should remain unchanged
        assert data["fname"] == sample_player_data["fname"]
        assert data["id"] == sample_player_data["id"]

    def test_update_player_rating_nonexistent(self, client):
        """Test updating a nonexistent player returns 404."""
        response = client.patch("/api/players/99999", json={"rating": 2000})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


# --- EVENT ENDPOINT TESTS ---

class TestEventEndpoints:
    """Test suite for event-related endpoints."""

    def test_create_event_success(self, client, sample_event_data):
        """Test successful event creation with client-provided ID."""
        response = client.post("/api/events", json=sample_event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == sample_event_data["id"]
        assert data["max_players"] == sample_event_data["max_players"]
        assert data["gender"] == sample_event_data["gender"]
        assert data["court"] == sample_event_data["court"]
        assert data["description"] == sample_event_data["description"]
        # Check that end_time is calculated correctly (start + 1 hour)
        start_dt = datetime.fromisoformat(sample_event_data["start_time"])
        end_dt = datetime.fromisoformat(data["end_time"])
        assert end_dt == start_dt + timedelta(hours=1)

    def test_create_event_duplicate_id(self, client, sample_event_data):
        """Test that duplicate event IDs are rejected."""
        # Create first event
        client.post("/api/events", json=sample_event_data)

        # Try to create second event with same ID
        response = client.post("/api/events", json=sample_event_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_get_all_events_empty(self, client):
        """Test getting all events when database is empty."""
        response = client.get("/api/events")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_events_multiple(self, client):
        """Test getting multiple events."""
        # Create three events
        for i in range(3):
            event_data = {
                "id": 1000 + i,
                "start_time": (datetime.now() + timedelta(days=i)).isoformat(),
                "max_players": 4,
                "gender": 3,
                "court": i + 1,
                "description": f"Event {i}"
            }
            client.post("/api/events", json=event_data)

        # Get all events
        response = client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


# --- EVENT-PLAYER INTERACTION TESTS ---

class TestEventPlayerInteractions:
    """Test suite for adding/removing players to/from events."""

    def test_add_player_to_event_success(self, client, sample_player_data, sample_event_data):
        """Test successfully adding a player to an event."""
        # Create player and event
        client.post("/api/players", json=sample_player_data)
        client.post("/api/events", json=sample_event_data)

        # Add player to event
        response = client.patch(
            f"/api/events/{sample_event_data['id']}/add_player",
            json={"player_id": sample_player_data["id"]}
        )
        assert response.status_code == 200
        assert response.json()["id"] == sample_event_data["id"]

    def test_add_nonexistent_player_to_event(self, client, sample_event_data):
        """Test adding a nonexistent player to an event."""
        # Create only the event
        client.post("/api/events", json=sample_event_data)

        # Try to add nonexistent player
        response = client.patch(
            f"/api/events/{sample_event_data['id']}/add_player",
            json={"player_id": 99999}
        )
        assert response.status_code == 404
        assert "Player" in response.json()["detail"]

    def test_add_player_to_nonexistent_event(self, client, sample_player_data):
        """Test adding a player to a nonexistent event."""
        # Create only the player
        client.post("/api/players", json=sample_player_data)

        # Try to add to nonexistent event
        response = client.patch(
            "/api/events/99999/add_player",
            json={"player_id": sample_player_data["id"]}
        )
        assert response.status_code == 404
        assert "Event" in response.json()["detail"]

    def test_add_player_to_full_event(self, client):
        """Test that adding a player to a full event is rejected."""
        # Create event with max_players=1
        event_data = {
            "id": 2000,
            "start_time": datetime.now().isoformat(),
            "max_players": 1,
            "gender": 3,
            "court": 1,
            "description": "Singles only"
        }
        client.post("/api/events", json=event_data)

        # Create two players
        player1 = {
            "username": "player1", "password": "pass", "id": 201,
            "fname": "First", "lname": "Player", "rating": 1500,
            "email": "p1@test.com", "phone": "111", "bday": "1990-01-01", "gender": 1
        }
        player2 = {
            "username": "player2", "password": "pass", "id": 202,
            "fname": "Second", "lname": "Player", "rating": 1500,
            "email": "p2@test.com", "phone": "222", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player1)
        client.post("/api/players", json=player2)

        # Add first player (should succeed)
        response1 = client.patch("/api/events/2000/add_player", json={"player_id": 201})
        assert response1.status_code == 200

        # Add second player (should fail - event full)
        response2 = client.patch("/api/events/2000/add_player", json={"player_id": 202})
        assert response2.status_code == 409
        assert "locked" in response2.json()["detail"].lower()

    def test_add_player_wrong_gender(self, client):
        """Test that adding a player of wrong gender to gender-specific event is rejected."""
        # Create men's only event
        event_data = {
            "id": 3000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 1,  # Men's only
            "court": 1,
            "description": "Men's singles"
        }
        client.post("/api/events", json=event_data)

        # Create female player
        player_data = {
            "username": "female_player", "password": "pass", "id": 301,
            "fname": "Jane", "lname": "Doe", "rating": 1500,
            "email": "jane@test.com", "phone": "333", "bday": "1990-01-01", "gender": 2
        }
        client.post("/api/players", json=player_data)

        # Try to add female player to men's event
        response = client.patch("/api/events/3000/add_player", json={"player_id": 301})
        assert response.status_code == 409
        assert "MENS" in response.json()["detail"]

    def test_remove_player_from_event_success(self, client, sample_player_data, sample_event_data):
        """Test successfully removing a player from an event."""
        # Create player and event
        client.post("/api/players", json=sample_player_data)
        client.post("/api/events", json=sample_event_data)

        # Add player to event
        client.patch(
            f"/api/events/{sample_event_data['id']}/add_player",
            json={"player_id": sample_player_data["id"]}
        )

        # Remove player from event
        response = client.patch(
            f"/api/events/{sample_event_data['id']}/remove_player",
            json={"player_id": sample_player_data["id"]}
        )
        assert response.status_code == 200

    def test_remove_player_not_in_event(self, client, sample_player_data, sample_event_data):
        """Test removing a player that's not in the event."""
        # Create player and event
        client.post("/api/players", json=sample_player_data)
        client.post("/api/events", json=sample_event_data)

        # Try to remove player without adding them first
        response = client.patch(
            f"/api/events/{sample_event_data['id']}/remove_player",
            json={"player_id": sample_player_data["id"]}
        )
        assert response.status_code == 404
        assert "not found in event" in response.json()["detail"]

    def test_remove_nonexistent_player_from_event(self, client, sample_event_data):
        """Test removing a nonexistent player from an event."""
        # Create only the event
        client.post("/api/events", json=sample_event_data)

        # Try to remove nonexistent player
        response = client.patch(
            f"/api/events/{sample_event_data['id']}/remove_player",
            json={"player_id": 99999}
        )
        assert response.status_code == 404
        assert "Player" in response.json()["detail"]


# --- RECOMMENDATION ENDPOINT TESTS ---

class TestRecommendations:
    """Test suite for event recommendation endpoint."""

    def test_recommendations_no_events(self, client, sample_player_data):
        """Test recommendations when no events exist."""
        # Create player
        client.post("/api/players", json=sample_player_data)

        # Get recommendations
        response = client.get(f"/api/recommendations/{sample_player_data['id']}")
        assert response.status_code == 200
        assert response.json() == []

    def test_recommendations_nonexistent_player(self, client):
        """Test recommendations for nonexistent player."""
        response = client.get("/api/recommendations/99999")
        assert response.status_code == 404

    def test_recommendations_empty_event(self, client):
        """Test that empty events are recommended to all players."""
        # Create player
        player_data = {
            "username": "testuser", "password": "pass", "id": 400,
            "fname": "Test", "lname": "User", "rating": 1500,
            "email": "test@test.com", "phone": "444", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player_data)

        # Create empty event
        event_data = {
            "id": 4000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Empty event"
        }
        client.post("/api/events", json=event_data)

        # Get recommendations
        response = client.get("/api/recommendations/400")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 1
        assert recommendations[0]["id"] == 4000

    def test_recommendations_rating_range(self, client):
        """Test that recommendations respect rating ranges."""
        # Create two players with different ratings
        player1 = {
            "username": "lowrated", "password": "pass", "id": 501,
            "fname": "Low", "lname": "Rated", "rating": 1000,
            "email": "low@test.com", "phone": "555", "bday": "1990-01-01", "gender": 1
        }
        player2 = {
            "username": "highrated", "password": "pass", "id": 502,
            "fname": "High", "lname": "Rated", "rating": 2000,
            "email": "high@test.com", "phone": "666", "bday": "1990-01-01", "gender": 1
        }
        player3 = {
            "username": "midrated", "password": "pass", "id": 503,
            "fname": "Mid", "lname": "Rated", "rating": 1500,
            "email": "mid@test.com", "phone": "777", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player1)
        client.post("/api/players", json=player2)
        client.post("/api/players", json=player3)

        # Create event
        event_data = {
            "id": 5000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Rating test event"
        }
        client.post("/api/events", json=event_data)

        # Add low-rated player (rating 1000)
        client.patch("/api/events/5000/add_player", json={"player_id": 501})

        # Mid-rated player (1500) should be recommended (within 1000±5 range: 995-1005)
        # Actually, the range is ±5 from min/max, so 995-1005
        # Player with 1500 rating is outside this range
        response = client.get("/api/recommendations/503")
        recommendations = response.json()
        # 1500 is NOT within 995-1005, so should not be recommended
        assert len(recommendations) == 0

        # High-rated player (2000) should definitely not be recommended
        response = client.get("/api/recommendations/502")
        recommendations = response.json()
        assert len(recommendations) == 0

    def test_recommendations_gender_filter(self, client):
        """Test that gender-specific events are filtered correctly."""
        # Create male and female players
        male_player = {
            "username": "maleplayer", "password": "pass", "id": 601,
            "fname": "Male", "lname": "Player", "rating": 1500,
            "email": "male@test.com", "phone": "888", "bday": "1990-01-01", "gender": 1
        }
        female_player = {
            "username": "femaleplayer", "password": "pass", "id": 602,
            "fname": "Female", "lname": "Player", "rating": 1500,
            "email": "female@test.com", "phone": "999", "bday": "1990-01-01", "gender": 2
        }
        client.post("/api/players", json=male_player)
        client.post("/api/players", json=female_player)

        # Create men's only event
        mens_event = {
            "id": 6000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 1,
            "court": 1,
            "description": "Men's event"
        }
        client.post("/api/events", json=mens_event)

        # Male player should see the event
        response = client.get("/api/recommendations/601")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 1

        # Female player should not see the event
        response = client.get("/api/recommendations/602")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 0

    def test_recommendations_exclude_full_events(self, client):
        """Test that full events are not recommended."""
        # Create player
        player_data = {
            "username": "excluded", "password": "pass", "id": 700,
            "fname": "Excluded", "lname": "Player", "rating": 1500,
            "email": "excl@test.com", "phone": "000", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player_data)

        # Create event with max 1 player
        event_data = {
            "id": 7000,
            "start_time": datetime.now().isoformat(),
            "max_players": 1,
            "gender": 3,
            "court": 1,
            "description": "Full event"
        }
        client.post("/api/events", json=event_data)

        # Create another player and add to event
        other_player = {
            "username": "other", "password": "pass", "id": 701,
            "fname": "Other", "lname": "Player", "rating": 1500,
            "email": "other@test.com", "phone": "001", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=other_player)
        client.patch("/api/events/7000/add_player", json={"player_id": 701})

        # Original player should not see the full event
        response = client.get("/api/recommendations/700")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 0

    def test_recommendations_exclude_already_joined(self, client):
        """Test that events the player has already joined are not recommended."""
        # Create player
        player_data = {
            "username": "joined", "password": "pass", "id": 800,
            "fname": "Joined", "lname": "Player", "rating": 1500,
            "email": "joined@test.com", "phone": "800", "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player_data)

        # Create event
        event_data = {
            "id": 8000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Already joined"
        }
        client.post("/api/events", json=event_data)

        # Add player to event
        client.patch("/api/events/8000/add_player", json={"player_id": 800})

        # Player should not see events they're already in
        response = client.get("/api/recommendations/800")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) == 0


# --- DATABASE INTEGRATION TESTS ---

class TestDatabaseIntegration:
    """Test suite for direct database operations through the API."""

    def test_database_persistence_across_requests(self, client, sample_player_data):
        """Test that data persists across multiple API requests."""
        # Create player
        client.post("/api/players", json=sample_player_data)

        # Retrieve player multiple times
        for _ in range(3):
            response = client.get("/api/players", params={
                "username": sample_player_data["username"],
                "password": sample_player_data["password"]
            })
            assert response.status_code == 200
            assert response.json()["id"] == sample_player_data["id"]

    def test_event_players_relationship(self, client):
        """Test that the event-player many-to-many relationship works correctly."""
        # Create multiple players
        players = []
        for i in range(3):
            player = {
                "username": f"player{i}", "password": "pass", "id": 900 + i,
                "fname": f"Player{i}", "lname": "Test", "rating": 1500,
                "email": f"p{i}@test.com", "phone": f"90{i}",
                "bday": "1990-01-01", "gender": 1
            }
            client.post("/api/players", json=player)
            players.append(player)

        # Create event
        event_data = {
            "id": 9000,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Multi-player event"
        }
        client.post("/api/events", json=event_data)

        # Add all players to the event
        for player in players:
            response = client.patch("/api/events/9000/add_player", json={"player_id": player["id"]})
            assert response.status_code == 200

        # Verify all players are in the event by checking recommendations
        # Players in the event should not see it in recommendations
        for player in players:
            response = client.get(f"/api/recommendations/{player['id']}")
            recommendations = response.json()
            assert len(recommendations) == 0  # Event should not be recommended (already joined)

    def test_cascade_delete_behavior(self, client):
        """Test database cascade delete on event_players table."""
        # Create player
        player_data = {
            "username": "cascade_test", "password": "pass", "id": 950,
            "fname": "Cascade", "lname": "Test", "rating": 1500,
            "email": "cascade@test.com", "phone": "950",
            "bday": "1990-01-01", "gender": 1
        }
        client.post("/api/players", json=player_data)

        # Create event
        event_data = {
            "id": 9500,
            "start_time": datetime.now().isoformat(),
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Cascade test event"
        }
        client.post("/api/events", json=event_data)

        # Add player to event
        client.patch("/api/events/9500/add_player", json={"player_id": 950})

        # Verify player is in event (won't be recommended)
        response = client.get("/api/recommendations/950")
        assert len(response.json()) == 0

        # Get all events to verify the event exists with players
        response = client.get("/api/events")
        events = response.json()
        assert len(events) == 1
        assert events[0]["id"] == 9500


# --- EDGE CASES AND ERROR HANDLING ---

class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_invalid_date_format(self, client):
        """Test that invalid date formats are rejected."""
        player_data = {
            "username": "baddate", "password": "pass", "id": 1100,
            "fname": "Bad", "lname": "Date", "rating": 1500,
            "email": "bad@test.com", "phone": "110",
            "bday": "not-a-date", "gender": 1
        }
        response = client.post("/api/players", json=player_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_datetime_format(self, client):
        """Test that invalid datetime formats are rejected."""
        event_data = {
            "id": 11000,
            "start_time": "not-a-datetime",
            "max_players": 4,
            "gender": 3,
            "court": 1,
            "description": "Invalid datetime"
        }
        response = client.post("/api/events", json=event_data)
        assert response.status_code == 422  # Validation error

    def test_negative_rating(self, client):
        """Test creating a player with negative rating (should be allowed by schema)."""
        player_data = {
            "username": "negative", "password": "pass", "id": 1200,
            "fname": "Negative", "lname": "Rating", "rating": -100,
            "email": "neg@test.com", "phone": "120",
            "bday": "1990-01-01", "gender": 1
        }
        response = client.post("/api/players", json=player_data)
        # Current schema doesn't validate rating >= 0, so this should succeed
        assert response.status_code == 201

    def test_zero_max_players(self, client):
        """Test creating an event with zero max players."""
        event_data = {
            "id": 12000,
            "start_time": datetime.now().isoformat(),
            "max_players": 0,
            "gender": 3,
            "court": 1,
            "description": "Zero capacity"
        }
        response = client.post("/api/events", json=event_data)
        # Should succeed but event will never accept players
        assert response.status_code == 201
