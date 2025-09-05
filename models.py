from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    completions = relationship("Completion", back_populates="user")

class Chore(Base):
    __tablename__ = "chores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    schedule = Column(String)  # e.g., "0,3" for Monday and Thursday

    completions = relationship("Completion", back_populates="chore")

class Completion(Base):
    __tablename__ = "completions"

    id = Column(Integer, primary_key=True, index=True)
    chore_id = Column(Integer, ForeignKey("chores.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime)

    chore = relationship("Chore", back_populates="completions")
    user = relationship("User", back_populates="completions")
