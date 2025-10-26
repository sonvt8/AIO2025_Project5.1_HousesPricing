"""
Main training script for house price prediction with MLflow tracking.
Loads best model configuration and trains the model end-to-end.
"""

import json
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.sklearn

from ..e_featuring.data_featuring import make_feature_space
from .pipeline import build_model_pipeline, evaluate_model
from .pipeline import HAS_XGB

if HAS_XGB:
    import xgboost as xgb


def load_config(config_path):
    """Load best model configuration from JSON file."""
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def create_xgb_model_from_config(config):
    """Create XGBoost model with hyperparameters from config."""
    if not HAS_XGB:
        raise ImportError("XGBoost is not installed")

    hyperparams = config["hyperparameters"]

    model = xgb.XGBRegressor(
        n_estimators=4000,
        learning_rate=hyperparams.get("learning_rate", 0.03),
        max_depth=hyperparams.get("max_depth", 4),
        subsample=hyperparams.get("subsample", 0.8),
        colsample_bytree=hyperparams.get("colsample_bytree", 0.8),
        min_child_weight=hyperparams.get("min_child_weight", 2.0),
        reg_lambda=hyperparams.get("reg_lambda", 3.0),
        reg_alpha=hyperparams.get("reg_alpha", 0.2),
        gamma=hyperparams.get("gamma", 0.05),
        max_bin=hyperparams.get("max_bin", 256),
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
        missing=np.nan,
    )
    return model


def train_model(
    data_path,
    config_path,
    output_dir="src/models",
    mlflow_experiment="House_Price_Prediction",
    mlflow_tracking_uri=None,
):
    """
    Main training function.

    Args:
        data_path: Path to raw training data CSV
        config_path: Path to best model configuration JSON
        output_dir: Directory to save trained pipeline
        mlflow_experiment: MLflow experiment name
        mlflow_tracking_uri: MLflow tracking URI (default: check env var or use docker)
    """
    # Set up MLflow tracking URI
    if mlflow_tracking_uri is None:
        # Check environment variable first
        mlflow_tracking_uri = os.environ.get(
            "MLFLOW_TRACKING_URI", "http://localhost:5555"
        )

    print(f"🔗 MLflow tracking URI: {mlflow_tracking_uri}")
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    # Load configuration
    print("📋 Loading best model configuration...")
    config = load_config(config_path)

    # Load data
    print(f"📊 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"   Dataset shape: {df.shape}")

    # Split data
    X = df.drop("SalePrice", axis=1)
    y = df["SalePrice"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   Training set: {X_train.shape[0]} samples")
    print(f"   Test set: {X_test.shape[0]} samples")

    # Set up MLflow experiment
    mlflow.set_experiment(mlflow_experiment)

    # Get feature engineering config
    feat_config = config.get("feature_engineering", {})
    te_cols = feat_config.get(
        "target_encoder_features",
        [
            "Neighborhood",
            "MSZoning",
            "Exterior1st",
            "Exterior2nd",
            "SaleCondition",
            "BldgType",
            "Neighborhood_BldgType",
        ],
    )
    te_alpha = feat_config.get("target_encoder_alpha", 30.0)
    rare_min_count = feat_config.get("rare_pooler_min_count", 15)

    with mlflow.start_run(run_name="Best_Model_Training"):
        # Build feature pipeline
        print("🔧 Building feature pipeline...")
        feature_pipe = make_feature_space(
            X_train,
            X_test,
            te_cols=te_cols,
            te_alpha=te_alpha,
            rare_min_count=rare_min_count,
        )
        print("   Feature pipeline created successfully")

        # Create model
        print("🤖 Creating XGBoost model...")
        model = create_xgb_model_from_config(config)

        # Log hyperparameters
        hyperparams = config["hyperparameters"]
        for param, value in hyperparams.items():
            mlflow.log_param(f"xgb_{param}", value)

        mlflow.log_param("model_type", "XGB")
        mlflow.log_param("n_estimators", 4000)

        # Build complete pipeline
        print("🏗️  Building complete pipeline...")
        model_pipe = build_model_pipeline(feature_pipe, model, "XGB")

        # Evaluate model
        print("📈 Evaluating model (this may take a few minutes)...")
        results = evaluate_model(
            model_pipe, X_train, y_train, X_test, y_test, n_splits=5, random_state=42
        )

        # Log metrics
        print("\n📊 Model Performance:")
        print(
            f"   CV RMSE: {results['cv_rmse_mean']:.2f} ± {results['cv_rmse_std']:.2f}"
        )
        print(f"   CV R²: {results['cv_r2_mean']:.4f} ± {results['cv_r2_std']:.4f}")
        print(f"   Test RMSE: {results['test_rmse']:.2f}")
        print(f"   Test R²: {results['test_r2']:.4f}")

        mlflow.log_metric("cv_rmse_mean", results["cv_rmse_mean"])
        mlflow.log_metric("cv_rmse_std", results["cv_rmse_std"])
        mlflow.log_metric("cv_r2_mean", results["cv_r2_mean"])
        mlflow.log_metric("cv_r2_std", results["cv_r2_std"])
        mlflow.log_metric("test_rmse", results["test_rmse"])
        mlflow.log_metric("test_r2", results["test_r2"])

        # Log expected metrics from config for comparison
        expected_metrics = config.get("performance", {})
        print("\n📋 Expected Performance (from config):")
        print(f"   CV RMSE: {expected_metrics.get('cv_rmse_mean', 'N/A')}")
        print(f"   Test RMSE: {expected_metrics.get('test_rmse', 'N/A')}")
        print(f"   Test R²: {expected_metrics.get('test_r2', 'N/A')}")

        # Save pipeline
        os.makedirs(output_dir, exist_ok=True)
        pipeline_path = os.path.join(output_dir, "best_pipeline.joblib")

        print(f"\n💾 Saving pipeline to {pipeline_path}...")
        mlflow.sklearn.log_model(model_pipe, "model")

        import joblib

        joblib.dump(model_pipe, pipeline_path)
        print("   ✅ Pipeline saved successfully")

        # Save feature pipeline separately for inference
        feature_pipeline_path = os.path.join(output_dir, "feature_pipeline.joblib")
        joblib.dump(feature_pipe, feature_pipeline_path)
        print(f"   ✅ Feature pipeline saved to {feature_pipeline_path}")

        print("\n✅ Training completed successfully!")
        print("🔗 View results at: mlflow ui")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train house price prediction model")
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/train-house-prices-advanced-regression-techniques.csv",
        help="Path to training data CSV",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="src/configs/best_model_config.json",
        help="Path to model configuration JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="src/models",
        help="Directory to save trained model",
    )
    parser.add_argument(
        "--experiment",
        type=str,
        default="House_Price_Prediction",
        help="MLflow experiment name",
    )

    args = parser.parse_args()

    train_model(
        data_path=args.data,
        config_path=args.config,
        output_dir=args.output_dir,
        mlflow_experiment=args.experiment,
    )
