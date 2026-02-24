import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://uavuser:uavpass@localhost:5432/uavdb")
GEOJSON_2D_PATH = os.environ.get("GEOJSON_2D_PATH", "/data/2D_safe_corridors_prioritized.geojson")
GEOJSON_3D_PATH = os.environ.get("GEOJSON_3D_PATH", "/data/3D_merged_network.geojson")
GEOJSON_HDB_PATH = os.environ.get("GEOJSON_HDB_PATH", "/data/hdb_footprints.geojson")
TILES_DIR = os.environ.get("TILES_DIR", "/data/tiles")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from import_data import run_import
    try:
        run_import(DATABASE_URL, GEOJSON_2D_PATH, GEOJSON_3D_PATH, GEOJSON_HDB_PATH)
    except Exception as e:
        print(f"Startup import warning: {e}")
    yield
    # no shutdown needed


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
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        db = "ok"
    except Exception as e:
        db = str(e)
    return {"status": "ok", "database": db}


def get_2d_corridors_geojson(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, "OBJECTID", "PLN_AREA_N", "PLN_AREA_C", "CA_IND", "REGION_N", "REGION_C",
                    "INC_CRC", "FMEL_UPD_D", "SHAPE.AREA", "SHAPE.LEN", "Total_Population",
                    "Total_Males", "Total_Females", "LabourForce_Total_Total", "LabourForce_Total_Males",
                    "LabourForce_Total_Females", "LabourForce_Employed_Total", "LabourForce_Employed_Males",
                    "LabourForce_Employed_Females", "LabourForce_Unemployed_Total", "LabourForce_Unemployed_Males",
                    "LabourForce_Unemployed_Females", "OutsidetheLabourForce_Total", "OutsidetheLabourForce_Males",
                    "OutsidetheLabourForce_Females", "Area_km2", "Pop_Density", "priorityID",
                    ST_AsGeoJSON(geom)::json AS geom
                FROM corridors_2d_4326
            """
            params = []
            if min_lon is not None and min_lat is not None and max_lon is not None and max_lat is not None:
                query += " WHERE ST_Intersects(geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326))"
                params.extend([min_lon, min_lat, max_lon, max_lat])
            query += " ORDER BY id"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
    features = []
    for r in rows:
        geom = r.pop("geom", None)
        r.pop("id", None)
        if geom is None:
            continue
        features.append({
            "type": "Feature",
            "properties": dict(r),
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}


def get_3d_network_geojson(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, min_altitude, corridor_type, max_altitude, volume_m3, "priorityID",
                    ST_AsGeoJSON(geom)::json AS geom
                FROM network_3d_4326
            """
            params = []
            if min_lon is not None and min_lat is not None and max_lon is not None and max_lat is not None:
                query += " WHERE ST_Intersects(geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326))"
                params.extend([min_lon, min_lat, max_lon, max_lat])
            query += " ORDER BY id"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
    features = []
    for r in rows:
        geom = r.pop("geom", None)
        r.pop("id", None)
        if geom is None:
            continue
        features.append({
            "type": "Feature",
            "properties": dict(r),
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/2d-corridors")
def corridors_2d(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    return JSONResponse(content=get_2d_corridors_geojson(min_lon, min_lat, max_lon, max_lat))


@app.get("/3d-network")
def network_3d(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    return JSONResponse(content=get_3d_network_geojson(min_lon, min_lat, max_lon, max_lat))


def get_hdb_footprints_geojson(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, feat_id, height, levels,
                    ST_AsGeoJSON(geom)::json AS geom
                FROM hdb_footprints_4326
            """
            params = []
            if min_lon is not None and min_lat is not None and max_lon is not None and max_lat is not None:
                query += " WHERE ST_Intersects(geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326))"
                params.extend([min_lon, min_lat, max_lon, max_lat])
            query += " ORDER BY id"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
    features = []
    for r in rows:
        geom = r.pop("geom", None)
        r.pop("id", None)
        if geom is None:
            continue
        features.append({
            "type": "Feature",
            "properties": dict(r),
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/hdb-footprints")
def hdb_footprints(min_lon: float = None, min_lat: float = None, max_lon: float = None, max_lat: float = None):
    return JSONResponse(content=get_hdb_footprints_geojson(min_lon, min_lat, max_lon, max_lat))


# Static 3D Tiles: Cesium uses base URL e.g. http://localhost:8000/3dtiles/tileset.json
if os.path.isdir(TILES_DIR):
    app.mount("/3dtiles", StaticFiles(directory=TILES_DIR, html=False), name="3dtiles")
