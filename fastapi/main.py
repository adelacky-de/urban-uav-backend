import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


GEOJSON_2D_PATH = os.environ.get("GEOJSON_2D_PATH", "/data/2D_safe_corridors_prioritized.geojson")
GEOJSON_3D_PATH = os.environ.get("GEOJSON_3D_PATH", "/data/3D_merged_network.geojson")
GEOJSON_HDB_PATH = os.environ.get("GEOJSON_HDB_PATH", "/data/hdb_footprints.geojson")
TILES_DIR = os.environ.get("TILES_DIR", "/data/tiles")


# In-memory cache for the data to avoid reading from disk on every request
geojson_cache = {
    "2d": None,
    "3d": None,
    "hdb": None
}

def load_geojson(path):
    # Adjust path if running locally vs in docker
    if not os.path.exists(path):
        local_path = os.path.basename(path)
        if os.path.exists(local_path):
            path = local_path
            
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {"type": "FeatureCollection", "features": []}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load files into memory on startup
    geojson_cache["2d"] = load_geojson(GEOJSON_2D_PATH)
    geojson_cache["3d"] = load_geojson(GEOJSON_3D_PATH)
    geojson_cache["hdb"] = load_geojson(GEOJSON_HDB_PATH)
    yield


app = FastAPI(title="Corridors API", lifespan=lifespan)

# CORS for local frontend dev and dynamic Vercel production preview URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins so Vercel dynamic preview URLs don't get blocked
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "static_file_serving"}


@app.get("/2d-corridors")
def corridors_2d(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    # Bounding box parameters are ignored. Returning entire dataset.
    return JSONResponse(content=geojson_cache["2d"])


@app.get("/3d-network")
def network_3d(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    # Bounding box parameters are ignored. Returning entire dataset.
    return JSONResponse(content=geojson_cache["3d"])


@app.get("/hdb-footprints")
def hdb_footprints(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    # Bounding box parameters are ignored. Returning entire dataset.
    return JSONResponse(content=geojson_cache["hdb"])


# Static 3D Tiles: Cesium uses base URL e.g. http://localhost:8000/3dtiles/tileset.json
if os.path.isdir(TILES_DIR):
    app.mount("/3dtiles", StaticFiles(directory=TILES_DIR, html=False), name="3dtiles")
