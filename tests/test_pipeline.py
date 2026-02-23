import pandas as pd
from ml_end_to_end_pipeline.models.pipeline import build_pipeline

def test_pipeline_builds():
    """Ensure the pipeline builds and can run a forward pass."""
    pipeline = build_pipeline()
    assert pipeline is not None

    # Minimal synthetic input matching your feature schema
    df = pd.DataFrame({
        "chip_id": ["chip_001"],
        "time_id": ["T1"],
        "building_count": [10],
        "prev_building_count": [8],
        "delta_count": [2],  # target, but pipeline should ignore during transform
    })

    # Fit on synthetic data (fast, offline)
    pipeline.fit(df, df["delta_count"])

    # Run a forward pass
    pred = pipeline.predict(df)

    # Validate output shape and type
    assert len(pred) == 1
    assert isinstance(pred[0], (float, int))

