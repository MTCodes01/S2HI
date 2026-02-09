# Docker Quick Start Guide

## Testing in Docker Desktop (Local)

### 1. Make sure Docker Desktop is running

### 2. Build and start containers
```bash
cd d:\Github\S2HI
docker-compose up --build
```

### 3. Access the application
- Frontend: http://localhost:3002
- Backend: http://localhost:3001

### 4. Stop containers
```bash
docker-compose down
```

## What was created:

### Backend (Django)
- `backend/Dockerfile` - Container configuration
- `backend/.dockerignore` - Files to exclude from image

### Frontend (React + Vite)
- `frontend/Dockerfile` - Multi-stage build with Nginx
- `frontend/.dockerignore` - Files to exclude from image
- `frontend/nginx.conf` - Web server configuration
- `frontend/.env.example` - Environment template

### Orchestration
- `docker-compose.yml` - Runs both services together
- `DOCKER_DEPLOYMENT.md` - Complete deployment guide

## Next Steps for Home Server Deployment

See `DOCKER_DEPLOYMENT.md` for detailed instructions on:
- Transferring images to your server
- Production configuration
- HTTPS setup
- Database persistence
- Troubleshooting

## Important Notes

1. **Environment Variables**: Copy `backend/.env.example` to `backend/.env` and add your `GEMINI_API_KEY`
2. **Database**: SQLite database and media files are persisted via Docker volumes
3. **Ports**: Frontend runs on port 3002, backend on port 3001 (avoids conflicts with common services)
4. **API Configuration**: Frontend automatically connects to backend via environment variable
