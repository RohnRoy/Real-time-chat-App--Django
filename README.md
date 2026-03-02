# Real-Time Individual Chat Application (Django + Channels)

## Overview

This project is a real-time individual chat application built using Django with the MVT architecture and Django Channels for WebSocket communication. It allows authenticated users to register, log in, view other users, and exchange private messages in real time. The system also supports online status tracking, last seen information, unread message counts, and read receipts.

The application uses SQLite as the database and standard HTML, CSS, and JavaScript for the frontend.

---

## Features

### Authentication
- User registration with email and password
- Login and logout functionality
- Custom user model using email as the username field
- Only authenticated users can access chat features
- Unauthenticated users are redirected to the login page

### User List
- Displays all users except the currently logged-in user
- Shows online/offline status
- Displays last seen timestamp when offline
- Shows unread message count per user
- Real-time updates for presence and unread messages

### Real-Time Private Chat
- One-to-one chat between users
- WebSocket-based communication using Django Channels
- Messages are saved in the database
- Previous chat history is loaded on opening a conversation
- Automatic scrolling to the latest message

### Message Status
- Read receipts for sent messages
- Sent messages show a single tick when delivered
- Messages show double ticks when read
- Read status updates in real time

### Presence Tracking
- Online status is updated when a user connects
- Last seen timestamp is recorded when a user disconnects
- Presence updates propagate in real time to all connected users

### Validations
- Prevents sending empty messages
- Only authenticated users can establish WebSocket connections
- Prevents users from chatting with themselves
- Validates existence of target user before establishing chat

---

## Technology Stack

- Python
- Django (MVT architecture)
- Django Channels
- SQLite
- HTML, CSS, JavaScript
- Optional Bootstrap styling

---

## Project Structure

```text
chat_project/
├── accounts/       # Authentication app
├── chat/           # Chat logic and WebSocket consumers
├── chat_project/   # Project settings and configuration
├── templates/      # HTML templates
├── db.sqlite3      # SQLite database
├── manage.py
├── README.md
└── .gitignore
```

---

## Installation Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd chat_project
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install django channels daphne
```

---

## Database Setup

Apply migrations to create database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

Open the application in a browser:

```text
http://127.0.0.1:8000/
```

---

## Usage

1. Register a new user account.
2. Log in using your credentials.
3. The user list page will display all other registered users.
4. Click on any user to start a private chat.
5. Messages are delivered instantly in real time.
6. Read receipts and presence information update automatically.

To test real-time behavior, open the application in multiple browser windows or different browsers and log in with different users.

---

## WebSocket Endpoints

- Private chat: `/ws/chat/<user_id>/`
- User presence updates: `/ws/users/`

---

## Security Considerations

- WebSocket connections require authenticated users.
- Anonymous users are denied access to chat endpoints.
- Input validation prevents empty messages.
- Users cannot initiate chat sessions with themselves.

---

## Notes

- The default branch is develop and production branch is used for deployment

---
