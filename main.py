from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/complete", response_model=schemas.Completion)
def complete_chore(completion: schemas.CompletionCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=completion.user_name)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{completion.user_name}' not found.")
    
    chore = crud.get_chore_by_name(db, name=completion.chore_name)
    if not chore:
        raise HTTPException(status_code=404, detail=f"Chore '{completion.chore_name}' not found.")

    db_completion = crud.create_completion(db=db, chore_id=chore.id, user_id=user.id)
    
    return {
        "message": f"Chore '{chore.name}' marked as complete for user '{user.username}'.",
        "timestamp": db_completion.completed_at
    }

@app.get("/api/admin/chores", response_model=List[schemas.Chore])
def read_chores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chores = crud.get_chores(db, skip=skip, limit=limit)
    return chores

@app.get("/api/status/{user_name}", response_model=schemas.UserStatus)
def get_user_status(user_name: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=user_name)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_name}' not found.")

    all_chores = crud.get_chores(db)
    today_weekday = date.today().weekday()

    chores_today = []
    for chore in all_chores:
        if str(today_weekday) in chore.schedule.split(','):
            completed = crud.is_chore_completed_today(db, user_id=user.id, chore_id=chore.id)
            chores_today.append(schemas.ChoreStatus(name=chore.name, completed=completed))

    streaks = []
    for chore in all_chores:
        streak = calculate_streak(db, user.id, chore)
        streaks.append(schemas.Streak(chore_name=chore.name, current_streak=streak))

    return schemas.UserStatus(
        user_name=user.username,
        chores_today=chores_today,
        streaks=streaks
    )

def calculate_streak(db: Session, user_id: int, chore: models.Chore) -> int:
    completions = crud.get_completions_by_user_and_chore(db, user_id=user_id, chore_id=chore.id)
    completion_dates = {c.completed_at.date() for c in completions}
    
    schedule_days = [int(d) for d in chore.schedule.split(',')]
    if not schedule_days:
        return 0

    streak = 0
    cursor_date = date.today()
    
    # Find the most recent schedule date (could be today)
    # If today is not a schedule day, find the last one.
    days_since_last_scheduled = 0
    while cursor_date.weekday() not in schedule_days:
        cursor_date -= timedelta(days=1)
        days_since_last_scheduled += 1
        # break if we go back too far, e.g. more than a week
        if days_since_last_scheduled > 7:
            return 0 # No scheduled days in the last week, so streak is 0

    # Now cursor_date is on a scheduled day. Let's check the streak.
    while True:
        if cursor_date.weekday() in schedule_days:
            if cursor_date in completion_dates:
                streak += 1
            else:
                # First missed day breaks the streak
                break
        
        # Move to the previous day
        cursor_date -= timedelta(days=1)
        
        # Find the next scheduled day backwards
        while cursor_date.weekday() not in schedule_days:
            cursor_date -= timedelta(days=1)
            # Safety break for sparse schedules
            if (date.today() - cursor_date).days > 365 * 5: # 5 years
                 return streak


    return streak

@app.get("/")
def read_root():
    return {"Hello": "World"}
