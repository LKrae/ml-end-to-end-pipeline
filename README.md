# SpaceNet7 End‑to‑End Geospatial ML Pipeline

## Overview
This project demonstrates a full machine learning engineering workflow, including data ingestion, ETL pipelines, model training, API deployment, CI/CD automation, cloud hosting, and MLOps practices. It is designed as a commercial-grade portfolio project to showcase ML engineering skills end-to-end.

This project implements a complete, production‑style geospatial machine learning pipeline using the SpaceNet7 dataset. It demonstrates real‑world data engineering and ML engineering skills across ingestion, transformation, spatial processing, data warehousing, orchestration, and modeling.

The pipeline ingests 6.6M+ pixel‑level building labels, reconstructs chip geometries and AOIs, builds a star‑schema warehouse in Postgres/PostGIS, and orchestrates the workflow using Prefect. Future phases extend into feature engineering, model training, inference, and deployment.

The goal is to build a system that mirrors how real ML engineering teams work: modular, testable, containerized, deployable, and fully documented.

---

## Project Goals
- Build a production-minded ML system from scratch
- Demonstrate engineering workflows (CI/CD, testing, versioning)
- Deploy a containerized ML model to the cloud
- Implement experiment tracking and model lifecycle management
- Provide clear documentation and reproducible workflows

---

## Architecture
- Python ETL for parsing, geometry creation, and AOI assignment

- Postgres + PostGIS as the analytical warehouse

- Star schema for clean analytics and ML feature generation

- Prefect for orchestration and scheduling

- ML pipeline (Week 3+) for chip‑level predictions

---
## Dataset
- SpaceNet7 provides multi‑temporal satellite imagery and pixel‑level building labels. This project uses:

- 6,664,652 pixel‑level building observations

- 60 chips across 30 AOIs

- Multiple time periods

- Raw CSV + filename‑encoded metadata

The ETL pipeline reconstructs all spatial and temporal metadata from scratch.

---
## ETL Pipeline
1. The ETL process performs the following steps:
2. Load pixel CSV (6.6M rows)
3. Parse filenames into structured metadata (chip ID, AOI, time, coordinates)
4. Build chip geometries (bounding boxes + centroids)
5. Generate AOI polygons from chip centroids
6. Assign chips to AOIs via spatial join
    - Construct star‑schema tables:
    - dim_chip
    - dim_aoi
    - dim_time
    - fact_chip_observation

7. Load all tables into Postgres/PostGIS
8. Orchestrate the pipeline with Prefect

The ETL has been validated end‑to‑end and successfully loads all data into Postgres.

---

## Tech Stack
**Languages & Libraries**
- Python
- scikit-learn
- pandas
- FastAPI

**Infrastructure & Tooling**
- Docker
- GitHub Actions
- Azure (App Service + Container Registry)
- MLflow or DVC
- Prefect
- PostgreSQL

---
## Database Schema
dim_chip
Chip‑level metadata including geometry and centroid.

dim_aoi
AOI polygons reconstructed from chip centroids.

dim_time
Year/month combinations extracted from filenames.

fact_chip_observation
Building‑level observations linked to chip, AOI, and time.

---

## Repository Structure
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
│   │   └── metadata_flow.py     # ← Prefect flow lives here
│   │
│   ├── models/                  # Week 3
│   ├── api/                     # Week 4–5
│   └── utils/                   # Shared helpers
│
├── data/
├── notebooks/
├── tests/
├── docs/
└── README.md

```

---

## How to Run Locally
Instructions will be added in Week 5 once the API and Docker components are implemented.

---

## Roadmap
- **Week 1–2:** ETL + SQL + Prefect
- **Week 3–4:** ML Pipelines
- **Week 5–6:** API + Docker
- **Week 7–8:** CI/CD
- **Week 9–10:** Cloud Deployment
- **Week 11–12:** MLOps
---

## Future Improvements
- Add monitoring dashboards
- Add automated retraining pipeline
- Add feature store integration