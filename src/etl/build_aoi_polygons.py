"""
build_aoi_polygons.py

Generate AOI polygons by unioning chip geometries for each AOI.
This reconstructs the AOI boundaries directly from the dataset.
"""

import geopandas as gpd
from shapely.ops import unary_union


def build_aoi_polygons(metadata_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build AOI polygons by taking the convex hull of chip centroids for each AOI.
    This avoids sliver polygons and produces clean AOI boundaries.
    """
    print("Constructing AOI polygons from chip centroids...")

    # Ensure centroids exist
    if "centroid" not in metadata_gdf.columns:
        metadata_gdf["centroid"] = metadata_gdf.geometry.centroid

    # Group by AOI and compute convex hull of centroids
    aoi_polygons = (
        metadata_gdf
        .groupby("aoi_id")["centroid"]
        .apply(lambda pts: pts.unary_union.convex_hull)
        .reset_index()
        .rename(columns={"centroid": "geometry"})
    )

    # Convert to GeoDataFrame
    aoi_gdf = gpd.GeoDataFrame(aoi_polygons, geometry="geometry", crs=metadata_gdf.crs)

    # Optional: add readable name
    aoi_gdf["name"] = aoi_gdf["aoi_id"]

    print(f"✓ Built {len(aoi_gdf)} AOI polygons")

    return aoi_gdf
