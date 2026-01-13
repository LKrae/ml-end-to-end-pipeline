"""
transform.py

Transformation utilities for SpaceNet7:
- Compute chip bounding boxes
- Convert tile indices to lon/lat and UTM
- Compute centroids
- Spatially join chips to AOIs
"""

import math
import geopandas as gpd
from shapely.geometry import box

from ingest import ParsedFilename


# -----------------------------
# Tile → lon/lat conversion
# -----------------------------

def tile_to_lonlat_bounds(x: int, y: int, z: int):
    """
    Convert Web Mercator tile indices to lon/lat bounding box.
    """
    n = 2 ** z

    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0

    lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))

    return lon_left, lat_bottom, lon_right, lat_top


# -----------------------------
# Lon/lat → UTM conversion
# -----------------------------

import pyproj

def lonlat_to_utm_bounds(lon_left, lat_bottom, lon_right, lat_top, zone):
    """
    Convert lon/lat bounding box to UTM bounding box.
    """
    proj = pyproj.Transformer.from_crs("EPSG:4326", f"EPSG:326{zone}", always_xy=True)
    x1, y1 = proj.transform(lon_left, lat_bottom)
    x2, y2 = proj.transform(lon_right, lat_top)
    return box(x1, y1, x2, y2)


# -----------------------------
# Compute chip geometry
# -----------------------------

def compute_chip_geometry(parsed: ParsedFilename):
    """
    Compute the UTM bounding box for a parsed SpaceNet7 chip.
    """
    lon_left, lat_bottom, lon_right, lat_top = tile_to_lonlat_bounds(
        parsed.utm_x, parsed.utm_y, parsed.zoom
    )
    return lonlat_to_utm_bounds(lon_left, lat_bottom, lon_right, lat_top, parsed.utm_zone)


# -----------------------------
# Build GeoDataFrame of chip centroids
# -----------------------------

def build_chip_geometries(df):
    """
    Add bounding boxes and centroids to chip metadata.
    """
    geoms = df.apply(
        lambda row: compute_chip_geometry(
            ParsedFilename(
                mosaic=row["mosaic"],
                year=row["year"],
                month=row["month"],
                chip_id=row["chip_id"],
                zoom=row["zoom"],
                tile_x=row["tile_x"],
                tile_y=row["tile_y"],
                utm_x=row["utm_x"],
                utm_y=row["utm_y"],
                utm_zone=row["utm_zone"],
            )
        ),
        axis=1,
    )

    gdf = gpd.GeoDataFrame(df, geometry=geoms, crs="EPSG:32613")
    gdf["centroid"] = gdf.geometry.centroid
    return gdf


# -----------------------------
# Spatial join: chips → AOIs
# -----------------------------

def join_chips_to_aois(chip_gdf: gpd.GeoDataFrame, aoi_gdf: gpd.GeoDataFrame):
    """
    Assign each chip to an AOI by spatial join.
    """
    centroids = chip_gdf.copy()
    centroids = centroids.set_geometry("centroid")
    return centroids.sjoin(aoi_gdf, how="left", predicate="within")
