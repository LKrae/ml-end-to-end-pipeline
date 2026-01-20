from prefect import flow, task
from etl.metadata import build_sn7_metadata
from etl.load import (
    get_connection,
    create_tables,
    insert_dim_aoi,
    insert_dim_chip,
    insert_dim_time,
    insert_fact_chip_observation,
)

@task
def extract_metadata(pixel_csv_path):
    return build_sn7_metadata(pixel_csv_path=pixel_csv_path, aoi_geojson_path=None)

@task
def load_to_postgres(metadata, dbname, user, password):
    conn = get_connection(dbname, user, password)
    create_tables(conn)

    insert_dim_aoi(conn, metadata["dim_aoi"])
    insert_dim_chip(conn, metadata["dim_chip"])
    insert_dim_time(conn, metadata["dim_time"])
    insert_fact_chip_observation(conn, metadata["fact"])

    conn.close()

@flow
def metadata_etl_flow(pixel_csv_path, dbname, user, password):
    metadata = extract_metadata(pixel_csv_path)
    load_to_postgres(metadata, dbname, user, password)
