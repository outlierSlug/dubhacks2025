# test_tennis_system.py
import pytest
import sqlite3
from datetime import date, datetime, timedelta
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

# Test get_player method
def test_get_player_existing(db: SQLiteDatabase):
    player = Player(id=9, fname="Maria", lname="Sharapova", rating=2300,
                    email="maria@tennis.com", phone="555-6666",
                    bday=date(1987, 4, 19), gender=2)
    db.add_player(player)

    retrieved = db.get_player(9)
    assert retrieved is not None
    assert retrieved.fname == "Maria"
    assert retrieved.lname == "Sharapova"
    assert retrieved.rating == 2300
    assert retrieved.email == "maria@tennis.com"
    assert retrieved.phone == "555-6666"
    assert retrieved.bday == date(1987, 4, 19)
    assert retrieved.gender == 2

def test_get_player_nonexistent(db: SQLiteDatabase):
    retrieved = db.get_player(999)
    assert retrieved is None

# Test authentication methods
def test_add_account_and_authenticate(db: SQLiteDatabase):
    player = Player(id=10, fname="Venus", lname="Williams", rating=2350,
                    email="venus@tennis.com", phone="555-7777",
                    bday=date(1980, 6, 17), gender=2)
    db.add_player(player)

    # Create account
    assert db.add_account("venus_w", "securepass123", 10)

    # Authenticate with correct credentials
    player_id = db.get_player_id("venus_w", "securepass123")
    assert player_id == 10

def test_authenticate_wrong_password(db: SQLiteDatabase):
    player = Player(id=11, fname="Pete", lname="Sampras", rating=2500,
                    email="pete@tennis.com", phone="555-8888",
                    bday=date(1971, 8, 12), gender=1)
    db.add_player(player)
    db.add_account("pete_s", "correctpass", 11)

    # Try wrong password
    player_id = db.get_player_id("pete_s", "wrongpass")
    assert player_id is None

def test_authenticate_nonexistent_user(db: SQLiteDatabase):
    player_id = db.get_player_id("nonexistent", "password")
    assert player_id is None

def test_add_duplicate_username(db: SQLiteDatabase):
    player1 = Player(id=12, fname="John", lname="McEnroe", rating=2400,
                     email="john@tennis.com", phone="555-9999",
                     bday=date(1959, 2, 16), gender=1)
    player2 = Player(id=13, fname="Bjorn", lname="Borg", rating=2450,
                     email="bjorn@tennis.com", phone="555-0000",
                     bday=date(1956, 6, 6), gender=1)
    db.add_player(player1)
    db.add_player(player2)

    # Create first account
    assert db.add_account("legend", "pass1", 12)

    # Try to create duplicate username (should fail due to UNIQUE constraint)
    assert not db.add_account("legend", "pass2", 13)

def test_remove_account_existing(db: SQLiteDatabase):
    player = Player(id=29, fname="Stan", lname="Wawrinka", rating=2400,
                    email="stan@tennis.com", phone="555-8080",
                    bday=date(1985, 3, 28), gender=1)
    db.add_player(player)
    db.add_account("stan_w", "password123", 29)

    # Remove the account
    assert db.remove_account("stan_w")

    # Verify account is removed - authentication should fail
    player_id = db.get_player_id("stan_w", "password123")
    assert player_id is None

def test_remove_account_nonexistent(db: SQLiteDatabase):
    # Try to remove an account that doesn't exist
    assert not db.remove_account("nonexistent_user")

def test_remove_account_player_remains(db: SQLiteDatabase):
    player = Player(id=30, fname="Dominic", lname="Thiem", rating=2380,
                    email="dominic@tennis.com", phone="555-9090",
                    bday=date(1993, 9, 3), gender=1)
    db.add_player(player)
    db.add_account("dominic_t", "password456", 30)

    # Remove the account
    assert db.remove_account("dominic_t")

    # Verify player still exists (only account is removed)
    retrieved_player = db.get_player(30)
    assert retrieved_player is not None
    assert retrieved_player.fname == "Dominic"
    assert retrieved_player.lname == "Thiem"

# Edge case tests
def test_add_player_with_duplicate_id(db: SQLiteDatabase):
    player1 = Player(id=14, fname="Steffi", lname="Graf", rating=2400,
                     email="steffi@tennis.com", phone="555-1010",
                     bday=date(1969, 6, 14), gender=2)
    player2 = Player(id=14, fname="Monica", lname="Seles", rating=2380,
                     email="monica@tennis.com", phone="555-2020",
                     bday=date(1973, 12, 2), gender=2)

    assert db.add_player(player1)
    # Duplicate ID should fail
    assert not db.add_player(player2)

def test_remove_nonexistent_player(db: SQLiteDatabase):
    player = Player(id=999, fname="Ghost", lname="Player", rating=2000,
                    email="ghost@tennis.com", phone="555-0000",
                    bday=date(1990, 1, 1), gender=1)
    # Should return False since player doesn't exist
    assert not db.remove_player(player)

def test_remove_nonexistent_event(db: SQLiteDatabase):
    start = datetime.now()
    event = Event(id=999, start_time=start, max_players=2, gender=1,
                  court=1, description="Ghost Event")
    # Should return False since event doesn't exist
    assert not db.remove_event(event)

def test_all_players_empty_database(db: SQLiteDatabase):
    players = db.all_players()
    assert players == []

def test_all_events_empty_database(db: SQLiteDatabase):
    events = db.all_events()
    assert events == []

def test_event_with_no_players(db: SQLiteDatabase):
    start = datetime.now()
    event = Event(id=15, start_time=start, max_players=4, gender=3,
                  court=2, description="Co-ed Doubles")

    assert db.add_event(event)
    events = db.all_events()
    assert len(events) == 1
    assert len(events[0].players) == 0

def test_multiple_events_for_same_player(db: SQLiteDatabase):
    player = Player(id=16, fname="Andre", lname="Agassi", rating=2450,
                    email="andre@tennis.com", phone="555-3030",
                    bday=date(1970, 4, 29), gender=1)
    db.add_player(player)

    start1 = datetime.now()
    event1 = Event(id=17, start_time=start1, max_players=2, gender=1,
                   court=1, description="Morning Match")
    event1.add_player(player)

    start2 = datetime.now() + timedelta(hours=3)
    event2 = Event(id=18, start_time=start2, max_players=2, gender=1,
                   court=2, description="Afternoon Match")
    event2.add_player(player)

    assert db.add_event(event1)
    assert db.add_event(event2)

    events = db.all_events()
    assert len(events) == 2

def test_gender_restriction_enforcement():
    start = datetime.now()
    mens_event = Event(id=19, start_time=start, max_players=2, gender=1,
                       court=1, description="Men's Singles")

    male_player = Player(id=20, fname="Jimmy", lname="Connors", rating=2400,
                         email="jimmy@tennis.com", phone="555-4040",
                         bday=date(1952, 9, 2), gender=1)
    female_player = Player(id=21, fname="Chris", lname="Evert", rating=2400,
                           email="chris@tennis.com", phone="555-5050",
                           bday=date(1954, 12, 21), gender=2)

    # Male player should be added successfully
    mens_event.add_player(male_player)
    assert len(mens_event.players) == 1

    # Female player should raise PermissionError
    with pytest.raises(PermissionError, match="This Event is marked as MENS"):
        mens_event.add_player(female_player)

def test_coed_event_accepts_both_genders():
    start = datetime.now()
    coed_event = Event(id=22, start_time=start, max_players=4, gender=3,
                       court=1, description="Mixed Doubles")

    male_player = Player(id=23, fname="Boris", lname="Becker", rating=2400,
                         email="boris@tennis.com", phone="555-6060",
                         bday=date(1967, 11, 22), gender=1)
    female_player = Player(id=24, fname="Martina", lname="Navratilova", rating=2450,
                           email="martina@tennis.com", phone="555-7070",
                           bday=date(1956, 10, 18), gender=2)

    # Both should be added successfully
    coed_event.add_player(male_player)
    coed_event.add_player(female_player)
    assert len(coed_event.players) == 2

def test_player_update_methods():
    player = Player(id=25, fname="Original", lname="Name", rating=2000,
                    email="original@email.com", phone="555-0000",
                    bday=date(1990, 1, 1), gender=1)

    # Test change_name
    player.change_name("Updated", "Player")
    assert player.fname == "Updated"
    assert player.lname == "Player"

    # Test change_email
    player.change_email("updated@email.com")
    assert player.email == "updated@email.com"

    # Test change_phone
    player.change_phone("555-9999")
    assert player.phone == "555-9999"

    # Test change_bday
    player.change_bday(date(1995, 5, 15))
    assert player.bday == date(1995, 5, 15)

    # Test change_gender
    player.change_gender(2)
    assert player.gender == 2

    # Test update_rating
    player.update_rating(2500)
    assert player.rating == 2500

def test_event_remove_player():
    start = datetime.now()
    event = Event(id=26, start_time=start, max_players=2, gender=1,
                  court=1, description="Test Match")

    player1 = Player(id=27, fname="Player", lname="One", rating=2000,
                     email="p1@tennis.com", phone="555-1111",
                     bday=date(1990, 1, 1), gender=1)
    player2 = Player(id=28, fname="Player", lname="Two", rating=2000,
                     email="p2@tennis.com", phone="555-2222",
                     bday=date(1990, 1, 1), gender=1)

    event.add_player(player1)
    event.add_player(player2)
    assert len(event.players) == 2

    # Remove existing player
    assert event.remove_player(player1)
    assert len(event.players) == 1
    assert player2 in event.players

    # Try to remove non-existent player
    assert not event.remove_player(player1)
    assert len(event.players) == 1