# Deploy to Render (Merged Backend + Frontend)

## Quick Setup

### Step 1: Build the Frontend
Before deploying, build the React app:
```bash
cd frontend
npm install
npm run build
cd ..
```

This creates `frontend/dist/` with all static files.

### Step 2: Deploy to Render

1. Go to [render.com](https://render.com) and log in
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Fill in these details:
   - **Name**: `periodic-table-bot` (or any name)
   - **Environment**: Select **python3**
   - **Build Command**: 
     ```
     bash build.sh
     ```
   - **Start Command**: 
     ```
     cd backend && python main.py
     ```
   - **Port**: `8000` (or leave blank - Render will detect it)

5. Click **Create Web Service**

### Step 3: Add Environment Variables

In Render's dashboard, go to your service's **Environment** tab and add:

- `DATABASE_URL` = Your PostgreSQL connection string
- `SESSION_SECRET` = Copy from Replit Secrets (click the Secrets lock icon in Replit)
- `OPENROUTER_API_KEY` = Copy from Replit Secrets

Done! Your app will be live at `https://<your-app-name>.onrender.com`

## How It Works

- **Backend**: FastAPI on port 8000
- **Frontend**: React built to static files, served by FastAPI
- **Single Service**: Everything runs together
- **API Routes**: `/api/*` routes handled by FastAPI backend
- **Static Routes**: All other routes served by React app

## Local Testing

Before deploying, test locally:

```bash
# Build frontend
cd frontend
npm run build

# Start backend (serves built frontend)
cd ../backend
python main.py
```

Visit `http://localhost:8000` - you should see your app!
