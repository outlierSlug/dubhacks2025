# test_tennis_system.py
import pytest
import sqlite3
from datetime import date, datetime
from Classes import Player, Event
from database import SQLiteDatabase, init_db # Note the changed imports

@pytest.fixture
def db():
    """Fixture to set up and tear down an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    db_instance = SQLiteDatabase(conn)
    yield db_instance
    conn.close()

def test_add_and_fetch_player(db: SQLiteDatabase):
    player = Player(id=1, fname="Rafael", lname="Nadal", rating=2500, email="rafa@nadal.com",
                    phone="555-1212", bday=date(1986, 6, 3), gender=1)
    
    assert db.add_player(player)
    assert player.id is not None

    players = db.all_players()
    assert len(players) == 1
    p = players[0]
    assert p.fname == "Rafael"
    assert p.email == "rafa@nadal.com"

def test_remove_player(db: SQLiteDatabase):
    player = Player(id=2, fname="Roger", lname="Federer", rating=2600, email="roger@fed.com",
                    phone="555-1111", bday=date(1981, 8, 8), gender=1)
    db.add_player(player)
    
    assert db.remove_player(player)
    assert db.all_players() == []

def test_add_and_fetch_event(db: SQLiteDatabase):
    p1 = Player(id=3, fname="Novak", lname="Djokovic", rating=2550, email="djoko@serb.com",
                phone="555-9999", bday=date(1987, 5, 22), gender=1)
    p2 = Player(id=4, fname="Andy", lname="Murray", rating=2450, email="andy@uk.com",
                phone="555-7777", bday=date(1987, 5, 15), gender=1)
    db.add_player(p1)
    db.add_player(p2)

    start_time = datetime.now()
    event = Event(id=1, start_time=start_time, max_players=2, gender=1, court=1, description="Men's Singles Final")
    event.add_player(p1)
    event.add_player(p2)

    assert db.add_event(event)
    assert event.id is not None

    events = db.all_events()
    assert len(events) == 1
    e = events[0]
    assert len(e.players) == 2

# You must also update your other tests to accept the 'db' fixture
def test_remove_event_removes_links(db: SQLiteDatabase):
    player = Player(id=5, fname="Serena", lname="Williams", rating=2400,
                    email="serena@tennis.com", phone="555-2222",
                    bday=date(1981, 9, 26), gender=2)
    db.add_player(player)

    start = datetime.now()
    event = Event(id=2, start_time=start, max_players=1, gender=2, court=3, description="Women's Singles")
    event.add_player(player)
    db.add_event(event)

    assert len(db.all_events()) == 1
    assert db.remove_event(event)
    assert len(db.all_events()) == 0

# Note: The tests that don't need the database don't need the fixture
def test_add_player_lock():
    start_time = datetime.now()
    event = Event(id=3, start_time=start_time, max_players=1, gender=1, court=2, description="Singles Match")
    p1 = Player(id=6, fname="Carlos", lname="Alcaraz", rating=2400, email="carlos@tennis.com",
                phone="555-3333", bday=date(2003, 5, 5), gender=1)
    p2 = Player(id=7, fname="Jannik", lname="Sinner", rating=2380, email="jannik@tennis.com",
                phone="555-4444", bday=date(2001, 8, 16), gender=1)
    event.add_player(p1)
    with pytest.raises(PermissionError):
        event.add_player(p2)

def test_player_age_calculation():
    p = Player(id=8, fname="Test", lname="Player", rating=2000, email="test@player.com",
               phone="555-5555", bday=date(2000, 1, 1), gender=1)
    age = p.get_age()
    assert isinstance(age, int)
    assert 20 < age < 40