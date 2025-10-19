from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from Classes import Player, Event, DataBase
from datetime import date, datetime

app = FastAPI()


def get_db():
    class MockDatabase(DataBase):
        def __init__(self):
            self._players: List[Player] = []
            self._events: List[Event] = []
            self._accounts: dict[str, tuple[str, int]] = {}  # username -> (password, player_id)

        # --- Player methods ---
        def add_player(self, player: Player) -> bool:
            if any(p.id == player.id for p in self._players):
                return False
            self._players.append(player)
            return True

        def remove_player(self, player: Player) -> bool:
            if player in self._players:
                self._players.remove(player)
                return True
            return False

        # --- Event methods ---
        def add_event(self, event: Event) -> bool:
            if any(e.id == event.id for e in self._events):
                return False
            self._events.append(event)
            return True

        def remove_event(self, event: Event) -> bool:
            if event in self._events:
                self._events.remove(event)
                return True
            return False

        # --- Account methods ---
        def add_account(self, username: str, password: str, player_id: int) -> bool:
            if username in self._accounts:
                return False
            self._accounts[username] = (password, player_id)
            return True

        def get_player_id(self, username: str, password: str) -> Optional[Player]:
            record = self._accounts.get(username)
            if not record or record[0] != password:
                return None
            pid = record[1]
            for player in self._players:
                if player.id == pid:
                    return player
            return None

        # --- Retrieval methods ---
        def all_players(self) -> List[Player]:
            return list(self._players)

        def all_events(self) -> List[Event]:
            return list(self._events)

    if not hasattr(get_db, "_instance"):
        get_db._instance = MockDatabase()

    return get_db._instance


# --- CORS and port validation ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class NewPlayer(BaseModel):
    username: str
    password: str

    id: int
    fname: str
    lname: str
    rating: int
    email: str
    phone: str
    bday: date
    gender: int

class Account(BaseModel):
    username: str
    password: str

class NewEventRequest(BaseModel):
    id: int
    start_time: datetime
    max_players: int
    gender: int
    court: int
    description: str

class PlayerRatingUpdate(BaseModel):
    rating: int

class PlayerResponse(BaseModel):
    id: int
    fname: str
    lname: str
    rating: int
    email: str
    phone: str
    bday: date
    gender: int

class EventResponse(BaseModel):
    id: int
    start_time: datetime
    max_players: int
    gender: int
    court: int
    description: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"message": "Tennis Organizer API is up and running!"}

@app.post("/api/players", status_code=201, response_model=PlayerResponse)
def new_player(info: NewPlayer, db: DataBase = Depends(get_db)):
    """Adds a new Player"""
    player = Player(info.id, info.fname, info.lname, info.rating, info.email, info.phone, info.bday, info.gender)
    if not db.add_account(info.username, info.password, info.id):
        raise HTTPException(status_code=409, detail=f"Username already exists!")
    if not db.add_player(player):
        raise HTTPException(status_code=409, detail=f"Player with id {info.id} already exists.")
    return PlayerResponse(**player.__dict__)

@app.get("/api/player", response_model=PlayerResponse)
def get_player(username: str, password: str, db: DataBase = Depends(get_db)):
    """Gets a Player by account credentials"""
    pid = db.get_player_id(username, password)
    if pid is None:
        raise HTTPException(status_code=404, detail="Username/Password not found")
    player = next((p for p in db.all_players() if p.id == pid), None)
    if not player:
        raise HTTPException(status_code=500, detail="Player ID exists in accounts but not in player list - State Error")
    
    return PlayerResponse(**player.__dict__)


@app.patch("/api/players/{player_id}", response_model=PlayerResponse)
def update_player_rating(player_id: int, rating_update: PlayerRatingUpdate, db: DataBase = Depends(get_db)):
    """
    Updates the rating for a specific player.
    Finds the player by their ID from the URL path.
    """
    players = db.all_players()
    for player in players:
        if player.id == player_id:
            db.remove_player(player)
            player.rating = rating_update.rating
            db.add_player(player)
            return PlayerResponse(**player.__dict__)
    raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

@app.post("/api/events", status_code=201, response_model=EventResponse)
def new_event(info: NewEventRequest, db: DataBase = Depends(get_db)):
    """Creates a new event."""
    event = Event(info.id, info.start_time, info.max_players, info.gender, info.court, info.description)
    if not db.add_event(event):
        raise HTTPException(status_code=409, detail=f"Event with id {info.id} already exists.")
    return EventResponse(**event.__dict__)


