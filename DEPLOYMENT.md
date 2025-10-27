# 🐳 Deployment Guide

Hướng dẫn deploy House Price Prediction API với Docker Compose.

## 📁 Structure

```
deployments/
├── api/
│   ├── docker-compose.yaml    # Docker Compose cho API + MLflow
│   ├── Dockerfile             # Docker image cho API
│   └── README.md              # Chi tiết deployment
└── mlflow/
    └── docker-compose.yaml    # Chỉ MLflow (legacy)
```

## 🚀 Quick Start

### Option 1: Deploy với Docker Compose (Recommended)

```bash
# Navigate to deployment directory
cd deployments/api

# Start all services (API + MLflow)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

**Services:**
- API: http://localhost:8000
- MLflow: http://localhost:5555

### Option 2: Deploy chỉ MLflow

```bash
# Navigate to MLflow directory
cd deployments/mlflow

# Start MLflow only
docker compose up -d
```

## 📋 Prerequisites

### 1. Ensure Model is Trained

```bash
# Train model first (if not done)
python train.py
```

### 2. Verify Model File

```bash
# Should exist
ls src/models/best_pipeline.joblib
ls src/configs/best_model_config.json
```

## 🐳 Docker Commands

### Start Services

```bash
cd deployments/api
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
```

### Rebuild

```bash
docker compose up -d --build
```

### Remove Everything

```bash
docker compose down -v  # Removes volumes too
```

## 🧪 Test Deployment

### Test API

```bash
# From project root
python src/api/test_api.py
```

### Or with curl

```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

## 📊 Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **MLflow UI**: http://localhost:5555

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Change port in docker-compose.yaml
# Edit: ports: - "8080:8000"
docker compose up -d
```

### Model Not Found

```bash
# Ensure model exists
ls src/models/best_pipeline.joblib

# Train if needed
python train.py
```

### Check Container Status

```bash
docker ps
docker compose ps
```

### View Logs

```bash
docker compose logs api
docker compose logs mlflow
```

## 📝 Notes

- Model files mounted as read-only from host
- MLflow data persisted in `mlflow_db/` và `mlruns/`
- Use `docker compose down` to stop without removing volumes
- Use `docker compose down -v` to remove volumes (clears MLflow data)

## 🎯 Production Considerations

- Add authentication middleware
- Use environment variables for secrets
- Configure proper CORS origins
- Set up reverse proxy (nginx)
- Add monitoring and logging
- Use HTTPS

## 📚 More Info

- API details: [src/api/README.md](src/api/README.md)
- Deployment details: [deployments/api/README.md](deployments/api/README.md)
