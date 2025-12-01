# Periodic Table Facts Bot

## Overview
A local Periodic Table Facts Bot with JWT authentication, Neon PostgreSQL database, and AI-generated chemistry facts using OpenRouter API. Users can sign up, log in, search for element information, and chat with an AI assistant about chemistry topics.

## Project Structure
```
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
- **Periodic Table Image**: Ask to "view periodic table" or "show all elements" to get a complete periodic table image
- **Modern UI**: React frontend with responsive design with chemistry-themed backgrounds

## API Endpoints (all prefixed with /api)
- `POST /api/signup` - Create new user account
- `POST /api/login` - Authenticate user
- `GET /api/me` - Get current user info (protected)
- `GET /api/elements` - Get all elements
- `GET /api/elements/{identifier}` - Get element by symbol or name
- `POST /api/ask` - Ask AI a chemistry question (protected); returns periodic table image when asking about all elements
- `GET /{filename}.png` - Serve periodic table and background images

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
Frontend is accessible via the webview. The Vite dev server proxies /api requests to the backend.

## Recent Changes
- November 2024: Initial project setup with authentication system
- Deployed to Render with merged frontend/backend
- Fixed login error handling - shows error messages instead of page refresh
- Added email-validator dependency for email validation
- Replaced modern glassmorphism design with clean, classic UI
- Simplified styling: removed animations, gradients, and fancy effects
- Final design: Professional minimalist interface with blue accents
- November 30, 2025: Enhanced UI/UX:
  - Added chemistry-themed background to login/signup pages
  - Made auth cards 40% transparent for better background visibility
  - Highlighted text with shadows for improved readability
  - Redesigned chat page with gradients, improved spacing, animations
  - Added shadow effects and better visual hierarchy
  - Improved typography and button styling throughout
  - Added slide-in animations for chat messages
  - Enhanced sidebar with gradient background and better styling
- December 1, 2025: Added Periodic Table Feature:
  - Generated and integrated periodic table image
  - Backend detects keywords: "periodic table", "all elements", "view elements", "show table", etc.
  - Fixed static file serving to properly display images in chat
  - Added image display support in Chat component with responsive styling
