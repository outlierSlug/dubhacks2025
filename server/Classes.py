from typing import List
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

DURATION = 1 # Hours

"""
    MENS = 1
    WOMENS = 2
    CO_ED = 3
"""

class Player():
    def __init__(self, id: int, fname: str, lname: str, rating: int, email: str, phone: str, bday: date, gender: int):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.rating = rating
        self.email = email
        self.phone = phone
        self.bday = bday
        self.gender = gender

    def change_name(self, fname: str, lname: str):
        self.fname = fname
        self.lname = lname

    def change_bday(self, bday: date):
        self.bday = bday

    def change_email(self, email: str):
        self.email = email
    
    def change_phone(self, phone: str):
        self.phone = phone

    def change_gender(self, gender: int):
        self.gender = gender

    def update_rating(self, rating: int):
        self.rating = rating
    
    def get_age(self):
        today = date.today()
        age = today.year - self.bday.year - ((today.month, today.day) < (self.bday.month, self.bday.day))
        return age


class Event():
    def __init__(self, start_time: datetime = None, max_players: int = None, gender: int = None, court: int = None, description: str = None):
        self.id = None
        self.start_time = start_time
        self.duration = timedelta(hours = DURATION) if start_time else None
        self.end_time = self.start_time + self.duration if start_time else None

        self.players: List[Player] = []
        self.max_players = max_players

        self.gender = gender
        self.court = court
        self.description = description

    def add_player(self, player: Player):
        """Raises error if event is full"""
        if len(self.players) == self.max_players:
            raise PermissionError("This event is locked - no more sign-ups allowed")
        elif self.gender < 3 and (player.gender != self.gender):
            gender = "MENS" if self.gender == 1 else "WOMENS" if self.gender == 2 else "CO-ED"
            raise PermissionError(f"This Event is marked as {gender}!")
        self.players.append(player)

    def remove_player(self, player: Player) -> bool:
        """Returns true if player succesfully removed"""
        if player in self.players:
            self.players.remove(player)
            return True
        return False
    

class DataBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_player(self, player: Player) -> bool:
        pass

    @abstractmethod
    def remove_player(self, player: Player) -> bool:
        pass

    @abstractmethod
    def add_event(self, event: Event) -> bool:
        pass

    @abstractmethod
    def remove_event(self, event: Event) -> bool:
        pass

    @abstractmethod
    def all_players(self) -> List[Player]:
        pass

    @abstractmethod
    def all_events(self) -> List[Event]:
        pass
