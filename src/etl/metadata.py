"""
metadata.py

High‑level orchestration for the SpaceNet7 metadata ETL pipeline.

This module ties together:
- Pixel CSV ingestion
- Filename parsing
- Chip geometry computation
- AOI polygon loading (optional)
- Chip → AOI spatial join

The output is a clean metadata GeoDataFrame ready for loading into
dimension and fact tables.
"""

import pandas as pd
import geopandas as gpd

from etl.ingest import (
    load_sn7_pixel_csv,
    load_aoi_polygons,
    build_raw_chip_records,
)

from etl.transform import (
    build_chip_geometries,
    join_chips_to_aois,
)


# ---------------------------------------------------------------------
# Main metadata ETL function
# ---------------------------------------------------------------------

def build_sn7_metadata(
    pixel_csv_path: str,
    aoi_geojson_path: str,
) -> gpd.GeoDataFrame:
    """
    Build the complete SpaceNet7 metadata table.
    """

    # ---------------------------------------------------------
    # 1. Load pixel-level CSV
    # ---------------------------------------------------------
    print("Step 1: Loading pixel CSV...")
    df = load_sn7_pixel_csv(pixel_csv_path)
    print("✓ Pixel CSV loaded")

    # ---------------------------------------------------------
    # 2. Parse filenames → structured metadata
    # ---------------------------------------------------------
    print("Step 2: Parsing filenames into structured metadata...")
    df = build_raw_chip_records(df)
    print("✓ Filename parsing complete")

    # ---------------------------------------------------------
    # 3. Compute chip bounding boxes + centroids
    # ---------------------------------------------------------
    print("Step 3: Building chip geometries (bounding boxes + centroids)...")
    chip_gdf = build_chip_geometries(df)
    print("✓ Chip geometries built")

    # ---------------------------------------------------------
    # 4. Load AOI polygons (optional)
    # ---------------------------------------------------------
    if aoi_geojson_path is not None:
        print("Step 4: Loading AOI polygons from file...")
        aoi_gdf = load_aoi_polygons(aoi_geojson_path)
        print("✓ AOI polygons loaded")
    else:
        print("Step 4: No AOI file provided — generating AOI polygons from chip geometries...")
        from etl.build_aoi_polygons import build_aoi_polygons
        aoi_gdf = build_aoi_polygons(chip_gdf)
        print("✓ AOI polygons generated")


    # ---------------------------------------------------------
    # 5. Spatial join: chip centroids → AOIs
    # ---------------------------------------------------------
    print("Step 5: Assigning chips to AOIs via spatial join...")
    chip_with_aoi = join_chips_to_aois(chip_gdf, aoi_gdf)
    print("✓ Chip → AOI assignment complete")

    return chip_with_aoi


# ---------------------------------------------------------------------
# Convenience wrapper for notebooks / Prefect flows
# ---------------------------------------------------------------------

def run_metadata_pipeline(pixel_csv_path: str, aoi_geojson_path: str):
    """
    Convenience wrapper that prints progress and returns the final metadata.
    """

    print("Starting SpaceNet7 metadata ETL pipeline...")
    metadata = build_sn7_metadata(pixel_csv_path, aoi_geojson_path)
    print("✓ Metadata ETL complete")
    print(f"Total chip records: {len(metadata):,}")

    return metadata
