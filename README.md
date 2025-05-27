# Campaign Manager

This repository contains a Flask backend and React frontend.

## Development Setup

1. Build and start services with Docker Compose:
   ```bash
   docker-compose up --build
   ```
2. Backend runs on `http://localhost:5000` with automatic reload.
3. Frontend runs on `http://localhost:3000` and reloads on file changes.

The database tables are created automatically on startup via `scripts/init_db.py`.
