# Project Progress: ChoreKeeper

This file tracks the development progress of the ChoreKeeper application.

## Milestones

- [ ] **Milestone 1: Project Setup & Core Models**
- [ ] **Milestone 2: API Endpoints**
- [ ] **Milestone 3: Core Logic**
- [ ] **Milestone 4: Containerization**
- [ ] **Milestone 5: Testing & Documentation**

## Development Tasks

### Milestone 1: Project Setup & Core Models

- [ ] Initialize Python project with FastAPI.
- [ ] Set up virtual environment and install dependencies (`fastapi`, `uvicorn`, `sqlalchemy`).
- [ ] Create `main.py` with a basic FastAPI app instance.
- [ ] Define database models for `User`, `Chore`, and `Completion` using SQLAlchemy.
- [ ] Implement database connection and session management.
- [ ] Create a script or function to initialize the database schema.

### Milestone 2: API Endpoints

- [ ] Implement `POST /api/complete` endpoint.
  - [ ] Add logic to find user and chore by name.
  - [ ] Create a new completion record.
  - [ ] Return success or error response.
- [ ] Implement `GET /api/status/{user_name}` endpoint.
  - [ ] Add logic to find user by name.
  - [ ] Determine which chores are due today for the user.
  - [ ] Check completion status for today's chores.
  - [ ] Calculate streaks for all of the user's chores.
  - [ ] Return the full status payload.
- [ ] Implement `GET /api/admin/chores` endpoint.
  - [ ] Retrieve all chores from the database.
  - [ ] Return the list of chores and their schedules.

### Milestone 3: Core Logic

- [ ] Implement the streak calculation logic.
  - [ ] Get chore schedule.
  - [ ] Fetch all completions for the chore and user.
  - [ ] Iterate backward through scheduled dates to find consecutive completions.

### Milestone 4: Containerization

- [ ] Create `Dockerfile`.
- [ ] Create `docker-compose.yml`.
- [ ] Add `requirements.txt`.

### Milestone 5: Testing & Documentation

- [ ] Write unit tests for the `POST /api/complete` endpoint.
- [ ] Write unit tests for the `GET /api/status/{user_name}` endpoint.
- [ ] Write unit tests for the streak calculation logic.
- [ ] Verify auto-generated API documentation (`/docs`).
