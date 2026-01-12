import os
from pathlib import Path
from typing import Dict, List, Any

import rasterio
import geopandas as gpd
from prefect import task

# ---------------------------------------------------------------------
# Environment variable: SPACENET_DATA_DIR
# ---------------------------------------------------------------------
DATA_DIR = Path(os.environ["SPACENET_DATA_DIR"])
TILES_DIR = DATA_DIR / "tiles"   # e.g., spacenet/tiles/L15-xxxx/

# ---------------------------------------------------------------------
# Utility: detect tile folders
# ---------------------------------------------------------------------
def list_tile_folders() -> List[Path]:
    return [p for p in TILES_DIR.iterdir() if p.is_dir()]

# ---------------------------------------------------------------------
# Load imagery (multi-temporal)
# ---------------------------------------------------------------------
@task
def load_imagery(tile_path: Path) -> Dict[str, Any]:
    images_dir = tile_path / "images"
    if not images_dir.exists():
        raise FileNotFoundError(f"No imagery folder found in {tile_path}")

    imagery_files = sorted(images_dir.glob("*.tif"))
    imagery_stack = {}

    for tif in imagery_files:
        with rasterio.open(tif) as src:
            imagery_stack[tif.stem] = {
                "array": src.read(),
                "meta": src.meta
            }

    return {
        "tile_id": tile_path.name,
        "imagery": imagery_stack
    }

# ---------------------------------------------------------------------
# Load labels (vector)
# ---------------------------------------------------------------------
@task
def load_labels(tile_path: Path) -> Dict[str, Any]:
    labels_dir = tile_path / "labels"
    if not labels_dir.exists():
        raise FileNotFoundError(f"No labels folder found in {tile_path}")

    label_files = sorted(labels_dir.glob("*.geojson")) + sorted(labels_dir.glob("*.json"))
    labels = {}

    for lf in label_files:
        gdf = gpd.read_file(lf)
        labels[lf.stem] = gdf

    return {
        "tile_id": tile_path.name,
        "labels": labels
    }

# ---------------------------------------------------------------------
# Load matched labels (optional)
# ---------------------------------------------------------------------
@task
def load_matched_labels(tile_path: Path) -> Dict[str, Any]:
    match_dir = tile_path / "labels_match"
    if not match_dir.exists():
        return {"tile_id": tile_path.name, "labels_match": {}}

    match_files = sorted(match_dir.glob("*.geojson")) + sorted(match_dir.glob("*.json"))
    matched = {}

    for mf in match_files:
        gdf = gpd.read_file(mf)
        matched[mf.stem] = gdf

    return {
        "tile_id": tile_path.name,
        "labels_match": matched
    }

# ---------------------------------------------------------------------
# Master ingest task for a single tile
# ---------------------------------------------------------------------
@task
def ingest_tile(tile_path: Path) -> Dict[str, Any]:
    imagery = load_imagery(tile_path)
    labels = load_labels(tile_path)
    matched = load_matched_labels(tile_path)

    return {
        "tile_id": tile_path.name,
        "imagery": imagery["imagery"],
        "labels": labels["labels"],
        "labels_match": matched["labels_match"]
    }

# ---------------------------------------------------------------------
# Pipeline entrypoint
# ---------------------------------------------------------------------
@task
def ingest_all_tiles() -> List[Dict[str, Any]]:
    tile_paths = list_tile_folders()
    results = []

    for tile in tile_paths:
        results.append(ingest_tile(tile))

    return results
