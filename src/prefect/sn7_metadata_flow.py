"""
sn7_metadata_flow.py

Prefect flow for the SpaceNet7 metadata ETL pipeline.
"""

from prefect import flow, task
from etl.metadata import build_sn7_metadata
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


@task
def extract_metadata(pixel_csv_path: str, aoi_geojson_path: str):
    return build_sn7_metadata(pixel_csv_path, aoi_geojson_path)


@task
def build_dimensions(metadata):
    dim_aoi = build_dim_aoi(metadata)
    dim_chip = build_dim_chip(metadata)
    dim_time = build_dim_time(metadata)
    fact = build_fact_chip_observation(metadata)
    return dim_aoi, dim_chip, dim_time, fact


@task
def load_to_postgres(dim_aoi, dim_chip, dim_time, fact, db_config):
    conn = get_connection(**db_config)
    create_tables(conn)

    insert_dim_aoi(conn, dim_aoi)
    insert_dim_chip(conn, dim_chip)
    insert_dim_time(conn, dim_time)
    insert_fact_chip_observation(conn, fact)

    conn.close()


@flow(name="sn7_metadata_pipeline")
def sn7_metadata_pipeline(pixel_csv_path: str, aoi_geojson_path: str, db_config: dict):
    metadata = extract_metadata(pixel_csv_path, aoi_geojson_path)
    dim_aoi, dim_chip, dim_time, fact = build_dimensions(metadata)
    load_to_postgres(dim_aoi, dim_chip, dim_time, fact, db_config)
