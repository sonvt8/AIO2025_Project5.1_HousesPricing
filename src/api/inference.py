"""
Inference module for house price prediction.
Contains core prediction logic that can be used by API or CLI.
"""

import sys
import os
import pandas as pd
import joblib
import numpy as np


def load_pipeline(pipeline_path="src/models/best_pipeline.joblib", verbose=False):
    """Load trained pipeline from disk."""
    if not os.path.exists(pipeline_path):
        if verbose:
            print(f"❌ Error: Pipeline not found at {pipeline_path}")
            print("   Please run train.py first to train the model.")
        raise FileNotFoundError(
            f"Pipeline not found at {pipeline_path}. Please run train.py first."
        )

    if verbose:
        print(f"📦 Loading pipeline from {pipeline_path}...")

    pipeline = joblib.load(pipeline_path)

    if verbose:
        print("   ✅ Pipeline loaded successfully")

    return pipeline


def predict(
    input_data,
    pipeline_path="src/models/best_pipeline.joblib",
    output_path=None,
    verbose=False,
):
    """
    Make predictions on new data.

    Args:
        input_data: Path to CSV file or pandas DataFrame
        pipeline_path: Path to trained pipeline
        output_path: Path to save predictions (optional)
        verbose: Whether to print progress messages

    Returns:
        numpy array: Predictions
    """
    # Load pipeline
    pipeline = load_pipeline(pipeline_path, verbose=verbose)

    # Load input data
    if isinstance(input_data, str):
        if verbose:
            print(f"📊 Loading data from {input_data}...")
        df = pd.read_csv(input_data)
    else:
        df = input_data.copy()

    if verbose:
        print(f"   Data shape: {df.shape}")
        print("🔮 Making predictions...")

    # Make predictions
    predictions = pipeline.predict(df)

    if verbose:
        print("\n✅ Predictions completed!")
        print(f"   Number of predictions: {len(predictions)}")
        print(f"   Min price: ${predictions.min():,.2f}")
        print(f"   Max price: ${predictions.max():,.2f}")
        print(f"   Mean price: ${predictions.mean():,.2f}")
        print(f"   Median price: ${np.median(predictions):,.2f}")

    # Save to file if output path provided
    if output_path:
        result_df = pd.DataFrame({"predicted_price": predictions})
        result_df.to_csv(output_path, index=False)
        if verbose:
            print(f"\n💾 Predictions saved to {output_path}")

    return predictions


def predict_single(features: dict, pipeline_path="src/models/best_pipeline.joblib"):
    """
    Predict price for a single house.

    Args:
        features: Dictionary of house features
        pipeline_path: Path to trained pipeline

    Returns:
        float: Predicted price
    """
    # Convert dict to DataFrame
    df = pd.DataFrame([features])

    # Load pipeline and predict
    pipeline = load_pipeline(pipeline_path)
    prediction = pipeline.predict(df)[0]

    return float(prediction)


if __name__ == "__main__":
    """CLI interface for inference."""
    import argparse

    parser = argparse.ArgumentParser(description="Make predictions on house price data")
    parser.add_argument("input", type=str, help="Path to input CSV file")
    parser.add_argument(
        "--pipeline",
        type=str,
        default="src/models/best_pipeline.joblib",
        help="Path to trained pipeline",
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Path to save predictions CSV"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🏠 House Price Prediction - Inference")
    print("=" * 60)

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found at {args.input}")
        sys.exit(1)

    try:
        predictions = predict(
            input_data=args.input,
            pipeline_path=args.pipeline,
            output_path=args.output,
            verbose=True,
        )

        print("\n" + "=" * 60)
        print("✅ Inference completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Inference failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
