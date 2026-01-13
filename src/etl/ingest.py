"""
ingest.py

Ingestion utilities for the SpaceNet7 dataset:
- Load pixel-level ground truth CSV
- Parse chip filenames into structured metadata
- Load AOI polygons
"""

import os
import pandas as pd
import geopandas as gpd
from dataclasses import asdict

from shapely.geometry import Point

# -----------------------------
# Filename parsing
# -----------------------------
import re
from dataclasses import dataclass


@dataclass
class ParsedFilename:
    mosaic: str
    year: int
    month: int
    chip_id: str
    zoom: int
    tile_x: int
    tile_y: int
    utm_x: int
    utm_y: int
    utm_zone: int


def parse_sn7_filename(filename: str) -> ParsedFilename:
    """
    Parse a SpaceNet7 filename into structured metadata.

    Example:
        global_monthly_2018_01_mosaic_L15-0331E-1257N_1327_3160_13
    """
    mosaic, chip = filename.split("_mosaic_")

    # Extract year/month
    m = re.search(r"(\d{4})_(\d{2})", mosaic)
    year, month = int(m.group(1)), int(m.group(2))

    # Parse chip ID
    chip_core = chip.replace("L", "")
    zoom_str, rest = chip_core.split("-", 1)
    zoom = int(zoom_str)

    tile_e, tile_n, utm_x, utm_y, utm_zone = re.split("[-_]", rest)

    tile_x = int(tile_e[:-1])  # remove trailing 'E'
    tile_y = int(tile_n[:-1])  # remove trailing 'N'

    return ParsedFilename(
        mosaic=mosaic,
        year=year,
        month=month,
        chip_id=chip,
        zoom=zoom,
        tile_x=tile_x,
        tile_y=tile_y,
        utm_x=int(utm_x),
        utm_y=int(utm_y),
        utm_zone=int(utm_zone),
    )


# -----------------------------
# AOI loader
# -----------------------------

def load_aoi_polygons(aoi_path: str, utm_zone: int = 13) -> gpd.GeoDataFrame:
    """
    Load AOI polygons and reproject to UTM.
    """
    gdf = gpd.read_file(aoi_path)
    gdf = gdf.to_crs(f"EPSG:326{utm_zone}")
    return gdf


# -----------------------------
# Pixel-level CSV loader
# -----------------------------

def load_sn7_pixel_csv(csv_path: str) -> pd.DataFrame:
    """
    Load the SpaceNet7 pixel-level ground truth CSV.
    """
    df = pd.read_csv(csv_path)
    return df


# -----------------------------
# Build raw chip metadata records
# -----------------------------

def build_raw_chip_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse filenames and attach structured metadata fields.
    """
    parsed = df["filename"].apply(parse_sn7_filename)
    parsed_df = pd.DataFrame([asdict(p) for p in parsed])
    return pd.concat([df, parsed_df], axis=1)
