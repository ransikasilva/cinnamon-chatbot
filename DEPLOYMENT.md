# Cinnamon Hotels Chatbot - Deployment Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git
- Google Maps API Key

## Environment Setup

### Frontend (.env.local)
Create `frontend/.env.local`:
```
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## Deployment Options

### Option 1: Vercel (Frontend) + Railway/Render (Backend)

#### Frontend (Vercel)
1. Push code to GitHub (without .env.local)
2. Go to vercel.com and import your repository
3. Set Framework Preset: **Next.js**
4. Root Directory: `frontend`
5. Add Environment Variable:
   - Key: `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`
   - Value: Your Google Maps API key
6. Deploy

#### Backend (Railway/Render)
1. Create new Python app on Railway or Render
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py` or `gunicorn app:app`
5. Update CORS in `backend/app.py` to allow your Vercel domain
6. Update frontend API base URL to backend URL

### Option 2: Docker (Full Stack)

Create `docker-compose.yml` in root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=${NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}
    depends_on:
      - backend
```

Deploy with: `docker-compose up -d`

### Option 3: Single Server (VPS)

1. SSH into your server
2. Clone repository
3. Install dependencies
4. Setup environment variables
5. Run with PM2:
```bash
# Backend
cd backend
pip install -r requirements.txt
pm2 start app.py --name chatbot-backend

# Frontend
cd frontend
npm install
npm run build
pm2 start npm --name chatbot-frontend -- start
```

## Important Security Steps

1. ✅ API key moved to environment variable
2. ✅ `.env.local` added to `.gitignore`
3. ⚠️ Update CORS settings in production
4. ⚠️ Restrict Google Maps API key to your domain
5. ⚠️ Enable rate limiting on backend

## Post-Deployment

1. Test all three user flows
2. Verify Google Maps loads correctly
3. Check booking form submissions
4. Test hotel carousel navigation

## Demo Accounts
- New Booking: newbooking@demo.com
- Explorer: explorer@demo.com
- Edit Booking: editbooking@demo.com
