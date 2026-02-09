# Port Configuration Reference

## Updated Ports (To Avoid Conflicts)

Your server already has services running on ports 80 and 8000, so the S2HI application uses:

- **Frontend**: Port **3002** (instead of 80)
- **Backend**: Port **3001** (instead of 8000)

## Quick Access URLs

### Local Testing (Docker Desktop)
- Frontend: http://localhost:3002
- Backend API: http://localhost:3001
- Backend Admin: http://localhost:3001/admin

### Home Server Access
Replace `localhost` with your server IP:
- Frontend: http://YOUR_SERVER_IP:3002
- Backend API: http://YOUR_SERVER_IP:3001

## Environment Configuration

Make sure to create `frontend/.env` with:
```env
VITE_API_BASE_URL=http://localhost:3001
```

For production on your server, update to:
```env
VITE_API_BASE_URL=http://YOUR_SERVER_IP:3001
```

## Existing Containers on Your Server

Based on your `docker ps` output:
- Port 80: Used by `hvh` container (fortis-app)
- Port 8000: Likely used by Portainer
- Port 9000: Portainer UI
- Port 3294: reelo_reelo
- Port 5174: fortis-app

S2HI ports (3001, 3002) don't conflict with any of these! ✅

## Changing Ports (If Needed)

Edit `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "YOUR_PORT:8000"  # Change YOUR_PORT
  
  frontend:
    ports:
      - "YOUR_PORT:80"    # Change YOUR_PORT
```

Then update `frontend/.env` to match the backend port.
