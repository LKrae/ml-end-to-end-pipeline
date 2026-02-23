import numpy as np
from ml_end_to_end_pipeline.models.predict import load_model, run_single_inference

def test_model_loads():
    """Ensure the trained model loads correctly."""
    model = load_model()
    assert model is not None

def test_single_inference_runs():
    """Ensure single-record inference returns a numeric prediction."""
    model = load_model()
    pred = run_single_inference(
        model,
        chip_id="A123",
        building_count=50,
        prev_building_count=45
    )

    # Accept numpy scalar or Python float
    assert isinstance(pred, (float, np.floating))
