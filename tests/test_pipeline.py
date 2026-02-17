from ml_end_to_end_pipeline.models.pipeline import build_pipeline

def test_pipeline_builds():
    """Ensure the pipeline object is created without errors."""
    pipeline = build_pipeline()
    assert pipeline is not None
