from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

# Chore Status
class ChoreStatus(BaseModel):
    name: str
    completed: bool

# Streak
class Streak(BaseModel):
    chore_name: str
    current_streak: int

# User Status
class UserStatus(BaseModel):
    user_name: str
    chores_today: List[ChoreStatus]
    streaks: List[Streak]

# User
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Chore
class ChoreBase(BaseModel):
    name: str
    schedule: str

class ChoreCreate(ChoreBase):
    pass

class Chore(ChoreBase):
    id: int
    name: str
    schedule: str
    model_config = ConfigDict(from_attributes=True)

# Completion
class CompletionBase(BaseModel):
    chore_name: str
    user_name: str

class CompletionCreate(CompletionBase):
    pass

class Completion(BaseModel):
    message: str
    timestamp: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
