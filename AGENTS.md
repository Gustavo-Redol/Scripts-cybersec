# Base44 Setup Notes

## What this repo is
A collection of CLI security/recon tools (bash, python, c) with **no native web app**. A minimal FastAPI dashboard (`webapp/`) was added to serve a read-only overview on port 3000.

## Running
- `docker compose -f docker-compose.base44.yml up -d`
- Single service `web` on python:3.12-slim, repo bind-mounted at `/app`, uvicorn `--reload` on port 3000.
- Deps (fastapi, uvicorn) are installed on container startup from the command — no requirements file.

## Verify
- `curl http://localhost:3000/api/health` → `{"status":"ok"}`
- `curl http://localhost:3000/api/tools` → JSON list of tools

## Quirks
- Tool descriptions are a hardcoded dict in `webapp/main.py` (`TOOLS`); the API enriches each entry with on-disk existence/size.
- No external secrets required for the dashboard to boot.
