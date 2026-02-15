# PostGIS + FastAPI – Safe Corridors & 3D Tiles

Backend for serving **2D safe corridors** (GeoJSON), **3D merged network** (GeoJSON), and **3D Tiles** from PostGIS and static files via a minimal FastAPI API. Two containers: **PostGIS** and **FastAPI**. Data is imported automatically on first run.

## Quick start

1. Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed.

2. Open Docker Desktop.

3. In this directory (`postgisWithFastAPI`), run:

   **First time:**
   ```bash
   docker compose up -d --build
   ```

   **If you already ran the old version on your pc** (single corridor layer), replace it with the new setup:
   ```bash
   docker compose down -v
   docker compose up -d --build
   ```
   (`down -v` removes the database volume so the new schema and data are loaded from scratch.)

4. Wait for PostGIS to be ready and FastAPI to run the first-time import.

5. Check the endpoints:
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8000/2d-corridors`
   - `curl http://localhost:8000/3d-network`
   - 3D Tiles: `http://localhost:8000/3dtiles/tileset.json` (use in Cesium as the tileset base URL).

## Layout

- **postgis/** – PostGIS container: init scripts and [README](postgis/README.md) (DB params, volumes, tables).
- **fastapi/** – FastAPI app: import logic, API, [README](fastapi/README.md) (endpoints and setup).
- **docker-compose.yml** – Defines `postgis` and `fastapi` services; FastAPI depends on PostGIS health.
- **2D_safe_corridors_prioritized.geojson** – 2D source data (EPSG:3414); imported into PostGIS on first startup.
- **3D_merged_network.geojson** – 3D network source (EPSG:3414); imported into PostGIS on first startup.
- **tiles/** – 3D Tiles folder (tileset.json + tile files); served statically at `/3dtiles/`.

## Subfolders

- [postgis/README.md](postgis/README.md) – How the PostGIS container and init scripts work.
- [fastapi/README.md](fastapi/README.md) – How to run the API and use the four endpoints.
