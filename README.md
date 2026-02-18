# 📘 SpaceNet7 End‑to‑End Geospatial ML Pipeline  
*A production‑style geospatial ML system with ETL, feature engineering, temporal modeling, API deployment, testing, and Dockerization.*

---

## 🚀 Overview

This repository implements a **full machine learning engineering workflow** using the **SpaceNet7** multi‑temporal satellite imagery dataset. It demonstrates real‑world engineering practices across:

- Large‑scale geospatial ETL  
- Spatial processing and geometry reconstruction  
- Data warehousing with Postgres/PostGIS  
- Orchestration with Prefect  
- Temporal feature engineering  
- Leakage‑aware ML modeling  
- Packaged inference pipeline  
- FastAPI deployment (single + batch prediction)  
- Dockerized serving  
- Full pytest suite  
- Clear, professional documentation  

The goal is to mirror how **commercial ML engineering teams** build systems: modular, testable, containerized, deployable, and fully reproducible.

---

# 🛰️ Geospatial ETL Pipeline (Weeks 1–2)

The ETL pipeline ingests **6.6M+ pixel‑level building labels** from SpaceNet7 and reconstructs all spatial and temporal metadata from scratch.

### **Key capabilities**
- Parse filename‑encoded metadata (chip ID, AOI, year, month, UTM coordinates)
- Build chip geometries (bounding boxes + centroids)
- Generate AOI polygons from chip centroids
- Assign chips to AOIs via spatial join
- Construct a **star schema** in Postgres/PostGIS:
  - `dim_chip`
  - `dim_aoi`
  - `dim_time`
  - `fact_chip_observation`
- Orchestrate the workflow using Prefect

### **Dataset summary**
- **6,664,652** pixel‑level building observations  
- **60** chips across **30** AOIs  
- Multiple time periods  
- Raw CSV + filename‑encoded metadata  

The ETL has been validated end‑to‑end and successfully loads all data into Postgres.

---

# 🧠 ML Pipeline (Weeks 3–4)

This project models **monthly building count changes** at the chip level.

Each row in the feature table represents:

- a single **chip** (spatial tile)  
- at a single **time_id** (month)  
- with its **building_count** and **prev_building_count**  

### 🎯 Target variable



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

## 📊 Feature Engineering

Defined in `src/ml_end_to_end_pipeline/models/features.py`.

Features include:

- `chip_id` — categorical identifier  
- `building_count` — current month  
- `prev_building_count` — previous month  
- `delta_count` — regression target  

To avoid leakage, we **drop**:

- `year`, `month`  
- `aoi_id`  
- geometries (`geometry`, `centroid`)  

---

## 🕒 Temporal Splitting

Implemented in `src/ml_end_to_end_pipeline/models/split.py`.

- **Train:** earliest months  
- **Validation:** middle months  
- **Test:** most recent months  

This preserves causal structure and prevents future‑to‑past leakage.

---

## 🤖 Modeling Pipeline

Defined in `src/ml_end_to_end_pipeline/models/pipeline.py`.

- Numeric features scaled  
- Categorical features one‑hot encoded  
- Model: `RandomForestRegressor`  
- Hyperparameter tuning via `GridSearchCV`  
- Evaluation via MAE, RMSE, R²  

The best model is saved to:

```
models/best_regression_model.joblib
```

---

# 🧪 Testing (Week 5)

A full pytest suite validates:

- Pipeline construction  
- Model loading  
- Single‑record inference  
- Batch inference  
- Feature engineering  
- Metadata parsing  

Run tests:

```bash
pytest -q
```

All tests pass:

```
6 passed in X.XXs
```

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

# 📚 Tech Stack

### **Languages & Libraries**
- Python  
- scikit‑learn  
- pandas  
- FastAPI  

### **Infrastructure & Tooling**
- Docker  
- Prefect  
- PostgreSQL + PostGIS  
- GitHub Actions  
- Azure (App Service + Container Registry)  
- MLflow or DVC (future)  

---

# 📂 Repository Structure

```
ml-end-to-end-pipeline/
│
├── deployments/
│   └── metadata_etl.yaml
│
├── src/
│   ├── etl/
│   │   ├── metadata.py
│   │   ├── load.py
│   │   ├── transform.py
│   │   ├── ingest.py
│   │   ├── build_aoi_polygons.py
│   │   ├── schema.py
│   │   └── run_metadata_local.py
│   │
│   ├── pipelines/
│   │   └── metadata_flow.py
│   │
│   ├── ml_end_to_end_pipeline/
│   │   ├── models/
│   │   ├── api/
│   │   └── utils/
│
├── models/
├── data/
├── notebooks/
├── tests/
└── README.md
```

---

# 🗺️ Roadmap

- **Week 1–2:** ETL + SQL + Prefect  
- **Week 3–4:** ML Pipelines  
- **Week 5:** API + Docker + Testing  
- **Week 6:** Cloud Deployment  
- **Week 7–8:** CI/CD  
- **Week 9–10:** MLOps (MLflow, DVC)  
- **Week 11–12:** Monitoring + Retraining  

---

# 🔭 Future Improvements

- Add monitoring dashboards  
- Add automated retraining pipeline  
- Add feature store integration  
- Add spatial ML models (CNNs, U‑Nets)  
- Integrate raster imagery  
- Deploy to Azure App Service or AKS  

---