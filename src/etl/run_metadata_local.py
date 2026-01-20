"""
run_metadata_local.py

Local test runner for the SpaceNet7 metadata ETL pipeline.
This version does NOT require an AOI GeoJSON file.
It generates AOI polygons directly from chip geometries.
"""

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from etl.metadata import build_sn7_metadata
from etl.build_aoi_polygons import build_aoi_polygons
from etl.schema import (
    build_dim_aoi,
    build_dim_chip,
    build_dim_time,
    build_fact_chip_observation,
)
from etl.load import (
    get_connection,
    create_tables,
    insert_dim_aoi,
    insert_dim_chip,
    insert_dim_time,
    insert_fact_chip_observation,
)

# ---------------------------------------------------------
# 1. File paths (UPDATE THESE)
# ---------------------------------------------------------

# IMPORTANT:
# Replace these with the actual paths on your machine.
pixel_csv = r"C:/Users/kraem/OneDrive/[04] Data Science/[02] Learning/[04] Datasets/spacenet/SN7_csvs/sn7_train_ground_truth_pix.csv"

# We no longer need an AOI GeoJSON file.
# AOI polygons will be generated automatically.

# ---------------------------------------------------------
# 2. Build metadata (chip geometries + parsed filenames)
# ---------------------------------------------------------

print("Running metadata ETL...")
metadata = build_sn7_metadata(pixel_csv_path=pixel_csv, aoi_geojson_path=None)
print(f"Metadata records: {len(metadata)}")

# ---------------------------------------------------------
# 3. Generate AOI polygons from chip geometries
# ---------------------------------------------------------

print("Generating AOI polygons from chip geometries...")
aoi_gdf = build_aoi_polygons(metadata)
print(f"AOIs generated: {len(aoi_gdf)}")

# ---------------------------------------------------------
# 4. Build star schema tables
# ---------------------------------------------------------

print("Building star schema tables...")

dim_aoi = build_dim_aoi(aoi_gdf)
dim_chip = build_dim_chip(metadata)
dim_time = build_dim_time(metadata)
fact = build_fact_chip_observation(metadata)

print("Dimensions built:")
print(f"  AOIs: {len(dim_aoi)}")
print(f"  Chips: {len(dim_chip)}")
print(f"  Time: {len(dim_time)}")
print(f"  Fact rows: {len(fact)}")

# ---------------------------------------------------------
# 5. Load into Postgres
# ---------------------------------------------------------

db_config = {
    "dbname": "sn7",
    "user": "postgres",
    "password": "admin",  # <-- UPDATE THIS
    "host": "localhost",
    "port": 5432,
}

print("Connecting to Postgres...")
conn = get_connection(**db_config)

print("Creating tables (if not exist)...")
create_tables(conn)

print("Loading dimensions...")
insert_dim_aoi(conn, dim_aoi)
insert_dim_chip(conn, dim_chip)
insert_dim_time(conn, dim_time)

print("Loading fact table...")
insert_fact_chip_observation(conn, fact)

conn.close()

print("ETL complete and loaded into Postgres.")
