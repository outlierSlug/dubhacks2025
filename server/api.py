from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from Classes import Player, Event, DataBase
import sqlite3
from database import SQLiteDatabase, init_db, DB_NAME
from datetime import date, datetime

RATING_WINDOW = 5

app = FastAPI()

def get_db():
    """
    Initializes and returns a singleton SQLite database instance.
    Creates the database file and schema on first call.
    """
    if not hasattr(get_db, "_instance"):
        # Create connection to SQLite database
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        
        # Initialize the database schema
        init_db(conn)
        
        # Create the SQLiteDatabase instance
        get_db._instance = SQLiteDatabase(conn)
    
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

class EventPlayerUpdate(BaseModel):
    player_id: int

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
    end_time: datetime
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
    if db.get_player(info.id) is not None:
        raise HTTPException(status_code=409, detail=f"Player with id {info.id} already exists.")
    if not db.add_account(info.username, info.password, info.id):
        raise HTTPException(status_code=409, detail=f"Username already exists!")
    if not db.add_player(player):
        raise HTTPException(status_code=500, detail=f"Server Broken")
    return PlayerResponse(**player.__dict__)

@app.get("/api/players", response_model=PlayerResponse)
def get_player(username: str, password: str, db: DataBase = Depends(get_db)):
    """Gets a Player by account credentials"""
    pid = db.get_player_id(username, password)
    if pid is None:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
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
    if not db.update_player_rating(player_id, rating_update.rating):
            raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

    # Fetch and return the updated player
    player = db.get_player(player_id)
    return PlayerResponse(**player.__dict__)

@app.post("/api/events", status_code=201, response_model=EventResponse)
def new_event(info: NewEventRequest, db: DataBase = Depends(get_db)):
    """Creates a new event."""
    event = Event(info.id, info.start_time, info.max_players, info.gender, info.court, info.description)
    if not db.add_event(event): # add_event sets the id
        raise HTTPException(status_code=409, detail=f"Event with id {info.id} already exists.")
    return EventResponse(**event.__dict__)

@app.patch("/api/events/{event_id}/add_player", response_model=EventResponse)
def add_player_to_event(event_id: int, update: EventPlayerUpdate, db: DataBase = Depends(get_db)):
    """Adds a player to a specific event."""
    player = db.get_player(update.player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {update.player_id} not found")
    for event in db.all_events():
        if event.id == event_id:
            if not db.remove_event(event):
                raise HTTPException(status_code=500, detail="Failed to update event (remove step)")
            try:
                event.add_player(player)
            except PermissionError as e:
                db.add_event(event) 
                raise HTTPException(status_code=409, detail=str(e))
            if not db.add_event(event):
                raise HTTPException(status_code=500, detail="Failed to update event (add step)")
            return EventResponse(**event.__dict__)
    raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")


@app.patch("/api/events/{event_id}/remove_player", response_model=EventResponse)
def remove_player_from_event(event_id: int, update: EventPlayerUpdate, db: DataBase = Depends(get_db)):
    """Removes a player from a specific event."""
    player = db.get_player(update.player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {update.player_id} not found")
    
    event = None
    for ev in db.all_events():
        if ev.id == event_id:
            event = ev
            break
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    # Check if player is in the event
    if not any(p.id == update.player_id for p in event.players):
        raise HTTPException(status_code=404, detail=f"Player with id {update.player_id} not found in event {event_id}")
    
    # Remove player from event_players table
    if not db.remove_player_from_event(event_id, update.player_id):
        raise HTTPException(status_code=500, detail="Failed to remove player from event")
    
    # Check if event has any players left
    updated_event = None
    for ev in db.all_events():
        if ev.id == event_id:
            updated_event = ev
            break
    
    # If no players left, delete the event entirely
    if updated_event and len(updated_event.players) == 0:
        if not db.delete_event_by_id(event_id):  # Changed from remove_event
            raise HTTPException(status_code=500, detail="Failed to delete empty event")
        return EventResponse(
            id=event_id,
            start_time=event.start_time,
            end_time=event.end_time,
            max_players=event.max_players,
            gender=event.gender,
            court=event.court,
            description=event.description
        )
    
    # Return updated event
    if updated_event:
        return EventResponse(**updated_event.__dict__)
    
    raise HTTPException(status_code=404, detail=f"Event not found after removal")

@app.get("/api/events", response_model=List[EventResponse])
def get_all_events(db: DataBase = Depends(get_db)):
    """Fetches all events from the database."""
    events = db.all_events()
    return events

@app.get("/api/events/mine/{player_id}", response_model=List[EventResponse])
def get_my_events(player_id: int, db: DataBase = Depends(get_db)):
    """Return events that the given player is currently in."""
    mine = []
    for ev in db.all_events():
        if any(p.id == player_id for p in ev.players):
            mine.append(ev)
    return mine


@app.get("/api/recommendations/{player_id}", response_model=List[EventResponse])
def get_event_recommendations(player_id: int, db: DataBase = Depends(get_db)):
    """
    Recommends events for a player based on the rating range of
    players already in the event.
    """
    # 1. Get the player
    player = db.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")

    recommended_events = []
    all_events = db.all_events()

    # 2. Loop through all events
    for event in all_events:
        
        # --- Filter out ineligible events first ---

        # Skip if event is full
        if len(event.players) >= event.max_players:
            continue

        # Skip if player is already in the event
        if player in event.players:
            continue

        # Skip if gender doesn't match
        if event.gender < 3 and event.gender != player.gender:
            continue
        
        # If the event is empty, recommend it
        if not event.players:
            recommended_events.append(event)
            continue
            
        # If the event has players, calculate the range
        player_ratings = [p.rating for p in event.players]
        min_rating = min(player_ratings)
        max_rating = max(player_ratings)
        
        lower_bound = min_rating - RATING_WINDOW
        upper_bound = max_rating + RATING_WINDOW
        
        # 3. Check if player's rating is within the range
        if lower_bound <= player.rating <= upper_bound:
            recommended_events.append(event)

    # 4. Return the list
    return recommended_events
