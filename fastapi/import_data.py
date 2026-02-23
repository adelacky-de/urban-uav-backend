"""
Idempotent import: load 2D and 3D GeoJSON into PostGIS (EPSG:3414), then
populate _4326 tables via ST_Transform. Skips each table if it already has data.
"""
import json
import time
from pathlib import Path

import psycopg2

# 2D corridors: attribute columns (no id, no geom)
ATTR_COLS_2D = [
    "OBJECTID", "PLN_AREA_N", "PLN_AREA_C", "CA_IND", "REGION_N", "REGION_C",
    "INC_CRC", "FMEL_UPD_D", "SHAPE.AREA", "SHAPE.LEN", "Total_Population",
    "Total_Males", "Total_Females", "LabourForce_Total_Total", "LabourForce_Total_Males",
    "LabourForce_Total_Females", "LabourForce_Employed_Total", "LabourForce_Employed_Males",
    "LabourForce_Employed_Females", "LabourForce_Unemployed_Total", "LabourForce_Unemployed_Males",
    "LabourForce_Unemployed_Females", "OutsidetheLabourForce_Total", "OutsidetheLabourForce_Males",
    "OutsidetheLabourForce_Females", "Area_km2", "Pop_Density", "priorityID",
]

# 3D network: attribute columns (no id, no geom)
ATTR_COLS_3D = ["min_altitude", "corridor_type", "max_altitude", "volume_m3", "priorityID"]


def wait_db(conninfo: str, timeout_sec: float = 60, interval_sec: float = 2) -> None:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            with psycopg2.connect(conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return
        except Exception:
            time.sleep(interval_sec)
    raise RuntimeError("Database did not become ready in time")


def has_data(conn, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {table} LIMIT 1")
        return cur.fetchone() is not None


def load_and_import_2d(conn, geojson_path: str) -> None:
    path = Path(geojson_path)
    if not path.is_file():
        raise FileNotFoundError(f"GeoJSON not found: {geojson_path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features") or []
    if not features:
        return

    col_list = ", ".join(f'"{c}"' for c in ATTR_COLS_2D)
    placeholders = ", ".join(["%s"] * len(ATTR_COLS_2D)) + ", ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON(%s)), 3414)"
    insert_sql = f'INSERT INTO corridors_2d ({col_list}, geom) VALUES ({placeholders})'

    with conn.cursor() as cur:
        for f in features:
            props = f.get("properties") or {}
            geom_str = json.dumps(f.get("geometry"))
            row = [props.get(c) for c in ATTR_COLS_2D] + [geom_str]
            cur.execute(insert_sql, row)
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO corridors_2d_4326 (
                "OBJECTID", "PLN_AREA_N", "PLN_AREA_C", "CA_IND", "REGION_N", "REGION_C",
                "INC_CRC", "FMEL_UPD_D", "SHAPE.AREA", "SHAPE.LEN", "Total_Population",
                "Total_Males", "Total_Females", "LabourForce_Total_Total", "LabourForce_Total_Males",
                "LabourForce_Total_Females", "LabourForce_Employed_Total", "LabourForce_Employed_Males",
                "LabourForce_Employed_Females", "LabourForce_Unemployed_Total", "LabourForce_Unemployed_Males",
                "LabourForce_Unemployed_Females", "OutsidetheLabourForce_Total", "OutsidetheLabourForce_Males",
                "OutsidetheLabourForce_Females", "Area_km2", "Pop_Density", "priorityID", geom
            )
            SELECT
                "OBJECTID", "PLN_AREA_N", "PLN_AREA_C", "CA_IND", "REGION_N", "REGION_C",
                "INC_CRC", "FMEL_UPD_D", "SHAPE.AREA", "SHAPE.LEN", "Total_Population",
                "Total_Males", "Total_Females", "LabourForce_Total_Total", "LabourForce_Total_Males",
                "LabourForce_Total_Females", "LabourForce_Employed_Total", "LabourForce_Employed_Males",
                "LabourForce_Employed_Females", "LabourForce_Unemployed_Total", "LabourForce_Unemployed_Males",
                "LabourForce_Unemployed_Females", "OutsidetheLabourForce_Total", "OutsidetheLabourForce_Males",
                "OutsidetheLabourForce_Females", "Area_km2", "Pop_Density", "priorityID",
                ST_Transform(geom, 4326)
            FROM corridors_2d
        """)
    conn.commit()


def load_and_import_3d(conn, geojson_path: str) -> None:
    path = Path(geojson_path)
    if not path.is_file():
        raise FileNotFoundError(f"GeoJSON not found: {geojson_path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features") or []
    if not features:
        return

    col_list = ", ".join(f'"{c}"' for c in ATTR_COLS_3D)
    placeholders = ", ".join(["%s"] * len(ATTR_COLS_3D)) + ", ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON(%s)), 3414)"
    insert_sql = f'INSERT INTO network_3d ({col_list}, geom) VALUES ({placeholders})'

    with conn.cursor() as cur:
        for f in features:
            props = f.get("properties") or {}
            geom_str = json.dumps(f.get("geometry"))
            row = [props.get(c) for c in ATTR_COLS_3D] + [geom_str]
            cur.execute(insert_sql, row)
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO network_3d_4326 (
                min_altitude, corridor_type, max_altitude, volume_m3, "priorityID", geom
            )
            SELECT
                min_altitude, corridor_type, max_altitude, volume_m3, "priorityID",
                ST_Transform(geom, 4326)
            FROM network_3d
        """)
    conn.commit()


def run_import(database_url: str, geojson_2d_path: str, geojson_3d_path: str, geojson_hdb_path: str = "") -> None:
    wait_db(database_url)
    with psycopg2.connect(database_url) as conn:
        if not has_data(conn, "corridors_2d"):
            load_and_import_2d(conn, geojson_2d_path)
        if not has_data(conn, "network_3d"):
            load_and_import_3d(conn, geojson_3d_path)
        if geojson_hdb_path and not has_data(conn, "hdb_footprints"):
            load_and_import_hdb(conn, geojson_hdb_path)


def load_and_import_hdb(conn, geojson_path: str) -> None:
    path = Path(geojson_path)
    if not path.is_file():
        raise FileNotFoundError(f"HDB GeoJSON not found: {geojson_path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features") or []
    if not features:
        return

    insert_sql = (
        "INSERT INTO hdb_footprints (feat_id, height, levels, geom) VALUES "
        "(%s, %s, %s, ST_SetSRID(ST_Multi(ST_GeomFromGeoJSON(%s)), 3414))"
    )

    with conn.cursor() as cur:
        for feat in features:
            props = feat.get("properties") or {}
            geom_str = json.dumps(feat.get("geometry"))
            cur.execute(insert_sql, [
                str(props.get("id", "")),
                props.get("height"),
                str(props.get("osm_building:levels", "")),
                geom_str,
            ])
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO hdb_footprints_4326 (feat_id, height, levels, geom)
            SELECT feat_id, height, levels, ST_Transform(geom, 4326)
            FROM hdb_footprints
        """)
    conn.commit()
