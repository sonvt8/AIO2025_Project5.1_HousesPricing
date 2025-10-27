"""
FastAPI application for House Price Prediction Service.
Provides REST API endpoints for model inference.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import (
    HouseFeatures,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse,
)
import pandas as pd


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "src" / "models" / "best_pipeline.joblib"
CONFIG_PATH = PROJECT_ROOT / "src" / "configs" / "best_model_config.json"

# Global variable to store pipeline
_pipeline = None
_model_info = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup and cleanup on shutdown."""
    global _pipeline, _model_info

    # Load pipeline
    try:
        import joblib

        _pipeline = joblib.load(str(MODEL_PATH))
        print(f"✅ Model loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        _pipeline = None

    # Load model config
    try:
        with open(CONFIG_PATH, "r") as f:
            _model_info = json.load(f)
        print(f"✅ Config loaded from {CONFIG_PATH}")
    except Exception as e:
        print(f"⚠️  Warning: Could not load config: {e}")
        _model_info = None

    yield

    # Cleanup
    _pipeline = None
    _model_info = None


# Create FastAPI app
app = FastAPI(
    title="House Price Prediction API",
    description="API for predicting house prices using XGBoost model",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def convert_to_dataframe(features: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert features dictionary to DataFrame with correct column names.
    Model pipeline expects ALL columns from training data, so we need to create
    a complete DataFrame with all required columns.

    Args:
        features: Dictionary of house features

    Returns:
        DataFrame with all required columns (missing columns filled with NaN)
    """
    # Map Python-safe field names to original column names
    field_mapping = {
        "FirstFlrSF": "1stFlrSF",
        "SecondFlrSF": "2ndFlrSF",
        "ThreeSsnPorch": "3SsnPorch",
    }

    # Create a copy to avoid modifying the original
    features_copy = features.copy()

    # Convert field names
    for new_name, old_name in field_mapping.items():
        if new_name in features_copy:
            features_copy[old_name] = features_copy.pop(new_name)

    # Remove SalePrice if present (it's the target)
    if "SalePrice" in features_copy:
        del features_copy["SalePrice"]

    # Preserve Id if present (model might need it during processing)
    # If not present, we'll add a dummy value
    preserve_id = "Id" in features_copy

    # Get the required columns from the pipeline's feature names
    # We need to load the training data to get all column names
    training_data_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "train-house-prices-advanced-regression-techniques.csv"
    )

    try:
        # Load one row to get all column names
        training_df = pd.read_csv(training_data_path, nrows=1)
        all_columns = list(training_df.columns)

        # Exclude only target column
        if "SalePrice" in all_columns:
            all_columns.remove("SalePrice")

        # Keep Id column in the list (will be used during preprocessing)

        # Create DataFrame with all required columns
        # Fill missing columns with None (will be converted to NaN)
        row_data = {}

        # Add Id column with dummy value if not provided
        if not preserve_id and "Id" in all_columns:
            row_data["Id"] = 999999  # Dummy ID

        # Add all other columns
        for col in all_columns:
            if col == "SalePrice":  # Skip target
                continue
            value = features_copy.get(col, None)
            # Convert None to np.nan for better compatibility
            if value is None:
                row_data[col] = np.nan
            else:
                row_data[col] = value

        df = pd.DataFrame([row_data])

        # Ensure proper data types for numeric columns
        # Convert string representations of numbers to actual numbers
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].replace([np.nan, None, "NA", "nan", ""], np.nan)

        return df

    except Exception as e:
        # Fallback: just create DataFrame from provided features
        # This might fail if model expects specific columns
        print(f"Warning: Could not load training data structure: {e}")
        return pd.DataFrame([features_copy])


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint."""
    return {
        "message": "House Price Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """
    Check service health.

    Returns:
        Health status and model loading status
    """
    return HealthResponse(
        status="healthy" if _pipeline is not None else "unhealthy",
        model_loaded=_pipeline is not None,
        version="1.0.0",
    )


@app.get("/model/info", response_model=ModelInfoResponse, summary="Model information")
async def get_model_info():
    """
    Get information about the loaded model.

    Returns:
        Model name, type, version, and performance metrics
    """
    if _model_info is None:
        raise HTTPException(status_code=503, detail="Model info not available")

    try:
        performance = _model_info.get("performance", {})

        return ModelInfoResponse(
            model_name=_model_info.get("model_info", {}).get("name", "XGBoost"),
            model_type=_model_info.get("model_info", {}).get("type", "Regressor"),
            version=_model_info.get("model_info", {}).get("model_version", "1.0"),
            performance={
                "cv_rmse": performance.get("cv_rmse_mean", 0.0),
                "cv_r2": performance.get("cv_r2_mean", 0.0),
                "test_rmse": performance.get("test_rmse", 0.0),
                "test_r2": performance.get("test_r2", 0.0),
            },
            features_count=len(
                _model_info.get("feature_engineering", {}).get("domain_features", [])
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting model info: {str(e)}"
        )


@app.post(
    "/predict", response_model=PredictionResponse, summary="Predict single house price"
)
async def predict_house(features: HouseFeatures):
    """
    Predict price for a single house.

    Args:
        features: House features

    Returns:
        Predicted price and confidence information
    """
    if _pipeline is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please check /health endpoint."
        )

    try:
        # Convert Pydantic model to dict
        features_dict = features.dict(exclude_none=True)

        # Convert to DataFrame with correct column names
        df = convert_to_dataframe(features_dict)

        # Make prediction
        prediction = _pipeline.predict(df)[0]

        return PredictionResponse(
            predicted_price=float(prediction),
            confidence_interval={
                "lower": float(prediction * 0.9),
                "upper": float(prediction * 1.1),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error making prediction: {str(e)}"
        )


@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predict batch of houses",
)
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict prices for multiple houses.

    Args:
        request: Batch prediction request with list of houses

    Returns:
        List of predicted prices and statistics
    """
    if _pipeline is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please check /health endpoint."
        )

    try:
        # Convert list of dicts to DataFrame
        features_list = []
        for house in request.houses:
            # Handle field name conversion for each house
            df = convert_to_dataframe(house)
            features_list.append(df)

        # Concatenate all houses
        df_all = pd.concat(features_list, ignore_index=True)

        # Make predictions
        predictions = _pipeline.predict(df_all)

        # Calculate statistics
        stats = {
            "min": float(predictions.min()),
            "max": float(predictions.max()),
            "mean": float(predictions.mean()),
            "median": float(np.median(predictions)),
            "std": float(predictions.std()),
        }

        return BatchPredictionResponse(
            predictions=[float(p) for p in predictions],
            count=len(predictions),
            statistics=stats,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error making batch prediction: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
