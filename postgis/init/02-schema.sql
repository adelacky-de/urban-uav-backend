-- corridors_2d: 2D safe corridors, original CRS EPSG:3414
CREATE TABLE IF NOT EXISTS corridors_2d (
  id SERIAL PRIMARY KEY,
  "OBJECTID" integer,
  "PLN_AREA_N" text,
  "PLN_AREA_C" text,
  "CA_IND" text,
  "REGION_N" text,
  "REGION_C" text,
  "INC_CRC" text,
  "FMEL_UPD_D" text,
  "SHAPE.AREA" double precision,
  "SHAPE.LEN" double precision,
  "Total_Population" double precision,
  "Total_Males" double precision,
  "Total_Females" double precision,
  "LabourForce_Total_Total" double precision,
  "LabourForce_Total_Males" double precision,
  "LabourForce_Total_Females" double precision,
  "LabourForce_Employed_Total" double precision,
  "LabourForce_Employed_Males" double precision,
  "LabourForce_Employed_Females" double precision,
  "LabourForce_Unemployed_Total" double precision,
  "LabourForce_Unemployed_Males" double precision,
  "LabourForce_Unemployed_Females" double precision,
  "OutsidetheLabourForce_Total" double precision,
  "OutsidetheLabourForce_Males" double precision,
  "OutsidetheLabourForce_Females" double precision,
  "Area_km2" double precision,
  "Pop_Density" double precision,
  "priorityID" integer,
  geom geometry(MultiPolygon, 3414)
);

CREATE INDEX IF NOT EXISTS idx_corridors_2d_geom ON corridors_2d USING GIST (geom);

-- corridors_2d_4326: transformed to EPSG:4326 for API/frontend
CREATE TABLE IF NOT EXISTS corridors_2d_4326 (
  id SERIAL PRIMARY KEY,
  "OBJECTID" integer,
  "PLN_AREA_N" text,
  "PLN_AREA_C" text,
  "CA_IND" text,
  "REGION_N" text,
  "REGION_C" text,
  "INC_CRC" text,
  "FMEL_UPD_D" text,
  "SHAPE.AREA" double precision,
  "SHAPE.LEN" double precision,
  "Total_Population" double precision,
  "Total_Males" double precision,
  "Total_Females" double precision,
  "LabourForce_Total_Total" double precision,
  "LabourForce_Total_Males" double precision,
  "LabourForce_Total_Females" double precision,
  "LabourForce_Employed_Total" double precision,
  "LabourForce_Employed_Males" double precision,
  "LabourForce_Employed_Females" double precision,
  "LabourForce_Unemployed_Total" double precision,
  "LabourForce_Unemployed_Males" double precision,
  "LabourForce_Unemployed_Females" double precision,
  "OutsidetheLabourForce_Total" double precision,
  "OutsidetheLabourForce_Males" double precision,
  "OutsidetheLabourForce_Females" double precision,
  "Area_km2" double precision,
  "Pop_Density" double precision,
  "priorityID" integer,
  geom geometry(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_corridors_2d_4326_geom ON corridors_2d_4326 USING GIST (geom);

-- network_3d: 3D merged network, original CRS EPSG:3414
CREATE TABLE IF NOT EXISTS network_3d (
  id SERIAL PRIMARY KEY,
  min_altitude double precision,
  corridor_type text,
  max_altitude double precision,
  volume_m3 double precision,
  "priorityID" integer,
  geom geometry(MultiPolygon, 3414)
);

CREATE INDEX IF NOT EXISTS idx_network_3d_geom ON network_3d USING GIST (geom);

-- network_3d_4326: transformed to EPSG:4326 for API/frontend
CREATE TABLE IF NOT EXISTS network_3d_4326 (
  id SERIAL PRIMARY KEY,
  min_altitude double precision,
  corridor_type text,
  max_altitude double precision,
  volume_m3 double precision,
  "priorityID" integer,
  geom geometry(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_network_3d_4326_geom ON network_3d_4326 USING GIST (geom);

-- hdb_footprints: building footprints, original CRS EPSG:3414
CREATE TABLE IF NOT EXISTS hdb_footprints (
  id SERIAL PRIMARY KEY,
  feat_id text,
  height double precision,
  levels text,
  geom geometry(MultiPolygon, 3414)
);

CREATE INDEX IF NOT EXISTS idx_hdb_footprints_geom ON hdb_footprints USING GIST (geom);

-- hdb_footprints_4326: transformed to EPSG:4326 for API/frontend
CREATE TABLE IF NOT EXISTS hdb_footprints_4326 (
  id SERIAL PRIMARY KEY,
  feat_id text,
  height double precision,
  levels text,
  geom geometry(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_hdb_footprints_4326_geom ON hdb_footprints_4326 USING GIST (geom);
