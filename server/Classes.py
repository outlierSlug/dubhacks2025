from enum import Enum
from typing import List
from datetime import date, datetime, timedelta

DURATION = 1 # Hours

class Gender(Enum):
    MALE = 1
    FEMALE = 2
    CO_ED = 3


class Player():
    def __init__(self, id: int, fname: str, lname: str, rating: int, email: str, phone: str, bday: date, gender: Gender):
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

    def change_gender(self, gender: Gender):
        self.gender = Gender

    def update_rating(self, rating: int):
        self.rating = rating
    
    def get_age(self):
        today = date.today()
        age = today.year - self.bday.year - ((today.month, today.day) < (self.bday.month, self.bday.day))
        return age


class Event():
    def init(self, start_time: datetime, max_players: int, gender: Gender, court: int, description: str):
        self.start_time = start_time
        self.duration = timedelta(hours = DURATION)
        self.end_time = self.start_time + self.duration 

        self.players: List[Player] = []
        self.max_players = max_players

        self.court = court
        self.description = description

    def add_player(self, player: Player):
        """Raises error if event is full"""
        if len(self.players) == self.max_players:
            raise PermissionError("This event is locked - no more sign-ups allowed")
        self.players.append(player)

    def remove_player(self, player: Player) -> bool:
        """Returns true if player succesfully removed"""
        if player in self.players:
            self.players.remove(player)
            return True
        return False
    

    
    
    

    
    


      
