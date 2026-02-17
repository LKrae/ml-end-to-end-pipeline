from ml_end_to_end_pipeline.models.features import load_feature_table

def test_feature_table_columns():
    """Ensure the feature table contains required columns."""
    df = load_feature_table()
    required = {"chip_id", "building_count", "prev_building_count", "delta_count"}
    assert required.issubset(df.columns)
