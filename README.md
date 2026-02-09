# PostGIS + FastAPI – Safe Corridors

Backend for serving **safe corridors** (GeoJSON) from PostGIS via a minimal FastAPI API. Two containers: **PostGIS** and **FastAPI**. One command to start; data is imported automatically on first run.

## Quick start

1. Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed.

2. open docker desktop

3. In this directory (`postgisWithFastAPI`), run:

   ```bash
   docker compose up -d
   ```

4. Wait for PostGIS to be ready and FastAPI to run the first-time import.
5. Check health and corridors:
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8000/corridors`

The **GET /corridors** response is a GeoJSON `FeatureCollection` (EPSG:4326) with all attribute columns; you can use it directly in a frontend map.

## Layout

- **postgis/** – PostGIS container: init scripts and [README](postgis/README.md) (DB params, volumes, tables).
- **fastapi/** – FastAPI app: import logic, API, [README](fastapi/README.md) (endpoints and setup).
- **docker-compose.yml** – Defines `postgis` and `fastapi` services; FastAPI depends on PostGIS health.
- **safe_corridors_prioritized.geojson** – Source data (EPSG:3414); mounted into the FastAPI container and imported into PostGIS on first startup.

## Subfolders

- [postgis/README.md](postgis/README.md) – How the PostGIS container and init scripts work.
- [fastapi/README.md](fastapi/README.md) – How to run the API and use `/health` and `/corridors`.
