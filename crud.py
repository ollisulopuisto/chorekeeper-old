from sqlalchemy.orm import Session
import models, schemas
import datetime
from datetime import date, timedelta, UTC

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Chore CRUD
def get_chore(db: Session, chore_id: int):
    return db.query(models.Chore).filter(models.Chore.id == chore_id).first()

def get_chore_by_name(db: Session, name: str):
    return db.query(models.Chore).filter(models.Chore.name == name).first()

def get_chores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Chore).offset(skip).limit(limit).all()

def create_chore(db: Session, chore: schemas.ChoreCreate):
    db_chore = models.Chore(name=chore.name, schedule=chore.schedule)
    db.add(db_chore)
    db.commit()
    db.refresh(db_chore)
    return db_chore

# Completion CRUD
def create_completion(db: Session, chore_id: int, user_id: int):
    db_completion = models.Completion(chore_id=chore_id, user_id=user_id, completed_at=datetime.datetime.now(UTC))
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion

def get_completions_by_user_and_chore(db: Session, user_id: int, chore_id: int):
    return db.query(models.Completion).filter(
        models.Completion.user_id == user_id,
        models.Completion.chore_id == chore_id
    ).order_by(models.Completion.completed_at.desc()).all()

def is_chore_completed_today(db: Session, user_id: int, chore_id: int) -> bool:
    today = date.today()
    completion = db.query(models.Completion).filter(
        models.Completion.user_id == user_id,
        models.Completion.chore_id == chore_id,
        models.Completion.completed_at >= today,
        models.Completion.completed_at < today + timedelta(days=1)
    ).first()
    return completion is not None
