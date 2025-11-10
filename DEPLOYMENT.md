# AI4SIDS Deployment Guide

## Architecture

- **Frontend**: React + TanStack Router + Vite → Deployed on Netlify
- **Backend**: FastAPI + SQLite → Deploy on Railway/Render/Fly.io

## Frontend Deployment (Netlify)

### Netlify Build Settings:

- **Branch to deploy**: `demo-1` (or `ash-demo-1`)
- **Base directory**: `frontend`
- **Build command**: `pnpm install && pnpm build`
- **Publish directory**: `frontend/dist`
- **Functions directory**: (leave empty)

### Environment Variables (Set in Netlify UI):

```
VITE_API_URL=https://your-backend-url.railway.app
```

### Steps:

1. Push code to GitHub
2. Connect repo to Netlify
3. Use settings above
4. Add environment variable after backend is deployed
5. Deploy!

## Backend Deployment (Railway - Recommended)

### Railway Setup:

1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select your `ai4sids` repo
4. **Root Directory**: `api`
5. **Start Command**: `fastapi run app`

### Environment Variables (Set in Railway):

```
DATABASE_URL=sqlite:///./ai4sids_demo.db
CORS_ORIGINS=https://your-netlify-app.netlify.app
```

### Alternative: Render.com

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `api`

## Local Development

### Frontend:

```bash
cd frontend
pnpm install
pnpm dev
# Runs on http://localhost:3000
```

### Backend:

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
fastapi dev app
# Runs on http://localhost:8000
```

## After Deployment

1. Update CORS in backend to allow your Netlify domain
2. Set `VITE_API_URL` in Netlify to point to your backend
3. Test the live site!

## Troubleshooting

### Frontend can't connect to backend:

- Check `VITE_API_URL` is set in Netlify
- Verify backend CORS includes Netlify domain
- Check backend is running and accessible

### Build fails on Netlify:

- Ensure Node version is 20 (set in netlify.toml)
- Check all dependencies are in package.json
- Review build logs for errors
