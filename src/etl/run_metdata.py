"""
run_metadata.py

Command-line entry point for the SpaceNet7 metadata ETL pipeline.
"""

import argparse
from prefect import flow
from prefect.deployments import run_deployment

def main():
    parser = argparse.ArgumentParser(description="Run SN7 metadata ETL pipeline")
    parser.add_argument("--pixel_csv", required=True)
    parser.add_argument("--aoi_geojson", required=True)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=5432)

    args = parser.parse_args()

    db_config = {
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
        "host": args.host,
        "port": args.port,
    }

    run_deployment(
        name="sn7_metadata_pipeline",
        parameters={
            "pixel_csv_path": args.pixel_csv,
            "aoi_geojson_path": args.aoi_geojson,
            "db_config": db_config,
        },
    )


if __name__ == "__main__":
    main()
