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

---

## Home Assistant Integration

ChoreKeeper is designed to integrate with Home Assistant. By using Home Assistant's `rest_command` and `rest` sensor platforms, you can create a seamless experience for managing chores directly from your dashboard.

First, ensure the ChoreKeeper container is running and accessible from your Home Assistant instance. You will need to know the IP address of the machine running Docker. In the examples below, replace `<chorekeeper_ip>` with this IP address.

### 1. Creating a Service to Complete Chores

You can create a RESTful command in Home Assistant to call the `POST /api/complete` endpoint. This allows you to mark a chore as done from automations or UI elements like buttons.

Add the following to your `configuration.yaml`:

```yaml
rest_command:
  chore_done:
    url: "http://<chorekeeper_ip>:8000/api/complete"
    method: "POST"
    headers:
      content-type: "application/json"
    payload: '{"chore_name": "{{ chore_name }}", "user_name": "{{ user_name }}"}'
```

After restarting Home Assistant, you can call the `rest_command.chore_done` service and pass `chore_name` and `user_name` as variables.

### 2. Creating Sensors to Display Chore Status

To display chore information in Home Assistant, you can configure RESTful sensors that fetch data from the `GET /api/status/{user_name}` endpoint.

This example creates sensors for a user named "billy". Add the following to your `configuration.yaml`:

```yaml
rest:
  - resource: http://<chorekeeper_ip>:8000/api/status/billy
    scan_interval: 60 # Fetches data every 60 seconds
    sensor:
      # Sensor for a specific chore's streak
      - name: "Billy Chore Streak Trash"
        value_template: >
          {{ value_json.streaks | selectattr('chore_name', 'eq', 'Take out Trash') | map(attribute='current_streak') | first | default(0) }}

      # Sensor for the number of pending chores today
      - name: "Billy Chores Pending"
        value_template: >
          {{ value_json.chores_today | rejectattr('completed', 'eq', true) | list | count }}
        # Store the full API response in attributes for more advanced Lovelace cards
        json_attributes:
          - chores_today
          - streaks
```

This configuration will create two new sensors:
- `sensor.billy_chore_streak_trash`: Displays the current streak for the "Take out Trash" chore.
- `sensor.billy_chores_pending`: Displays the count of chores that are due but not yet completed today. The attributes of this sensor will contain the full list of today's chores and all streaks, which you can use in custom Lovelace cards.

You can then add these sensors to your Home Assistant dashboard.