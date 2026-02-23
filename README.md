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



This project models **monthly building count changes** at the chip level.

Each row in the feature table represents:

- a single **chip** (spatial tile)  
- at a single **time_id** (month)  
- with its **building_count** and **prev_building_count**  

### 🎯 Target variable



\[
\Delta_t = \text{building\_count}_t - \text{building\_count}_{t-1}
\]



This is a **regression problem**.

---

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

# 📦 Installation

Install the package in editable mode:

```bash
pip install -e .
```

Import it:

```python
from ml_end_to_end_pipeline.models.predict import run_single_inference
```

---

# 🔮 Inference (CLI)

### Single‑record

```bash
python -m ml_end_to_end_pipeline.models.predict \
    --chip_id A123 \
    --building_count 50 \
    --prev_building_count 45
```

### Batch (CSV)

```bash
python -m ml_end_to_end_pipeline.models.predict \
    --input data/new_data.csv \
    --output predictions.csv
```

---

# 🏗️ Architecture Diagram

```
                ┌──────────────────────────┐
                │   Raw Pixel CSV (6.6M)   │
                └─────────────┬────────────┘
                              │
                              ▼
                        ETL Pipeline
      (parse → geometry → AOI → star schema → PostGIS)
                              │
                              ▼
                    Feature Engineering
                              │
                              ▼
                     Temporal Train/Val/Test
                              │
                              ▼
                    Regression Model (RF)
                              │
                              ▼
                   Saved Model Artifact
                              │
          ┌───────────────┬───────────────┐
          ▼               ▼               ▼
   predict.py       FastAPI Service     Tests
          │               │               │
          ▼               ▼               ▼
   CLI Inference     JSON API        CI-ready suite
          │               │
          └──────────► Docker ◄──────────┘
```

---

## Week 6: API Testing, Logging, and Container Reliability

Week 6 focused on validating the end‑to‑end inference API, improving observability, and ensuring the service runs reliably inside Docker. This was the first week where the full ML pipeline, model artifact, and FastAPI service were exercised together in a production‑like environment.

### Key Achievements

#### 1. API Testing & Validation
- Successfully tested `/health`, `/predict`, and `/predict/batch` endpoints using `curl`.
- Verified correct request/response schemas and JSON parsing.
- Confirmed that the regression model loads correctly inside the container and produces valid predictions.

#### 2. Logging Implementation
- Added structured logging to the FastAPI application, including:
  - Request‑level logs  
  - Latency measurement  
  - Model version tagging  
- Integrated a `logging_config.yaml` file and updated Uvicorn to use it.
- Installed `PyYAML` and validated that logs stream correctly via `docker logs -f`.

#### 3. Import & Inference Stability Fixes
- Resolved import errors by aligning API imports with the existing project structure (`models.predict`).
- Updated the API to load the model once at startup for efficient inference.
- Ensured DataFrame construction matches the model’s expected feature schema.

#### 4. Docker Reliability Improvements
- Rebuilt the Docker image with a clean build context and validated the internal file structure.
- Ensured all dependencies (including scikit‑learn and PyYAML) are installed correctly.
- Verified that the API runs cleanly in detached mode and is reachable at `localhost:8000`.

### Outcome
By the end of Week 6, the project had a fully functional, containerized inference API with reliable logging, stable imports, and validated prediction behavior. This foundation enables Week 7’s focus on testing, linting, and CI/CD.


---


---

# 🌐 FastAPI Inference Service (Week 5)

A production‑ready API supports **single** and **batch** prediction.

Start the API:

```bash
uvicorn ml_end_to_end_pipeline.api.app:app --reload
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/predict` | Single prediction |
| `POST` | `/predict/batch` | Batch prediction |

Swagger UI:

```
http://localhost:8000/docs
```

---

# 🐳 Docker Deployment (Week 5)

Build the image:

```bash
docker build -t building-growth-api .
```

Run the container:

```bash
docker run -p 8000:8000 building-growth-api
```

Test the API:

```
http://localhost:8000/health
http://localhost:8000/docs
```

---

# 📦 Installation

Install the package in editable mode:

```bash
pip install -e .
```

Import it:

```python
from ml_end_to_end_pipeline.models.predict import run_single_inference
```

---

# 🔮 Inference (CLI)

### Single‑record

```bash
python -m ml_end_to_end_pipeline.models.predict \
    --chip_id A123 \
    --building_count 50 \
    --prev_building_count 45
```

### Batch (CSV)

```bash
python -m ml_end_to_end_pipeline.models.predict \
    --input data/new_data.csv \
    --output predictions.csv
```

---

# 🏗️ Architecture Diagram

```
                ┌──────────────────────────┐
                │   Raw Pixel CSV (6.6M)   │
                └─────────────┬────────────┘
                              │
                              ▼
                        ETL Pipeline
      (parse → geometry → AOI → star schema → PostGIS)
                              │
                              ▼
                    Feature Engineering
                              │
                              ▼
                     Temporal Train/Val/Test
                              │
                              ▼
                    Regression Model (RF)
                              │
                              ▼
                   Saved Model Artifact
                              │
          ┌───────────────┬───────────────┐
          ▼               ▼               ▼
   predict.py       FastAPI Service     Tests
          │               │               │
          ▼               ▼               ▼
   CLI Inference     JSON API        CI-ready suite
          │               │
          └──────────► Docker ◄──────────┘
```

---

# 🗄️ Database Schema

### `dim_chip`
Chip‑level metadata including geometry and centroid.

### `dim_aoi`
AOI polygons reconstructed from chip centroids.

### `dim_time`
Year/month combinations extracted from filenames.

### `fact_chip_observation`
Building‑level observations linked to chip, AOI, and time.

---

# Future Improvements
- Monitoring dashboards
- Automated retraining
- Feature store integration
- Spatial ML models (CNNs, U‑Nets)
- Raster imagery integration
- Deployment to Azure App Service or AKS