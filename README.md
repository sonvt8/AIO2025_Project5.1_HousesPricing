# Dự đoán Giá Nhà - AIO2025 Project 5.1

Hệ thống dự đoán giá nhà sử dụng XGBoost với MLflow tracking, dựa trên Ames Housing Dataset.

## 📁 Cấu trúc dự án

```
AIO2025_Project5.1_HousesPricing/
├── data/
│   └── raw/                                    # Dữ liệu gốc
│       └── train-house-prices-advanced-regression-techniques.csv
├── src/
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
│   └── mlflow/
│       └── docker-compose.yaml                # MLflow tracking server
├── notebooks/
│   └── house_price_analysis_mlflow.ipynb      # Jupyter notebook experiments
├── train.py                                   # Script training chính
├── inference.py                               # Script inference
├── requirements.txt                           # Dependencies
└── README.md                                  # File này
```

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Khởi động MLflow tracking server

Mở terminal mới và chạy:

```bash
docker compose -f deployments/mlflow/docker-compose.yaml up -d
```

MLflow UI sẽ chạy tại: **http://localhost:5555**

### 3. Training model

Chạy script training:

```bash
python train.py
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

## 🔍 MLflow UI

Xem kết quả training trên MLflow:

1. Truy cập: **http://localhost:5555**
2. Chọn experiment: `House_Price_Prediction`
3. Xem metrics, parameters và model artifacts

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

## 🔄 Workflow

```
Raw data (data/raw/)
    ↓
Preprocessing (custom transformers)
    ↓
Feature Engineering (domain features)
    ↓
Training (XGBoost với MLflow tracking)
    ↓
Evaluation (CV + Test metrics)
    ↓
Save pipeline (src/models/)
```

## 🎯 Sử dụng Model

### Inference

```bash
python inference.py data/raw/test_data.csv --output predictions.csv
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

## 📚 Dependencies

- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - ML models và preprocessing
- `xgboost` - Gradient boosting model
- `mlflow` - Experiment tracking
- `joblib` - Model serialization
- `docker` - MLflow server

## 🎓 Model Performance

- **Dataset**: Ames Housing (1460 samples, 80 features)
- **Algorithm**: XGBoost Regressor
- **Evaluation**: 5-fold cross-validation
- **Best RMSE**: ~24609
- **Best R²**: ~0.92

## 🚧 Tương lai

- [ ] API endpoint với FastAPI
- [ ] Streamlit app cho interactive predictions
- [ ] Model versioning
- [ ] Batch inference
- [ ] Model monitoring

## 📝 Notes

- Raw data: Giữ nguyên trong `data/raw/`
- Trained models: Lưu trong `src/models/` (không commit lên Git)
- MLflow data: Lưu trong `deployments/mlflow/` (không commit lên Git)
- Intermediate data: **Không lưu** - chỉ dùng pipeline để transform

## 📄 License

Project cho AIO2025 - Project 5.1
