import pytest
from fastapi.testclient import TestClient
import sqlite3
from datetime import datetime
from api import app, get_db   # assuming your FastAPI app is in api.py
from database import SQLiteDatabase, init_db


# --- In-memory DB fixture to override dependency ---
@pytest.fixture(autouse=True)
def use_in_memory_db(monkeypatch):
    """Override the DB dependency with an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_db(conn)
    db = SQLiteDatabase(conn)

    def _get_db_override():
        return db

    monkeypatch.setattr("api.get_db", _get_db_override)
    yield db
    conn.close()


@pytest.fixture
def client():
    """Returns a FastAPI TestClient with the overridden DB."""
    return TestClient(app)


# --- PLAYER TESTS ---
def test_create_and_get_player(client):
    new_player = {
        "username": "alex",
        "password": "secret",
        "id": 1,
        "fname": "Alex",
        "lname": "Murray",
        "rating": 1500,
        "email": "alex@example.com",
        "phone": "123-456-7890",
        "bday": "2000-01-01",
        "gender": 1
    }

    # Create player
    res = client.post("/api/players", json=new_player)
    assert res.status_code == 201
    data = res.json()
    assert data["fname"] == "Alex"
    assert data["gender"] == 1

    # Get player by credentials
    res2 = client.get("/api/players", params={"username": "alex", "password": "secret"})
    assert res2.status_code == 200
    player = res2.json()
    assert player["fname"] == "Alex"
    assert player["rating"] == 1500


def test_update_player_rating(client):
    # Create a player first
    client.post("/api/players", json={
        "username": "test",
        "password": "pass",
        "id": 2,
        "fname": "John",
        "lname": "Smith",
        "rating": 1300,
        "email": "john@example.com",
        "phone": "111-222-3333",
        "bday": "1999-05-05",
        "gender": 2
    })

    # Update rating
    res = client.patch("/api/players/2", json={"rating": 1550})
    assert res.status_code == 200
    assert res.json()["rating"] == 1550


def test_duplicate_username_rejected(client):
    player_json = {
        "username": "sameuser",
        "password": "pw",
        "id": 10,
        "fname": "A",
        "lname": "B",
        "rating": 1000,
        "email": "a@b.com",
        "phone": "999",
        "bday": "2000-01-01",
        "gender": 1
    }

    # First one succeeds
    res1 = client.post("/api/players", json=player_json)
    assert res1.status_code == 201

    # Second one should fail with 409
    res2 = client.post("/api/players", json=player_json)
    assert res2.status_code == 409


# --- EVENT TESTS ---
def test_create_event_and_add_remove_player(client):
    # Create player
    player_json = {
        "username": "p1",
        "password": "pw1",
        "id": 3,
        "fname": "Serena",
        "lname": "Williams",
        "rating": 2000,
        "email": "serena@example.com",
        "phone": "123-456-9999",
        "bday": "1985-09-26",
        "gender": 2
    }
    res = client.post("/api/players", json=player_json)
    assert res.status_code == 201

    # Create event
    event_json = {
        "start_time": datetime.now().isoformat(),
        "max_players": 4,
        "gender": 3,
        "court": 1,
        "description": "Mixed doubles match"
    }
    res2 = client.post("/api/events", json=event_json)
    assert res2.status_code == 201
    event = res2.json()
    event_id = event["id"]

    # Add player to event
    res3 = client.patch(f"/api/events/{event_id}/add_player", json={"player_id": 3})
    assert res3.status_code == 200
    updated_event = res3.json()
    assert updated_event["max_players"] == 4

    # Remove player
    res4 = client.patch(f"/api/events/{event_id}/remove_player", json={"player_id": 3})
    assert res4.status_code == 200


def test_add_player_to_nonexistent_event(client):
    # Create player
    player_json = {
        "username": "ghost",
        "password": "pw",
        "id": 4,
        "fname": "Ghost",
        "lname": "User",
        "rating": 1000,
        "email": "ghost@example.com",
        "phone": "000-000-0000",
        "bday": "1990-01-01",
        "gender": 1
    }
    client.post("/api/players", json=player_json)

    # Try adding player to event that doesn’t exist
    res = client.patch("/api/events/999/add_player", json={"player_id": 4})
    assert res.status_code == 404


def test_remove_player_not_in_event(client):
    # Create player and event
    client.post("/api/players", json={
        "username": "eve",
        "password": "pw",
        "id": 5,
        "fname": "Eve",
        "lname": "Adams",
        "rating": 1200,
        "email": "eve@example.com",
        "phone": "888",
        "bday": "1995-03-03",
        "gender": 2
    })

    event_json = {
        "start_time": datetime.now().isoformat(),
        "max_players": 2,
        "gender": 2,
        "court": 2,
        "description": "Singles Match"
    }
    res = client.post("/api/events", json=event_json)
    assert res.status_code == 201
    event_id = res.json()["id"]

    # Try removing player that was never added
    res2 = client.patch(f"/api/events/{event_id}/remove_player", json={"player_id": 5})
    assert res2.status_code == 404
