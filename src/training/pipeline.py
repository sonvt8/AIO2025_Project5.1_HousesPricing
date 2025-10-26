"""
Training pipeline for house price prediction.
Handles model training, evaluation, and saving with MLflow tracking.
"""

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate, KFold
from sklearn.metrics import mean_squared_error, r2_score
import math

# Try to import xgboost
try:
    import xgboost as xgb

    HAS_XGB = True
except ImportError:
    xgb = None
    HAS_XGB = False


def make_scorers():
    """Get scoring metrics for cross-validation"""
    from sklearn.metrics import make_scorer

    scorers = {
        "neg_rmse": make_scorer(
            lambda yt, yp: -math.sqrt(mean_squared_error(yt, yp)),
            greater_is_better=True,
        ),
        "r2": "r2",
    }
    return scorers


def rmse(y_true, y_pred):
    """Calculate RMSE"""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def build_model_pipeline(feature_pipe, model, model_name):
    """
    Build a complete pipeline with feature engineering and model.

    Args:
        feature_pipe: Feature engineering pipeline
        model: Model object
        model_name: Name of the model

    Returns:
        Pipeline: Complete pipeline
    """
    return Pipeline([("features", feature_pipe), ("model", model)])


def evaluate_model(
    model_pipe, X_train, y_train, X_test, y_test, n_splits=5, random_state=42
):
    """
    Evaluate a model with cross-validation and test set evaluation.

    Args:
        model_pipe: Complete model pipeline
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target
        n_splits: Number of CV splits
        random_state: Random state for reproducibility

    Returns:
        dict: Evaluation metrics and predictions
    """
    # Cross-validation
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    scores = cross_validate(
        model_pipe,
        X_train,
        y_train,
        cv=cv,
        scoring=make_scorers(),
        return_train_score=False,
        n_jobs=1,
    )

    # Calculate CV metrics
    mean_neg_rmse = scores["test_neg_rmse"].mean()
    std_neg_rmse = scores["test_neg_rmse"].std()
    mean_r2 = scores["test_r2"].mean()
    std_r2 = scores["test_r2"].std()

    # Fit on full training set and evaluate on test set
    model_pipe.fit(X_train, y_train)
    y_pred = model_pipe.predict(X_test)

    test_rmse = rmse(y_test, y_pred)
    test_r2 = r2_score(y_test, y_pred)

    return {
        "cv_rmse_mean": -mean_neg_rmse,
        "cv_rmse_std": std_neg_rmse,
        "cv_r2_mean": mean_r2,
        "cv_r2_std": std_r2,
        "test_rmse": test_rmse,
        "test_r2": test_r2,
        "predictions": y_pred,
        "model_pipe": model_pipe,
    }
