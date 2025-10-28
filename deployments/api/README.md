# API & Frontend Deployment with Docker Compose

Hướng dẫn deploy House Price Prediction API và giao diện Streamlit sử dụng Docker Compose.

## 📋 Yêu cầu

- Docker Engine 20.10+
- Docker Compose v2.0+
- Model đã được train (`src/models/best_pipeline.joblib`)

## 🚀 Quick Start

### 1. Kiểm tra Model đã có

```bash
# Kiểm tra model file
ls src/models/best_pipeline.joblib

# Nếu chưa có, train model trước
cd ../..
python train.py
```

### 2. Build và Start Containers

```bash
# Navigate to api deployment directory
cd deployments/api

# Build và start API + Frontend + MLflow
docker compose up -d --build

# Xem logs
docker compose logs -f
```

### 3. Kiểm tra Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend (Streamlit)**: http://localhost:8501
- **MLflow**: http://localhost:5555

## 📊 Services

### API Service

- **Container**: `house-price-api`
- **Port**: 8000
- **Health Check**: Built-in health check every 30s

### MLflow Service

- **Container**: `mlflow-tracking-server`
- **Port**: 5555
- **Data**: Persistent trong `mlflow_db/` và `mlruns/`

## 🛠️ Management Commands

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### View Logs

```bash
# Tất cả services
docker compose logs -f

# Chỉ API
docker compose logs -f api

# Chỉ MLflow
docker compose logs -f mlflow
```

### Rebuild Containers

```bash
# Rebuild và restart
docker compose up -d --build

# Rebuild không cache
docker compose build --no-cache
```

### Scale API (nếu cần)

```bash
# Scale API instances
docker compose up -d --scale api=3
```

## 🧪 Test API

### Test với curl

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "OverallQual": 7,
    "GrLivArea": 1710,
    "YearBuilt": 2003,
    "FullBath": 2,
    "GarageCars": 2,
    "GarageArea": 548
  }'
```

### Test với Python

```bash
python src/api/test_api.py
```

## 🔍 Troubleshooting

### Container không start

```bash
# Check logs
docker compose logs api

# Check if model exists
ls src/models/
```

### Model không load

```bash
# Verify model file exists
docker exec house-price-api ls -lh /app/src/models/

# Check model loading logs
docker compose logs api | grep "Model loaded"
```

### Port conflict

Nếu port 8000 hoặc 5555 đã được sử dụng, sửa trong `docker-compose.yaml`:

```yaml
ports:
  - "8080:8000"  # Change external port to 8080
```

### Database issues

MLflow data được lưu trong `mlflow_db/` và `mlruns/`:

```bash
# Xóa và reset MLflow data
docker compose down -v
rm -rf mlflow_db/ mlruns/
docker compose up -d
```

## 📦 Volume Mounts

Model/raw data được mount từ host:

```
Host                          Container
─────────────────────────────────────────
src/models/    →    /app/src/models
src/configs/   →    /app/src/configs
data/raw/      →    /app/data/raw
```

## 🔐 Security Notes

- **Production**: Không dùng `allow_origins=["*"]` trong CORS
- **Authentication**: Thêm auth middleware cho production
- **Secrets**: Sử dụng Docker secrets cho sensitive data
- **Volumes**: Use named volumes instead of bind mounts

## 📈 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Container health
docker ps --filter "name=house-price-api"
```

### Resource Usage

```bash
docker stats house-price-api
```

## 🔄 Update Workflow

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build

# Verify
curl http://localhost:8000/health
```
