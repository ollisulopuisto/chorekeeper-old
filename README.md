# ChoreKeeper

ChoreKeeper is a lightweight, containerized web application that manages all the logic for a family chore system. It exposes a simple REST API that allows other services (like Home Assistant) to mark chores as complete and retrieve current stats, such as streaks and pending tasks.

## Features

- **Chore Management**: Define chores with recurring schedules.
- **User Management**: Track chores for multiple users.
- **Completion Tracking**: Log every time a user completes a chore.
- **Streak Calculation**: Automatically calculate consecutive completions.
- **Dynamic Task List**: Get a list of chores due today for a given user.
- **Data Persistence**: All data is stored in a simple, persistent SQLite database.

## Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **Database**: SQLite
- **Containerization**: Docker

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chorekeeper
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

---

## Running the Application

You can run the application either directly with Uvicorn for development or using Docker for a production-like environment.

### Running with Uvicorn (Development)

This method is great for development as it provides hot-reloading.

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### Running with Docker (Production)

This is the recommended way to run the application in production. It uses Docker and Docker Compose to build and run the containerized application.

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`. The SQLite database file (`chorekeeper.db`) will be persisted in the project root directory.

---

## API Usage

The API provides endpoints for managing and tracking chores. Interactive documentation is available at `http://localhost:8000/docs` when the application is running.

### Endpoints

#### `POST /api/complete`

Marks a chore as completed for a specific user.

**Request Body:**
```json
{
  "chore_name": "Take out Trash",
  "user_name": "billy"
}
```

**Example `curl`:**
```bash
curl -X POST "http://localhost:8000/api/complete" \
-H "Content-Type: application/json" \
-d '{"chore_name": "Take out Trash", "user_name": "billy"}'
```

#### `GET /api/status/{user_name}`

Retrieves a full status report for a given user, including chores due today and current streaks.

**Example `curl`:**
```bash
curl -X GET "http://localhost:8000/api/status/billy"
```

#### `GET /api/admin/chores`

Lists all defined chores and their schedules.

**Example `curl`:**
```bash
curl -X GET "http://localhost:8000/api/admin/chores"
```

---

## Running Tests

The project uses `pytest` for unit testing.

To run the test suite, execute the following command from the project root directory:

```bash
pytest
```
