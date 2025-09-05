import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base
import crud, schemas, models
from datetime import date, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    # setup
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # add some test data
    crud.create_user(db, schemas.UserCreate(username="billy"))
    crud.create_user(db, schemas.UserCreate(username="sally"))
    crud.create_chore(db, schemas.ChoreCreate(name="Take out Trash", schedule="0,3")) # Mon, Thu
    crud.create_chore(db, schemas.ChoreCreate(name="Feed the Dog", schedule="0,1,2,3,4,5,6")) # Everyday

    yield db
    
    # teardown
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_complete_chore(db_session):
    response = client.post(
        "/api/complete",
        json={"chore_name": "Take out Trash", "user_name": "billy"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Chore 'Take out Trash' marked as complete for user 'billy'."
    assert "timestamp" in data

def test_get_status_no_completions(db_session):
    response = client.get("/api/status/billy")
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "billy"
    
    today_weekday = date.today().weekday()
    
    chores_today = data["chores_today"]
    if today_weekday in [0, 3]: # Mon, Thu
        assert {"name": "Take out Trash", "completed": False} in chores_today
    if today_weekday in [0,1,2,3,4,5,6]:
        assert {"name": "Feed the Dog", "completed": False} in chores_today

    streaks = data["streaks"]
    assert {"chore_name": "Take out Trash", "current_streak": 0} in streaks
    assert {"chore_name": "Feed the Dog", "current_streak": 0} in streaks

def test_streak_calculation(db_session):
    user = crud.get_user_by_username(db_session, "billy")
    chore = crud.get_chore_by_name(db_session, "Take out Trash") # Mon, Thu schedule

    # --- Test Case 1: No completions ---
    response = client.get("/api/status/billy")
    trash_streak = [s["current_streak"] for s in response.json()["streaks"] if s["chore_name"] == "Take out Trash"][0]
    assert trash_streak == 0

    # --- Test Case 2: One completion today (if it's a scheduled day) ---
    today = date.today()
    if today.weekday() in [0, 3]:
        crud.create_completion(db_session, chore_id=chore.id, user_id=user.id)
        response = client.get("/api/status/billy")
        trash_streak = [s["current_streak"] for s in response.json()["streaks"] if s["chore_name"] == "Take out Trash"][0]
        assert trash_streak == 1
    
    # Reset for next test case
    db_session.query(models.Completion).delete()
    db_session.commit()

    # --- Test Case 3: Perfect streak for 3 weeks ---
    # Let's find the last 6 schedule dates for Mon/Thu
    last_six_schedule_dates = []
    a_date = date.today()
    while len(last_six_schedule_dates) < 6:
        if a_date.weekday() in [0, 3]: # Mon, Thu
            last_six_schedule_dates.append(a_date)
        a_date -= timedelta(days=1)
    
    for completion_date in last_six_schedule_dates:
        # We need a way to set the completion date for testing
        db_completion = models.Completion(chore_id=chore.id, user_id=user.id, completed_at=completion_date)
        db_session.add(db_completion)
    db_session.commit()

    response = client.get("/api/status/billy")
    trash_streak = [s["current_streak"] for s in response.json()["streaks"] if s["chore_name"] == "Take out Trash"][0]
    assert trash_streak == 6

    # --- Test Case 4: Broken streak ---
    # Miss the most recent scheduled day
    db_session.query(models.Completion).delete()
    db_session.commit()
    
    # last 5, but skipping the most recent one
    for completion_date in last_six_schedule_dates[1:]:
        db_completion = models.Completion(chore_id=chore.id, user_id=user.id, completed_at=completion_date)
        db_session.add(db_completion)
    db_session.commit()
    
    response = client.get("/api/status/billy")
    trash_streak = [s["current_streak"] for s in response.json()["streaks"] if s["chore_name"] == "Take out Trash"][0]
    assert trash_streak == 0

def test_admin_chores(db_session):
    response = client.get("/api/admin/chores")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {"id": 1, "name": "Take out Trash", "schedule": "0,3"} in data
    assert {"id": 2, "name": "Feed the Dog", "schedule": "0,1,2,3,4,5,6"} in data
