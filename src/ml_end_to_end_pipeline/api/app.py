from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import logging
import time
import joblib
import os
import pandas as pd

from ml_end_to_end_pipeline.version import __version__
from ml_end_to_end_pipeline.models.predict import (
    run_single_inference,
    run_batch_inference
)

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Load model once at startup
# ---------------------------------------------------------
MODEL_PATH = "models/best_regression_model.joblib"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------
app = FastAPI(title="Building Growth Prediction API")


# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class PredictionRequest(BaseModel):
    chip_id: str
    building_count: float
    prev_building_count: float


class BatchPredictionRequest(BaseModel):
    records: List[PredictionRequest]


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# Single Prediction Endpoint
# ---------------------------------------------------------
@app.post("/predict")
def predict(request: PredictionRequest):
    start = time.time()

    logger.info(f"Received single prediction request for chip {request.chip_id}")

    # Convert to DataFrame for your existing inference function
    df = pd.DataFrame([{
        "chip_id": request.chip_id,
        "building_count": request.building_count,
        "prev_building_count": request.prev_building_count
    }])

    pred = model.predict(df)[0]

    latency = round((time.time() - start) * 1000, 2)
    logger.info(
        f"Single prediction completed in {latency} ms | model_version={__version__}"
    )

    return {"delta_count_pred": float(pred)}


# ---------------------------------------------------------
# Batch Prediction Endpoint
# ---------------------------------------------------------
@app.post("/predict/batch")
def predict_batch(request: BatchPredictionRequest):
    start = time.time()
    num_records = len(request.records)

    logger.info(f"Received batch prediction request with {num_records} records")

    df = pd.DataFrame([{
        "chip_id": r.chip_id,
        "building_count": r.building_count,
        "prev_building_count": r.prev_building_count
    } for r in request.records])

    preds = model.predict(df).tolist()

    latency = round((time.time() - start) * 1000, 2)
    logger.info(
        f"Batch prediction completed in {latency} ms | "
        f"records={num_records} | model_version={__version__}"
    )

    return {"predictions": preds}
