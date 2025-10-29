# Dự đoán Giá Nhà - AIO2025 Project 5.1

Hệ thống dự đoán giá nhà sử dụng XGBoost, FastAPI, Streamlit và MLflow (Ames Housing Dataset).

## 📁 Cấu trúc dự án

```
AIO2025_Project5.1_HousesPricing/
├── data/
│   └── raw/                                    # Dữ liệu gốc
│       └── train-house-prices-advanced-regression-techniques.csv
├── src/
│   ├── api/                                    # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                            # FastAPI app
│   │   ├── models.py                          # Pydantic models
│   │   ├── inference.py                       # Inference logic & CLI
│   │   ├── run_api.py                         # Script chạy API server
│   │   └── test_api.py                        # Test script cho API
│   ├── processing/                             # Xử lý dữ liệu
│   │   ├── __init__.py
│   │   ├── transformers.py                     # Custom transformers
│   │   └── data_processing.py                  # Preprocessing pipeline
│   ├── e_featuring/                           # Feature engineering
│   │   ├── __init__.py
│   │   └── data_featuring.py                  # Domain-specific features
│   ├── training/                              # Training model
│   │   ├── __init__.py
│   │   ├── pipeline.py                        # Training pipeline
│   │   └── train_model.py                     # Training script
│   ├── configs/
│   │   └── best_model_config.json             # Cấu hình model tốt nhất
│   └── models/                                # Models đã train (auto-generated)
│       ├── best_pipeline.joblib              # Pipeline hoàn chỉnh
│       └── feature_pipeline.joblib           # Feature pipeline
├── deployments/
│   ├── api/                                   # API deployment
│   │   ├── docker-compose.yaml                # Docker Compose for API
│   │   └── Dockerfile                        # Dockerfile for API
│   └── mlflow/
│       └── docker-compose.yaml                # MLflow tracking server
├── notebooks/
│   └── house_price_analysis_mlflow.ipynb      # Jupyter notebook experiments
├── train.py                                   # Script training chính (root)
├── requirements.txt                           # Dependencies
└── README.md                                  # File này
```

## 🚀 Quick Start

### Phương án A: Chạy nhanh bằng Docker Compose (khuyến nghị)

```bash
python train.py               # nếu chưa có model
cd deployments/api
docker compose up -d --build
```

Truy cập:
- API: http://localhost:8000 (Docs: http://localhost:8000/docs)
- Frontend: http://localhost:8501
- MLflow: http://localhost:5555

### Phương án B: Chạy local (dev)

```bash
pip install -r requirements.txt
python train.py               # nếu chưa có model
python src/api/run_api.py     # chạy API tại 8000
streamlit run src/frontend/app.py
```

## 📊 Kết quả

### Performance metrics

Model được train với cấu hình từ `src/configs/best_model_config.json`:

- **CV RMSE**: 25259.42 ± 3479.64
- **Test RMSE**: 24608.89
- **Test R²**: 0.9210

### Output files

Sau khi training, các files sẽ được tạo trong `src/models/`:

- `best_pipeline.joblib` - Pipeline hoàn chỉnh (features + model)
- `feature_pipeline.joblib` - Feature engineering pipeline

## 🔍 MLflow

Mở MLflow UI tại `http://localhost:5555` để xem metrics, params và artifacts (khi chạy bằng compose đã có sẵn).

### Thông tin được track

- **Hyperparameters**: learning_rate, max_depth, subsample, ...
- **Performance metrics**: CV RMSE, CV R², Test RMSE, Test R²
- **Model artifacts**: Complete trained pipeline
- **Configuration**: Feature engineering và preprocessing settings

## 🏗️ Pipeline

### 1. Data Processing (`src/processing/`)

**Custom Transformers:**
- `OrdinalMapper` - Map categorical variables sang numeric
- `MissingnessIndicator` - Tạo indicators cho missing values
- `RarePooler` - Gộp rare categories thành 'Other'
- `TargetEncoderTransformer` - Target encoding với smoothing
- `FiniteCleaner` - Convert infinite values thành NaN
- `DropAllNaNColumns` - Loại bỏ columns toàn NaN

**Preprocessing:**
- Ordinal encoding cho 20 ordinal features
- Missing value imputation (categorical: most_frequent, numerical: median)
- One-hot encoding cho categorical features
- Quantile transformation cho continuous features

### 2. Feature Engineering (`src/e_featuring/`)

**Domain features (18 features):**
- `TotalSF` - Total square footage
- `TotalBath` - Total bathrooms
- `HouseAge`, `RemodAge`, `GarageAge` - Age features
- `IsRemodeled`, `Has2ndFlr` - Binary features
- `TotalPorchSF` - Total porch area
- `BathPerBedroom`, `RoomsPerArea`, `LotAreaRatio` - Ratio features
- `MoSold_sin`, `MoSold_cos` - Seasonal features
- `Neighborhood_BldgType` - Interaction features
- `Ln_TotalSF` - Log transformation
- `IQ_OQ_GrLiv`, `IQ_OQ_TotalSF` - Quality-area interactions
- `LotArea_clip` - Winsorization

### 3. Model Training (`src/training/`)

**Best Model:** XGBoost Regressor với hyperparameters từ config

**Training Process:**
1. Load data và split train/test (80/20)
2. Build feature pipeline với domain features
3. Train XGBoost với best hyperparameters
4. Cross-validation (5-fold)
5. Test set evaluation
6. Lưu pipeline và artifacts vào MLflow

## 🔄 Quy trình

Raw data → Preprocessing → Feature Engineering → Training (MLflow) → Evaluation → Save pipeline (`src/models/`)

## 🎯 Sử dụng Model

### Inference qua API

**Single prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"OverallQual": 7, "GrLivArea": 1710, "YearBuilt": 2003}'
```

**Batch prediction:**
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"houses": [{...}, {...}]}'
```

**Python client:**
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"OverallQual": 7, "GrLivArea": 1710, "YearBuilt": 2003}
)
print(response.json())
```

Chi tiết tham số/response xem tại `src/api/README.md`.

### Inference qua CLI

```bash
python src/api/inference.py data/raw/test_data.csv --output predictions.csv
```

### Programmatic usage

```python
import joblib
import pandas as pd

# Load trained pipeline
pipeline = joblib.load('src/models/best_pipeline.joblib')

# Predict
new_data = pd.read_csv('new_houses.csv')
predictions = pipeline.predict(new_data)
print(f"Predicted prices: {predictions}")
```

## 📚 Tech stack

- FastAPI (API), Streamlit (UI), XGBoost + scikit-learn (ML), MLflow (tracking)

## 🎓 Model Performance

- **Dataset**: Ames Housing (1460 samples, 80 features)
- **Algorithm**: XGBoost Regressor
- **Evaluation**: 5-fold cross-validation
- **Best RMSE**: ~24609
- **Best R²**: ~0.92

## 🚧 Tương lai

- [x] API FastAPI, [x] Batch inference, [x] Streamlit UI
- [ ] Model versioning, [ ] Monitoring/alerts

## 📝 Notes

- Raw data: Giữ nguyên trong `data/raw/`
- Trained models: Lưu trong `src/models/` (không commit lên Git)
- MLflow data: Lưu trong `deployments/mlflow/` (không commit lên Git)
- API: Chạy trên port 8000, có thể truy cập qua Docker hoặc local
- Intermediate data: **Không lưu** - chỉ dùng pipeline để transform

## 🔧 Deployment

### Triển khai

```bash
# Docker Compose (khuyến nghị)
cd deployments/api && docker compose up -d --build

# Local development
pip install -r requirements.txt
python src/api/run_api.py
```

### Test API

```bash
# After starting API
python src/api/test_api.py
```

### Truy cập dịch vụ

- API: http://localhost:8000 (Docs: /docs)
- Frontend: http://localhost:8501
- MLflow: http://localhost:5555

## 📄 License

Project cho AIO2025 - Project 5.1
