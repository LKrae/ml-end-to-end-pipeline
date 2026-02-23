from pydantic import BaseModel
from typing import List, Optional


class PredictionRequest(BaseModel):
    chip_id: str
    building_count: float
    prev_building_count: float


class BatchPredictionRequest(BaseModel):
    records: List[PredictionRequest]


class PredictionResponse(BaseModel):
    prediction: float


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
