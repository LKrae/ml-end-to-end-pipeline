"""
load.py

Postgres loader scaffolding for the SpaceNet7 star schema.

This module provides:
- Database connection helper
- Table creation DDL
- Bulk insert helpers for dim_aoi, dim_chip, dim_time, fact_chip_observation
"""

import psycopg2
import geopandas as gpd
import pandas as pd
from psycopg2.extras import execute_values


# ---------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------

def get_connection(dbname, user, password, host="localhost", port=5432):
    """
    Create a Postgres connection.
    """
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
    )


# ---------------------------------------------------------------------
# Table creation DDL
# ---------------------------------------------------------------------

DDL_DIM_AOI = """
CREATE TABLE IF NOT EXISTS dim_aoi (
    aoi_id TEXT PRIMARY KEY,
    name TEXT,
    geometry GEOMETRY(POLYGON, 32613)
);
"""

DDL_DIM_CHIP = """
CREATE TABLE IF NOT EXISTS dim_chip (
    chip_id TEXT PRIMARY KEY,
    year INT,
    month INT,
    zoom INT,
    tile_x INT,
    tile_y INT,
    utm_x INT,
    utm_y INT,
    utm_zone INT,
    geometry GEOMETRY(POLYGON, 32613),
    centroid GEOMETRY(POINT, 32613)
);
"""

DDL_DIM_TIME = """
CREATE TABLE IF NOT EXISTS dim_time (
    time_id TEXT PRIMARY KEY,
    year INT,
    month INT
);
"""

DDL_FACT_CHIP_OBS = """
CREATE TABLE IF NOT EXISTS fact_chip_observation (
    chip_id TEXT REFERENCES dim_chip(chip_id),
    aoi_id TEXT REFERENCES dim_aoi(aoi_id),
    time_id TEXT REFERENCES dim_time(time_id),
    building_id INT,
    chip_geometry GEOMETRY(POLYGON, 32613),
    centroid_geometry GEOMETRY(POINT, 32613),
    aoi_geometry GEOMETRY(POLYGON, 32613)
);
"""


def create_tables(conn):
    """
    Create all star schema tables.
    """
    with conn.cursor() as cur:
        cur.execute(DDL_DIM_AOI)
        cur.execute(DDL_DIM_CHIP)
        cur.execute(DDL_DIM_TIME)
        cur.execute(DDL_FACT_CHIP_OBS)
    conn.commit()


# ---------------------------------------------------------------------
# Bulk insert helpers
# ---------------------------------------------------------------------

def insert_dim_aoi(conn, dim_aoi: gpd.GeoDataFrame):
    """
    Insert rows into dim_aoi.
    """
    rows = [
        (row.aoi_id, row.name, row.geometry.wkt)
        for _, row in dim_aoi.iterrows()
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO dim_aoi (aoi_id, name, geometry) VALUES %s "
            "ON CONFLICT (aoi_id) DO NOTHING;",
            rows,
        )
    conn.commit()


def insert_dim_chip(conn, dim_chip: gpd.GeoDataFrame):
    """
    Insert rows into dim_chip.
    """
    rows = [
        (
            row.chip_id,
            row.year,
            row.month,
            row.zoom,
            row.tile_x,
            row.tile_y,
            row.utm_x,
            row.utm_y,
            row.utm_zone,
            row.geometry.wkt,
            row.centroid.wkt,
        )
        for _, row in dim_chip.iterrows()
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_chip (
                chip_id, year, month, zoom,
                tile_x, tile_y, utm_x, utm_y, utm_zone,
                geometry, centroid
            ) VALUES %s
            ON CONFLICT (chip_id) DO NOTHING;
            """,
            rows,
        )
    conn.commit()


def insert_dim_time(conn, dim_time: pd.DataFrame):
    """
    Insert rows into dim_time.
    """
    rows = [
        (row.time_id, row.year, row.month)
        for _, row in dim_time.iterrows()
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_time (time_id, year, month)
            VALUES %s
            ON CONFLICT (time_id) DO NOTHING;
            """,
            rows,
        )
    conn.commit()


def insert_fact_chip_observation(conn, fact: gpd.GeoDataFrame):
    """
    Insert rows into fact_chip_observation.
    """
    rows = [
        (
            row.chip_id,
            row.aoi_id,
            row.time_id,
            row.id,                 # building_id
            row.geometry.wkt,       # chip geometry
            row.centroid.wkt,       # chip centroid
            row.aoi_geometry.wkt,   # AOI polygon
        )
        for _, row in fact.iterrows()
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO fact_chip_observation (
                chip_id, aoi_id, time_id, building_id,
                chip_geometry, centroid_geometry, aoi_geometry
            ) VALUES %s;
            """,
            rows,
        )
    conn.commit()
