from fastapi import FastAPI
from ml_end_to_end_pipeline.models.predict import load_model
from ml_end_to_end_pipeline.api.schemas import (
    PredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    BatchPredictionResponse,
)
import pandas as pd

app = FastAPI(title="Building Growth Prediction API")

# Load model once at startup
model = load_model()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict_single(request: PredictionRequest):
    df = pd.DataFrame([request.dict()])
    pred = model.predict(df)[0]
    return PredictionResponse(delta_count_pred=float(pred))


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest):
    df = pd.DataFrame([r.dict() for r in request.records])
    preds = model.predict(df)
    responses = [PredictionResponse(delta_count_pred=float(p)) for p in preds]
    return BatchPredictionResponse(predictions=responses)
