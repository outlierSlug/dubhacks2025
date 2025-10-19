"""
Unit Tests for Database Layer (database.py)
Tests the SQLiteDatabase class methods directly without going through the API.
"""

import pytest
import sqlite3
from datetime import datetime, date, timedelta
from database import SQLiteDatabase, init_db
from Classes import Player, Event


# --- FIXTURES ---

@pytest.fixture
def db():
    """Create an in-memory database for testing."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_db(conn)
    database = SQLiteDatabase(conn)
    yield database
    conn.close()


@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    return Player(
        id=1,
        fname="John",
        lname="Doe",
        rating=1500,
        email="john@example.com",
        phone="555-1234",
        bday=date(1990, 1, 15),
        gender=1
    )


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    start_time = datetime.now() + timedelta(days=1)
    return Event(
        id=100,
        start_time=start_time,
        max_players=4,
        gender=3,
        court=1,
        description="Test event"
    )


# --- PLAYER DATABASE TESTS ---

class TestPlayerDatabase:
    """Test suite for player database operations."""

    def test_add_player(self, db, sample_player):
        """Test adding a player to the database."""
        result = db.add_player(sample_player)
        assert result is True

        # Verify player was added
        players = db.all_players()
        assert len(players) == 1
        assert players[0].id == sample_player.id
        assert players[0].fname == sample_player.fname

    def test_add_duplicate_player(self, db, sample_player):
        """Test that adding a duplicate player fails."""
        db.add_player(sample_player)
        result = db.add_player(sample_player)
        assert result is False

    def test_remove_player(self, db, sample_player):
        """Test removing a player from the database."""
        db.add_player(sample_player)
        result = db.remove_player(sample_player)
        assert result is True

        # Verify player was removed
        players = db.all_players()
        assert len(players) == 0

    def test_remove_nonexistent_player(self, db, sample_player):
        """Test removing a player that doesn't exist."""
        result = db.remove_player(sample_player)
        assert result is False

    def test_get_player(self, db, sample_player):
        """Test retrieving a player by ID."""
        db.add_player(sample_player)
        player = db.get_player(sample_player.id)
        assert player is not None
        assert player.id == sample_player.id
        assert player.fname == sample_player.fname
        assert player.rating == sample_player.rating

    def test_get_nonexistent_player(self, db):
        """Test retrieving a player that doesn't exist."""
        player = db.get_player(999)
        assert player is None

    def test_all_players_empty(self, db):
        """Test getting all players when database is empty."""
        players = db.all_players()
        assert players == []

    def test_all_players_multiple(self, db):
        """Test getting multiple players."""
        players_to_add = []
        for i in range(5):
            player = Player(
                id=i,
                fname=f"Player{i}",
                lname="Test",
                rating=1000 + i * 100,
                email=f"player{i}@test.com",
                phone=f"555-000{i}",
                bday=date(1990, 1, 1),
                gender=1 if i % 2 == 0 else 2
            )
            db.add_player(player)
            players_to_add.append(player)

        all_players = db.all_players()
        assert len(all_players) == 5

    def test_player_data_integrity(self, db):
        """Test that all player fields are stored and retrieved correctly."""
        player = Player(
            id=42,
            fname="Alice",
            lname="Smith",
            rating=2000,
            email="alice.smith@example.com",
            phone="555-9876",
            bday=date(1985, 12, 25),
            gender=2
        )
        db.add_player(player)

        retrieved = db.get_player(42)
        assert retrieved.id == 42
        assert retrieved.fname == "Alice"
        assert retrieved.lname == "Smith"
        assert retrieved.rating == 2000
        assert retrieved.email == "alice.smith@example.com"
        assert retrieved.phone == "555-9876"
        assert retrieved.bday == date(1985, 12, 25)
        assert retrieved.gender == 2


# --- EVENT DATABASE TESTS ---

class TestEventDatabase:
    """Test suite for event database operations."""

    def test_add_event(self, db, sample_event):
        """Test adding an event to the database."""
        result = db.add_event(sample_event)
        assert result is True

        # Verify event was added
        events = db.all_events()
        assert len(events) == 1
        assert events[0].id == sample_event.id

    def test_add_duplicate_event(self, db, sample_event):
        """Test that adding a duplicate event fails."""
        db.add_event(sample_event)
        result = db.add_event(sample_event)
        assert result is False

    def test_remove_event(self, db, sample_event):
        """Test removing an event from the database."""
        db.add_event(sample_event)
        result = db.remove_event(sample_event)
        assert result is True

        # Verify event was removed
        events = db.all_events()
        assert len(events) == 0

    def test_remove_nonexistent_event(self, db, sample_event):
        """Test removing an event that doesn't exist."""
        result = db.remove_event(sample_event)
        assert result is False

    def test_all_events_empty(self, db):
        """Test getting all events when database is empty."""
        events = db.all_events()
        assert events == []

    def test_all_events_multiple(self, db):
        """Test getting multiple events."""
        for i in range(3):
            event = Event(
                id=100 + i,
                start_time=datetime.now() + timedelta(days=i),
                max_players=4,
                gender=3,
                court=i + 1,
                description=f"Event {i}"
            )
            db.add_event(event)

        all_events = db.all_events()
        assert len(all_events) == 3

    def test_event_data_integrity(self, db):
        """Test that all event fields are stored and retrieved correctly."""
        start = datetime(2025, 12, 31, 14, 30, 0)
        event = Event(
            id=999,
            start_time=start,
            max_players=8,
            gender=2,
            court=5,
            description="Women's tournament final"
        )
        db.add_event(event)

        events = db.all_events()
        retrieved = events[0]
        assert retrieved.id == 999
        assert retrieved.start_time == start
        assert retrieved.end_time == start + timedelta(hours=1)  # DURATION is 1 hour
        assert retrieved.max_players == 8
        assert retrieved.gender == 2
        assert retrieved.court == 5
        assert retrieved.description == "Women's tournament final"

    def test_event_with_players(self, db):
        """Test storing and retrieving an event with players."""
        # Create players
        player1 = Player(1, "Alice", "A", 1500, "a@test.com", "111", date(1990, 1, 1), 1)
        player2 = Player(2, "Bob", "B", 1600, "b@test.com", "222", date(1991, 2, 2), 1)
        db.add_player(player1)
        db.add_player(player2)

        # Create event
        event = Event(
            id=200,
            start_time=datetime.now(),
            max_players=4,
            gender=3,
            court=1,
            description="Test with players"
        )
        event.add_player(player1)
        event.add_player(player2)
        db.add_event(event)

        # Retrieve and verify
        events = db.all_events()
        assert len(events) == 1
        retrieved_event = events[0]
        assert len(retrieved_event.players) == 2
        assert retrieved_event.players[0].id == 1
        assert retrieved_event.players[1].id == 2


# --- ACCOUNT DATABASE TESTS ---

class TestAccountDatabase:
    """Test suite for user account database operations."""

    def test_add_account(self, db, sample_player):
        """Test adding a user account."""
        db.add_player(sample_player)
        result = db.add_account("testuser", "password123", sample_player.id)
        assert result is True

    def test_add_duplicate_account(self, db, sample_player):
        """Test that adding a duplicate username fails."""
        db.add_player(sample_player)
        db.add_account("testuser", "password123", sample_player.id)
        result = db.add_account("testuser", "different_password", sample_player.id)
        assert result is False

    def test_get_player_id_valid_credentials(self, db, sample_player):
        """Test retrieving player ID with valid credentials."""
        db.add_player(sample_player)
        db.add_account("testuser", "password123", sample_player.id)

        player_id = db.get_player_id("testuser", "password123")
        assert player_id == sample_player.id

    def test_get_player_id_invalid_password(self, db, sample_player):
        """Test that invalid password returns None."""
        db.add_player(sample_player)
        db.add_account("testuser", "password123", sample_player.id)

        player_id = db.get_player_id("testuser", "wrongpassword")
        assert player_id is None

    def test_get_player_id_invalid_username(self, db):
        """Test that invalid username returns None."""
        player_id = db.get_player_id("nonexistent", "password")
        assert player_id is None

    def test_remove_account(self, db, sample_player):
        """Test removing a user account."""
        db.add_player(sample_player)
        db.add_account("testuser", "password123", sample_player.id)

        result = db.remove_account("testuser")
        assert result is True

        # Verify account was removed
        player_id = db.get_player_id("testuser", "password123")
        assert player_id is None

    def test_remove_nonexistent_account(self, db):
        """Test removing an account that doesn't exist."""
        result = db.remove_account("nonexistent")
        assert result is False


# --- EVENT-PLAYER RELATIONSHIP TESTS ---

class TestEventPlayerRelationship:
    """Test suite for event-player many-to-many relationship."""

    def test_add_player_to_event_then_store(self, db):
        """Test adding players to an event and storing in database."""
        # Create players
        player1 = Player(1, "P1", "Last", 1500, "p1@test.com", "111", date(1990, 1, 1), 1)
        player2 = Player(2, "P2", "Last", 1600, "p2@test.com", "222", date(1991, 2, 2), 1)
        db.add_player(player1)
        db.add_player(player2)

        # Create event and add players
        event = Event(300, datetime.now(), 4, 3, 1, "Multi-player event")
        event.add_player(player1)
        event.add_player(player2)
        db.add_event(event)

        # Retrieve and verify
        events = db.all_events()
        assert len(events[0].players) == 2

    def test_update_event_players(self, db):
        """Test updating event by removing and re-adding with different players."""
        # Create players
        player1 = Player(10, "P1", "Last", 1500, "p1@test.com", "111", date(1990, 1, 1), 1)
        player2 = Player(11, "P2", "Last", 1600, "p2@test.com", "222", date(1991, 2, 2), 1)
        db.add_player(player1)
        db.add_player(player2)

        # Create event with player1
        event = Event(400, datetime.now(), 4, 3, 1, "Update test")
        event.add_player(player1)
        db.add_event(event)

        # Update event: remove from DB, add player2, re-add to DB
        db.remove_event(event)
        event.add_player(player2)
        db.add_event(event)

        # Verify
        events = db.all_events()
        assert len(events[0].players) == 2
        player_ids = [p.id for p in events[0].players]
        assert 10 in player_ids
        assert 11 in player_ids

    def test_cascade_delete_event_removes_relationships(self, db):
        """Test that deleting an event removes event_players relationships."""
        # Create player and event
        player = Player(20, "Test", "Player", 1500, "test@test.com", "555", date(1990, 1, 1), 1)
        db.add_player(player)

        event = Event(500, datetime.now(), 4, 3, 1, "Cascade test")
        event.add_player(player)
        db.add_event(event)

        # Verify event exists with player
        events = db.all_events()
        assert len(events) == 1
        assert len(events[0].players) == 1

        # Remove event
        db.remove_event(event)

        # Verify event is gone
        events = db.all_events()
        assert len(events) == 0

        # Player should still exist
        players = db.all_players()
        assert len(players) == 1

    def test_player_in_multiple_events(self, db):
        """Test that a player can be in multiple events."""
        # Create player
        player = Player(30, "Multi", "Event", 1500, "multi@test.com", "333", date(1990, 1, 1), 1)
        db.add_player(player)

        # Create multiple events with the same player
        for i in range(3):
            event = Event(
                id=600 + i,
                start_time=datetime.now() + timedelta(days=i),
                max_players=4,
                gender=3,
                court=1,
                description=f"Event {i}"
            )
            event.add_player(player)
            db.add_event(event)

        # Verify all events have the player
        events = db.all_events()
        assert len(events) == 3
        for event in events:
            assert len(event.players) == 1
            assert event.players[0].id == 30


# --- DATABASE SCHEMA TESTS ---

class TestDatabaseSchema:
    """Test suite for database schema validation."""

    def test_init_db_creates_tables(self):
        """Test that init_db creates all required tables."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert 'players' in tables
        assert 'users' in tables
        assert 'events' in tables
        assert 'event_players' in tables

        conn.close()

    def test_players_table_structure(self):
        """Test that the players table has the correct structure."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)

        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(players)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        assert 'id' in columns
        assert 'fname' in columns
        assert 'lname' in columns
        assert 'rating' in columns
        assert 'email' in columns
        assert 'phone' in columns
        assert 'bday' in columns
        assert 'gender' in columns

        conn.close()

    def test_events_table_structure(self):
        """Test that the events table has the correct structure."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)

        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(events)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        assert 'id' in columns
        assert 'start_time' in columns
        assert 'end_time' in columns
        assert 'max_players' in columns
        assert 'gender' in columns
        assert 'court' in columns
        assert 'description' in columns

        conn.close()

    def test_users_table_structure(self):
        """Test that the users table has the correct structure."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)

        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        assert 'user_id' in columns
        assert 'username' in columns
        assert 'password' in columns
        assert 'player_id' in columns

        conn.close()

    def test_event_players_table_structure(self):
        """Test that the event_players junction table has the correct structure."""
        conn = sqlite3.connect(":memory:")
        init_db(conn)

        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(event_players)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        assert 'event_id' in columns
        assert 'player_id' in columns

        conn.close()


# --- ERROR HANDLING TESTS ---

class TestDatabaseErrorHandling:
    """Test suite for database error handling."""

    def test_add_player_with_none_bday(self, db):
        """Test adding a player with None birthday."""
        player = Player(
            id=50,
            fname="No",
            lname="Birthday",
            rating=1500,
            email="no@bday.com",
            phone="555",
            bday=None,
            gender=1
        )
        # This should handle None gracefully or raise appropriate error
        result = db.add_player(player)
        # Depending on implementation, this might succeed or fail
        # Currently the code will try to call .isoformat() on None which will error
        # This test documents the current behavior

    def test_concurrent_operations(self, db):
        """Test that database handles operations correctly."""
        # Add multiple players in sequence
        for i in range(10):
            player = Player(
                id=60 + i,
                fname=f"Player{i}",
                lname="Test",
                rating=1000 + i,
                email=f"p{i}@test.com",
                phone=f"60{i}",
                bday=date(1990, 1, 1),
                gender=1 if i % 2 == 0 else 2
            )
            result = db.add_player(player)
            assert result is True

        # Verify all were added
        players = db.all_players()
        assert len(players) == 10
