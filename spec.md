# Project Specification: ChoreKeeper

1. High-Level Concept

ChoreKeeper is a lightweight, containerized web application that manages all the logic for a family chore system. It exposes a simple REST API that allows other services (like Home Assistant) to mark chores as complete and retrieve current stats, such as streaks and pending tasks. It maintains its own state in a dedicated database, completely separating the complex business logic from the front-end display in Home Assistant.

2. Core Features

Chore Management: Define chores with names and recurring schedules (e.g., "Take out Trash" every Monday and Thursday).
User Management: Track chores for multiple users (e.g., different kids).
Completion Tracking: Log every time a user completes a chore.
Streak Calculation: Automatically calculate the number of consecutive times a scheduled chore has been completed without being missed.
Dynamic Task List: The API will provide a list of which chores are due today for a given user.
Data Persistence: All data is stored in a simple, persistent database.

3. Technology Stack

Language: Python 3.9+ (universally understood and great for web services).
Web Framework: FastAPI. It's modern, incredibly fast, and automatically generates interactive API documentation, which is invaluable for development and debugging.
Database: SQLite. It's a simple, file-based database that requires no separate server, making it perfect for a self-contained Docker application. It can easily be swapped for PostgreSQL later if needed.
Containerization: Docker. The entire application and its dependencies will be packaged into a single Docker image for easy deployment.

4. Database Schema

We'll use three simple tables to structure the data.

1. users

id (Integer, Primary Key)
username (Text, Unique) - e.g., "billy", "sally"

2. chores

id (Integer, Primary Key)
name (Text, Unique) - e.g., "Feed the Dog"
schedule (Text) - A comma-separated string of integers for the day of the week (Monday=0, Sunday=6). e.g., "0,3" for Monday and Thursday.

3. completions

id (Integer, Primary Key)
chore_id (Integer, Foreign Key to chores.id)
user_id (Integer, Foreign Key to users.id)
completed_at (Timestamp) - The date and time the chore was marked as done.

4. API Endpoints (The Contract)
This is how Home Assistant will communicate with ChoreKeeper.

POST /api/complete

Marks a chore as completed for a specific user. This is the primary "write" endpoint.

Request Body (JSON):

{
  "chore_name": "Take out Trash",
  "user_name": "billy"
}

Success Response (200 OK):
{
  "message": "Chore 'Take out Trash' marked as complete for user 'billy'.",
  "timestamp": "2025-09-04T10:30:00Z"
}

Error Response (404 Not Found): If the chore or user doesn't exist.
{ "detail": "User 'billy' not found." }
GET /api/status/{user_name}

Retrieves a full status report for a given user. This is the primary "read" endpoint for the HA dashboard.

URL Parameter:
user_name: The name of the user to get a status for.

Success Response (200 OK):
{
  "user_name": "billy",
  "chores_today": [
    {
      "name": "Feed the Dog",
      "completed": true
    },
    {
      "name": "Take out Trash",
      "completed": false
    }
  ],
  "streaks": [
    {
      "chore_name": "Feed the Dog",
      "current_streak": 14
    },
    {
      "chore_name": "Take out Trash",
      "current_streak": 3
    }
  ]
}

Error Response (404 Not Found):
{ "detail": "User 'billy' not found." }
GET /api/admin/chores (Optional, for management)

Lists all defined chores and their schedules.

Success Response (200 OK):
[
  { "name": "Feed the Dog", "schedule": "0,1,2,3,4,5,6" },
  { "name": "Take out Trash", "schedule": "0,3" }
]

6. Core Application Logic

Streak Calculation: The most complex logic. When a streak is requested for a chore, the app will:
Get the chore's schedule (e.g., every Monday and Thursday).
Fetch all of that chore's completion dates for the user, ordered from newest to oldest.
Starting from today, iterate backward through the scheduled dates (e.g., this Monday, last Thursday, last Monday...).
For each scheduled date, check if a completion was logged on that day.
The streak is the count of consecutive scheduled dates that have a completion. The count stops at the first missed scheduled day.

7. Dockerization

The project will include a Dockerfile to build the application image.

Dockerfile Example:

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variables (optional, good practice)
ENV DATABASE_URL=sqlite:///./chorekeeper.db

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
A docker-compose.yml file will be provided for easy one-command startup, including mounting a volume to persist the SQLite database file.

8. Home Assistant Configuration Example

This is how you would configure HA to interact with the running ChoreKeeper container.

rest_command (to mark chores done): in configuration.yaml

rest_command:
  chore_done:
    url: "http://<chorekeeper_ip>/api/complete"
    method: "POST"
    headers:
      content-type: "application/json"
    payload: '{"chore_name": "{{ chore_name }}", "user_name": "{{ user_name }}"}'

rest sensor (to get status): in configuration.yaml

rest:
  - resource: http://<chorekeeper_ip>/api/status/billy
    scan_interval: 60
    sensor:
      - name: "Billy Chore Streak Trash"
        value_template: >
          {{ value_json.streaks | selectattr('chore_name', 'eq', 'Take out Trash') | map(attribute='current_streak') | first }}
      - name: "Billy Chores Pending"
        value_template: >
          {{ value_json.chores_today | rejectattr('completed', 'eq', true) | map(attribute='name') | list | count }}
        json_attributes:
          - chores_today
          - streaks

Lovelace UI: You would then use a button card to call the rest_command.chore_done service with the correct variables and display the sensor values in an entities or custom card.
