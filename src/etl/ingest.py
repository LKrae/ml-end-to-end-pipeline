import os
from pathlib import Path

from prefect import flow, task
import rasterio
import geopandas as gpd


# ---------------------------------------------------------
# DATA PATHS — pulled from your OneDrive environment variable
# ---------------------------------------------------------

DATA_DIR = Path(os.environ["SPACENET_DATA_DIR"])

IMAGERY_DIR = DATA_DIR / "imagery"
LABELS_DIR = DATA_DIR / "labels"
METADATA_DIR = DATA_DIR / "metadata"


# ---------------------------------------------------------
# INGEST TASKS
# ---------------------------------------------------------

@task
def load_raster(path: Path):
    """Load a single raster (GeoTIFF) file into memory."""
    with rasterio.open(path) as src:
        array = src.read()          # numpy array
        profile = src.profile       # metadata
    return {"array": array, "profile": profile}


@task
def load_vector(path: Path):
    """Load a vector file (GeoJSON, Shapefile) into a GeoDataFrame."""
    gdf = gpd.read_file(path)
    return gdf


@task
def list_imagery():
    """Return a list of all raster files in the imagery directory."""
    return sorted(IMAGERY_DIR.rglob("*.tif"))


@task
def list_labels():
    """Return a list of all vector label files."""
    return sorted(LABELS_DIR.rglob("*.geojson"))


# ---------------------------------------------------------
# MAIN INGEST FLOW
# ---------------------------------------------------------

@flow
def ingest_spacenet():
    """
    A simple Prefect flow that:
    - lists imagery + labels
    - loads the first raster + first label file
    - returns them for downstream processing
    """

    imagery_files = list_imagery()
    label_files = list_labels()

    if not imagery_files:
        raise FileNotFoundError(f"No imagery found in {IMAGERY_DIR}")

    if not label_files:
        raise FileNotFoundError(f"No labels found in {LABELS_DIR}")

    # Load the first raster + vector file as a test
    raster_data = load_raster(imagery_files[0])
    vector_data = load_vector(label_files[0])

    return {
        "raster": raster_data,
        "vector": vector_data,
        "raster_path": imagery_files[0],
        "vector_path": label_files[0],
    }


# ---------------------------------------------------------
# SCRIPT ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    results = ingest_spacenet()
    print("Loaded raster:", results["raster_path"])
    print("Loaded vector:", results["vector_path"])
