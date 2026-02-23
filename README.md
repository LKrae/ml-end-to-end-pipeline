# SpaceNet7 End‑to‑End Geospatial ML Pipeline  
A production‑style system for geospatial ETL, temporal feature engineering, leakage‑aware modeling, packaged inference, FastAPI deployment, testing, and CI.

---

## Overview

This repository implements a complete machine learning engineering workflow using the SpaceNet7 multi‑temporal satellite imagery dataset. The system is designed to mirror real‑world ML engineering practices: modular ETL, reproducible feature engineering, leakage‑aware modeling, packaged inference, API deployment, containerization, and automated testing. The project processes 6.6M+ pixel‑level building observations, reconstructs spatial and temporal metadata, builds a star schema in Postgres/PostGIS, engineers chip‑level temporal features, trains a regression model to predict monthly building growth, and exposes the model through a FastAPI service with both single and batch prediction endpoints.

---

## System Architecture

### ETL (Weeks 1–2)

The ETL pipeline reconstructs all spatial and temporal metadata from raw SpaceNet7 filenames and pixel‑level building labels.

Key capabilities:
- Parse filename‑encoded metadata (chip ID, AOI, year, month, UTM coordinates)
- Reconstruct chip geometries (bounding boxes + centroids)
- Build AOI polygons from chip centroids
- Assign chips to AOIs via spatial join
- Load a star schema into Postgres/PostGIS:
  - `dim_chip`
  - `dim_aoi`
  - `dim_time`
  - `fact_chip_observation`
- Orchestrate with Prefect for reproducibility

Dataset summary:
- 6,664,652 building observations  
- 60 chips across 30 AOIs  
- Multiple time periods  
- Fully validated ETL into Postgres

---

## ML Pipeline (Weeks 3–4)

The model predicts chip‑level monthly building growth:



\[
\Delta_t = \text{building\_count}_t - \text{building\_count}_{t-1}
\]



Each row represents a chip at a specific month with:
- `building_count`
- `prev_building_count`
- `delta_count` (target)

### Feature Engineering

Defined in `models/features.py`.

Features include:
- `chip_id` (categorical)
- `building_count`
- `prev_building_count`
- `delta_count`

To prevent leakage, the pipeline drops:
- `year`, `month`
- `aoi_id`
- `geometry`, `centroid`

### Temporal Splitting

Implemented in `models/split.py`.

- Train: earliest months  
- Validation: middle months  
- Test: most recent months  

This preserves causal structure and prevents future‑to‑past leakage.

### Modeling Pipeline

Defined in `models/pipeline.py`.

- Numeric scaling  
- One‑hot encoding for categorical features  
- `RandomForestRegressor`  
- Hyperparameter tuning via `GridSearchCV`  
- Evaluation via MAE, RMSE, R²  
- Best model saved to `models/best_regression_model.joblib`

---

## Inference & FastAPI Service (Weeks 5–6)

The inference layer loads the trained model once at startup and exposes two endpoints.

Start the API:

```bash
uvicorn ml_end_to_end_pipeline.api.app:app --reload
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service status |
| `POST` | `/predict` | Single prediction |
| `POST` | `/predict/batch` | Batch prediction |

Swagger UI:  
`http://localhost:8000/docs`

### Example: Single Prediction

Input:
```json
{
  "chip_id": "chip_001",
  "building_count": 10,
  "prev_building_count": 8
}
```

### Example: Batch Prediction
```json
{
  "records": [
    {"chip_id": "chip_001", "building_count": 10, "prev_building_count": 8},
    {"chip_id": "chip_002", "building_count": 20, "prev_building_count": 18}
  ]
}
```
### Logging
- request‑level logs
- latency measurement
- model version tagging
- YAML‑based logging configuration

## Docker Deployment

Build the image:
docker build -t building-growth-api .


Run the container:
docker run -p 8000:8000 building-growth-api

### Test the API
- http://localhost:8000/health

- http://localhost:8000/docs

---

# Testing
- ETL feature schema (with DB mocking)
- Feature engineering cleanup
- Pipeline construction and forward pass
- Model loading and inference
- API endpoints (/health, /predict, /predict/batch)

---

# Future Improvements
- Monitoring dashboards
- Automated retraining
- Feature store integration
- Spatial ML models (CNNs, U‑Nets)
- Raster imagery integration
- Deployment to Azure App Service or AKS