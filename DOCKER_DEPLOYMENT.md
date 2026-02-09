# Docker Deployment Guide for S2HI

This guide will help you containerize and deploy the S2HI application using Docker.

## Prerequisites

- Docker Desktop installed and running
- Git Bash or PowerShell

## Project Structure

```
S2HI/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── nginx.conf
└── docker-compose.yml
```

## Quick Start

### 1. Environment Setup

Make sure your `backend/.env` file contains:
```env
GEMINI_API_KEY=your_api_key_here
```

### 2. Build and Run with Docker Compose

From the `S2HI` root directory:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Backend Admin**: http://localhost:8000/admin

### 4. Stop the Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes (WARNING: This will delete your database)
docker-compose down -v
```

## Testing in Docker Desktop

1. Open Docker Desktop
2. Navigate to the "Containers" tab
3. You should see:
   - `s2hi-backend` (running on port 8000)
   - `s2hi-frontend` (running on port 80)
4. Click on each container to view logs and status

## Individual Container Commands

### Backend Only

```bash
# Build backend image
cd backend
docker build -t s2hi-backend .

# Run backend container
docker run -p 8000:8000 --env-file .env s2hi-backend
```

### Frontend Only

```bash
# Build frontend image
cd frontend
docker build -t s2hi-frontend .

# Run frontend container
docker run -p 80:80 s2hi-frontend
```

## Deployment to Home Server

### Option 1: Using Docker Compose (Recommended)

1. Copy the entire `S2HI` directory to your home server
2. Ensure Docker and Docker Compose are installed on the server
3. Update the `.env` file with production values
4. Run: `docker-compose up -d`

### Option 2: Using Docker Images

1. **Build and save images locally:**
   ```bash
   docker save s2hi-backend:latest | gzip > s2hi-backend.tar.gz
   docker save s2hi-frontend:latest | gzip > s2hi-frontend.tar.gz
   ```

2. **Transfer to server:**
   ```bash
   scp s2hi-*.tar.gz user@your-server:/path/to/destination
   ```

3. **Load on server:**
   ```bash
   docker load < s2hi-backend.tar.gz
   docker load < s2hi-frontend.tar.gz
   ```

4. **Run on server:**
   ```bash
   docker-compose up -d
   ```

### Option 3: Using Docker Registry

1. **Tag images:**
   ```bash
   docker tag s2hi-backend:latest your-registry/s2hi-backend:latest
   docker tag s2hi-frontend:latest your-registry/s2hi-frontend:latest
   ```

2. **Push to registry:**
   ```bash
   docker push your-registry/s2hi-backend:latest
   docker push your-registry/s2hi-frontend:latest
   ```

3. **Pull on server:**
   ```bash
   docker pull your-registry/s2hi-backend:latest
   docker pull your-registry/s2hi-frontend:latest
   ```

## Production Considerations

### 1. Update Backend Settings

Edit `backend/ld_screening/settings.py`:
- Set `DEBUG = False`
- Update `ALLOWED_HOSTS` with your domain
- Update `CORS_ALLOWED_ORIGINS` with your frontend URL
- Consider using PostgreSQL or MySQL instead of SQLite

### 2. Use Environment Variables

Create a production `.env` file:
```env
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
GEMINI_API_KEY=your_api_key_here
```

### 3. Enable HTTPS

Use a reverse proxy like Nginx or Traefik with Let's Encrypt for SSL certificates.

### 4. Data Persistence

The `docker-compose.yml` already includes volume mounts for:
- Database: `./backend/db.sqlite3`
- Media files: `./backend/media`

These will persist even if containers are recreated.

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing .env file
# - Database migration errors
# - Port 8000 already in use
```

### Frontend not loading
```bash
# Check logs
docker-compose logs frontend

# Common issues:
# - Build errors (check Node.js version)
# - Nginx configuration errors
# - Port 80 already in use (use different port in docker-compose.yml)
```

### Database issues
```bash
# Run migrations manually
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## Useful Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python manage.py shell

# Rebuild specific service
docker-compose up -d --build backend

# Remove all containers and images
docker-compose down --rmi all
```

## Health Checks

Check if services are running:
```bash
# Backend health
curl http://localhost:8000/api/

# Frontend
curl http://localhost
```

## Next Steps

1. Test locally using Docker Desktop
2. Verify all features work correctly
3. Update production settings
4. Deploy to your home server
5. Set up monitoring and backups
