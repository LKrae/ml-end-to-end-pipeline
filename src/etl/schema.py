"""
schema.py

Defines the star schema tables for SpaceNet7 metadata.
"""

import pandas as pd
import geopandas as gpd


def build_dim_aoi(aoi_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build dim_aoi from AOI polygons.
    """
    dim = aoi_gdf.copy()
    dim["aoi_id"] = dim["aoi_id"].astype(str)
    dim["name"] = dim["aoi_id"]  # simple mapping for now
    return dim[["aoi_id", "name", "geometry"]]


def build_dim_chip(metadata_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build dim_chip from parsed metadata.
    """
    cols = [
        "chip_id", "year", "month", "zoom",
        "tile_x", "tile_y", "utm_x", "utm_y", "utm_zone",
        "geometry", "centroid"
    ]
    return metadata_gdf[cols].drop_duplicates("chip_id")


def build_dim_time(metadata_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Build dim_time from year/month combinations.
    """
    df = metadata_gdf[["year", "month"]].drop_duplicates()
    df["time_id"] = df["year"].astype(str) + "_" + df["month"].astype(str).str.zfill(2)
    return df[["time_id", "year", "month"]]


def build_fact_chip_observation(metadata_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build fact table linking chip, AOI, time, and building observations.
    Pixel-level geometry is not yet available, so it is excluded.
    """
    df = metadata_gdf.copy()

    # Build time_id
    df["time_id"] = df["year"].astype(str) + "_" + df["month"].astype(str).str.zfill(2)

    # Select available fields
    return df[
        [
            "chip_id",
            "aoi_id",
            "time_id",
            "id",          # building_id from pixel CSV
            "geometry",    # chip geometry
            "centroid",    # chip centroid
            "aoi_geometry" # AOI polygon
        ]
    ]
