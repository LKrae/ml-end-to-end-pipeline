"""
test_sn7_metadata.py

Unit tests for SpaceNet7 ingestion and transformation.
"""

from etl.ingest import parse_sn7_filename
from etl.transform import compute_chip_geometry
from shapely.geometry import Polygon


def test_parse_sn7_filename():
    fn = "global_monthly_2018_01_mosaic_L15-0331E-1257N_1327_3160_13"
    parsed = parse_sn7_filename(fn)

    assert parsed.year == 2018
    assert parsed.month == 1
    assert parsed.zoom == 15
    assert parsed.tile_x == 331
    assert parsed.tile_y == 1257
    assert parsed.utm_x == 1327
    assert parsed.utm_y == 3160
    assert parsed.utm_zone == 13


def test_compute_chip_geometry():
    from etl.ingest import ParsedFilename

    parsed = ParsedFilename(
        mosaic="global_monthly_2018_01",
        year=2018,
        month=1,
        chip_id="L15-0331E-1257N_1327_3160_13",
        zoom=15,
        tile_x=331,
        tile_y=1257,
        utm_x=1327,
        utm_y=3160,
        utm_zone=13,
    )

    geom = compute_chip_geometry(parsed)
    assert isinstance(geom, Polygon)
