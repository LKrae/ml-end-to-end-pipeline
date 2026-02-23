import pytest
import pandas as pd
from ml_end_to_end_pipeline.models.predict import load_model

@pytest.fixture(scope="session")
def synthetic_row():
    """Single synthetic feature row matching the cleaned feature schema."""
    return {
        "chip_id": "chip_001",
        "time_id": "T1",
        "building_count": 10,
        "prev_building_count": 8,
        "delta_count": 2,
    }

@pytest.fixture(scope="session")
def synthetic_df(synthetic_row):
    """Small DataFrame for pipeline and inference tests."""
    return pd.DataFrame([synthetic_row])

@pytest.fixture(scope="session")
def trained_model():
    """Load the trained model once per test session."""
    return load_model()


import pytest
from fastapi.testclient import TestClient
from ml_end_to_end_pipeline.api.app import app

@pytest.fixture(scope="session")
def api_client():
    """FastAPI test client for API endpoint tests."""
    return TestClient(app)

@pytest.fixture(scope="session")
def single_payload():
    """Payload for /predict endpoint."""
    return {
        "chip_id": "chip_001",
        "building_count": 10,
        "prev_building_count": 8
    }

@pytest.fixture(scope="session")
def batch_payload():
    """Payload for /predict/batch endpoint."""
    return {
        "records": [
            {
                "chip_id": "chip_001",
                "building_count": 10,
                "prev_building_count": 8
            },
            {
                "chip_id": "chip_002",
                "building_count": 20,
                "prev_building_count": 18
            }
        ]
    }
