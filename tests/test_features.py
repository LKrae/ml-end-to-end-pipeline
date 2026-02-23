import pandas as pd
from unittest.mock import patch, MagicMock
from ml_end_to_end_pipeline.models.features import load_feature_table

def test_feature_table_columns():
    """Ensure load_feature_table returns the correct cleaned schema."""

    # Synthetic row matching the SQL output BEFORE cleanup
    fake_rows = [{
        "chip_id": "chip_001",
        "time_id": "T1",
        "year": 2020,
        "month": 5,
        "aoi_id": "AOI_1",
        "centroid": "POINT(0 0)",
        "geometry": "POLYGON((...))",
        "building_count": 10,
        "prev_building_count": None,
        "delta_count": None,
    }]

    # Mock the DB connection + cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = fake_rows
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("ml_end_to_end_pipeline.models.features.get_db_connection", return_value=mock_conn):
        df = load_feature_table()

    # Columns that should remain after cleanup
    expected = {
        "chip_id",
        "time_id",
        "building_count",
        "prev_building_count",
        "delta_count",
    }

    assert expected.issubset(df.columns)
    assert "year" not in df.columns
    assert "month" not in df.columns
    assert "aoi_id" not in df.columns
    assert "geometry" not in df.columns
    assert "centroid" not in df.columns
