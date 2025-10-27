# House Price Prediction API

FastAPI service for predicting house prices using trained XGBoost model.

## 🚀 Quick Start

### Run the API server

From project root:
```bash
python src/api/run_api.py
```

or directly with uvicorn:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

### API Documentation

- Interactive docs: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**
- OpenAPI schema: **http://localhost:8000/openapi.json**

## 📋 Available Endpoints

### 1. Health Check
```
GET /health
```
Check if the service is running and model is loaded.

### 2. Model Information
```
GET /model/info
```
Get information about the model including performance metrics.

### 3. Single Prediction
```
POST /predict
```
Predict price for a single house.

**Request body example:**
```json
{
  "MSSubClass": 60,
  "LotArea": 8450,
  "OverallQual": 7,
  "OverallCond": 5,
  "YearBuilt": 2003,
  "GrLivArea": 1710,
  "FullBath": 2,
  "BedroomAbvGr": 3,
  "TotRmsAbvGrd": 8,
  "Fireplaces": 0,
  "GarageCars": 2,
  "GarageArea": 548
}
```

### 4. Batch Prediction
```
POST /predict/batch
```
Predict prices for multiple houses.

**Request body example:**
```json
{
  "houses": [
    {
      "MSSubClass": 60,
      "LotArea": 8450,
      "OverallQual": 7,
      ...
    },
    {
      "MSSubClass": 20,
      "LotArea": 9600,
      "OverallQual": 6,
      ...
    }
  ]
}
```

## 🧪 Testing the API

### Run test script

```bash
python src/api/test_api.py
```

### Using curl

**Single prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MSSubClass": 60,
    "LotArea": 8450,
    "OverallQual": 7,
    "OverallCond": 5,
    "YearBuilt": 2003,
    "GrLivArea": 1710,
    "FullBath": 2,
    "BedroomAbvGr": 3,
    "TotRmsAbvGrd": 8,
    "Fireplaces": 0,
    "GarageCars": 2,
    "GarageArea": 548
  }'
```

**Health check:**
```bash
curl http://localhost:8000/health
```

### Using Python requests

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "MSSubClass": 60,
        "LotArea": 8450,
        "OverallQual": 7,
        "OverallCond": 5,
        "YearBuilt": 2003,
        "GrLivArea": 1710,
        "FullBath": 2,
        "BedroomAbvGr": 3,
        "TotRmsAbvGrd": 8,
        "Fireplaces": 0,
        "GarageCars": 2,
        "GarageArea": 548
    }
)

print(response.json())
# {'predicted_price': 208500.0, 'confidence_interval': {...}}
```

## 📦 Structure

```
src/api/
├── __init__.py              # Module initialization
├── models.py                # Pydantic models for request/response
├── main.py                  # FastAPI application
└── inference.py             # Core inference logic
```

## ⚙️ Configuration

The API loads the model from:
- Model: `src/models/best_pipeline.joblib`
- Config: `src/configs/best_model_config.json`

Make sure these files exist before running the API.

## 🐳 Docker Deployment (Optional)

You can containerize the API using Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Notes

- All features are optional in the API request
- Missing features will be handled by the preprocessing pipeline
- The API automatically handles field name conversions (e.g., `1stFlrSF` → `FirstFlrSF`)
- Model is loaded once on startup for better performance
