# Periodic Table Facts Bot

## Overview
A local Periodic Table Facts Bot with JWT authentication, Neon PostgreSQL database, and AI-generated chemistry facts using OpenRouter API. Users can sign up, log in, search for element information, and chat with an AI assistant about chemistry topics.

## Project Structure
```
periodic-facts-bot/
├── backend/
│   ├── main.py          # FastAPI backend with all endpoints
│   └── elements.json    # Complete periodic table data (118 elements)
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── api.js   # API client with axios
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   └── Chat.jsx
│   │   ├── App.jsx
│   │   └── App.css
│   └── vite.config.js
└── replit.md
```

## Features
- **User Authentication**: Email-based signup/login with JWT tokens
- **Secure Passwords**: Password hashing using pbkdf2_sha256
- **Element Lookup**: Search any element by symbol or name
- **AI Chat**: Ask chemistry questions powered by OpenRouter API
- **Modern UI**: React frontend with responsive design

## API Endpoints
- `POST /signup` - Create new user account
- `POST /login` - Authenticate user
- `GET /me` - Get current user info (protected)
- `GET /elements` - Get all elements
- `GET /elements/{identifier}` - Get element by symbol or name
- `POST /ask` - Ask AI a chemistry question (protected)

## Environment Variables Required
- `DATABASE_URL` - PostgreSQL connection string (automatically set)
- `SESSION_SECRET` - JWT secret key (automatically set)
- `OPENROUTER_API_KEY` - OpenRouter API key for AI chat

## Tech Stack
- **Backend**: FastAPI, PyJWT, passlib, psycopg2, httpx
- **Frontend**: React, Vite, React Router, Axios
- **Database**: PostgreSQL (Neon)
- **AI**: OpenRouter API

## Running the Application
The application runs both backend (port 8000) and frontend (port 5000) together.
Frontend is accessible via the webview.

## Recent Changes
- Initial project setup (November 2024)
- Created FastAPI backend with authentication
- Added periodic table data for all 118 elements
- Built React frontend with Login, Signup, and Chat pages
- Integrated OpenRouter API for AI-powered chemistry facts
