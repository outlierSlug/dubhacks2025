import sqlite3
from typing import List
from datetime import datetime
from Classes import DataBase, Player, Event

DB_NAME = "tennis_system.db" # This will now only be used for the real app

def init_db(conn):
    """Initializes the database schema on the given connection."""
    cur = conn.cursor()

    """ Creates the Players table """
    cur.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        fname TEXT NOT NULL,
        lname TEXT NOT NULL,
        rating INTEGER,
        email TEXT,
        phone TEXT,
        bday TEXT,
        gender INTEGER
    )
    ''')

    """ Creates the Users table """
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        player_id INTEGER,
        FOREIGN KEY (player_id) REFERENCES players(id)
    )
    ''')

    """ Creates the Events table """
    cur.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        max_players INTEGER NOT NULL,
        gender INTEGER NOT NULL,
        court INTEGER NOT NULL,
        description TEXT
    )
    ''')

    """ Creates the event joins table """
    cur.execute('''
    CREATE TABLE IF NOT EXISTS event_players (
        event_id INTEGER,
        player_id INTEGER,
        PRIMARY KEY (event_id, player_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
    )
    ''')
    # Also added ON DELETE CASCADE to simplify removals
    conn.commit()


class SQLiteDatabase(DataBase):
    def __init__(self, conn):
        """Initializes the database with a connection object."""
        self.conn = conn

    def add_player(self, player: Player) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO players (id, fname, lname, rating, email, phone, bday, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player.id, player.fname, player.lname, player.rating, player.email,
                  player.phone, player.bday.isoformat(), player.gender))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding player: {e}")
            return False

    def remove_player(self, player: Player) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM players WHERE id = ?', (player.id,))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Error removing player: {e}")
            return False

    def update_player_rating(self, player_id: int, new_rating: int) -> bool:
        try: 
            cur = self.conn.cursor()
            cur.execute('UPDATE players SET rating = ? WHERE id = ?', (new_rating, player_id))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e: 
            print(f"Error updating player rating: {e}")
            return False

    def add_event(self, event: Event) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO events (id, start_time, end_time, max_players, gender, court, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event.id, event.start_time.isoformat(), event.end_time.isoformat(),
                  event.max_players, event.gender, event.court, event.description))

            for player in event.players:
                # Use INSERT OR IGNORE to avoid UNIQUE constraint violations
                cur.execute('INSERT OR IGNORE INTO event_players (event_id, player_id) VALUES (?, ?)',
                          (event.id, player.id))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding event: {e}")
            return False

    def remove_event(self, event: Event) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM events WHERE id = ?', (event.id,))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Error removing event: {e}")
            return False
    def delete_event_by_id(self, event_id: int) -> bool:
        """Deletes an event entirely from the database by ID"""
        try:
            cur = self.conn.cursor()
            
            # First delete all event_players entries (should already be done, but just in case)
            cur.execute('DELETE FROM event_players WHERE event_id = ?', (event_id,))
            
            # Then delete the event itself
            cur.execute('DELETE FROM events WHERE id = ?', (event_id,))
            
            rows_deleted = cur.rowcount
            print(f"Deleted event {event_id}, rows affected: {rows_deleted}")
            
            self.conn.commit()
            return rows_deleted > 0
        except Exception as e:
            print(f"Error removing event: {e}")
            return False
        
    def remove_player_from_event(self, event_id: int, player_id: int) -> bool:
        """Removes a player from an event by deleting from event_players table"""
        try:
            cur = self.conn.cursor()
            
            # Check if the relationship exists
            cur.execute('''
                SELECT * FROM event_players 
                WHERE event_id = ? AND player_id = ?
            ''', (event_id, player_id))
            result = cur.fetchone()
            
            if not result:
                return False
            
            # Delete the relationship
            cur.execute('''
                DELETE FROM event_players 
                WHERE event_id = ? AND player_id = ?
            ''', (event_id, player_id))
            
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Error removing player from event: {e}")
            return False

    def all_players(self) -> List[Player]:
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM players')
            rows = cur.fetchall()
            return [self._row_to_player(row) for row in rows]
        except Exception as e:
            print(f"Error fetching players: {e}")
            return []

    def all_events(self) -> List[Event]:
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM events')
            event_rows = cur.fetchall()

            events = []
            for row in event_rows:
                event = self._row_to_event(row)
                cur.execute('''
                    SELECT p.* FROM players p
                    JOIN event_players ep ON p.id = ep.player_id
                    WHERE ep.event_id = ?
                ''', (event.id,))
                player_rows = cur.fetchall()
                event.players = [self._row_to_player(p_row) for p_row in player_rows]
                events.append(event)
            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []

    def get_player(self, id: int) -> Player:
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM players WHERE id = ?', (id,))
            row = cur.fetchone()
            if row:
                return self._row_to_player(row)
            return None
        except Exception as e:
            print(f"Error fetching player: {e}")
            return None

    def get_player_id(self, username: str, password: str) -> int:
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT player_id FROM users WHERE username = ? AND password = ?',
                      (username, password))
            row = cur.fetchone()
            if row:
                return row[0]
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def add_account(self, username: str, password: str, player_id) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO users (username, password, player_id)
                VALUES (?, ?, ?)
            ''', (username, password, player_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating account: {e}")
            return False

    def remove_account(self, username: str) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM users WHERE username = ?', (username,))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Error removing account: {e}")
            return False

    def _row_to_player(self, row) -> Player:
        from datetime import date
        return Player(
            id=row[0],
            fname=row[1],
            lname=row[2],
            rating=row[3],
            email=row[4],
            phone=row[5],
            bday=date.fromisoformat(row[6]) if row[6] else None,
            gender=row[7]
        )

    def _row_to_event(self, row) -> Event:
        event = Event(
            id=row[0],
            start_time=datetime.fromisoformat(row[1]),
            max_players=row[3],
            gender=row[4],
            court=row[5],
            description=row[6]
        )
        event.players = []
        return event