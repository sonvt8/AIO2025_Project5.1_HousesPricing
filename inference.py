"""
Simplified inference script for house price prediction.
Auto-aligns input schema using fixed RAW_SCHEMA_FALLBACK.
"""

import sys
import os
import pandas as pd
import joblib
import numpy as np

PIPELINE_PATH = "src/models/best_pipeline.joblib"

# Fixed schema (from training header, excluding SalePrice)
RAW_SCHEMA_FALLBACK = [
    "Id","MSSubClass","MSZoning","LotFrontage","LotArea","Street","Alley","LotShape",
    "LandContour","Utilities","LotConfig","LandSlope","Neighborhood","Condition1",
    "Condition2","BldgType","HouseStyle","OverallQual","OverallCond","YearBuilt",
    "YearRemodAdd","RoofStyle","RoofMatl","Exterior1st","Exterior2nd","MasVnrType",
    "MasVnrArea","ExterQual","ExterCond","Foundation","BsmtQual","BsmtCond",
    "BsmtExposure","BsmtFinType1","BsmtFinSF1","BsmtFinType2","BsmtFinSF2",
    "BsmtUnfSF","TotalBsmtSF","Heating","HeatingQC","CentralAir","Electrical",
    "1stFlrSF","2ndFlrSF","LowQualFinSF","GrLivArea","BsmtFullBath","BsmtHalfBath",
    "FullBath","HalfBath","BedroomAbvGr","KitchenAbvGr","KitchenQual","TotRmsAbvGrd",
    "Functional","Fireplaces","FireplaceQu","GarageType","GarageYrBlt","GarageFinish",
    "GarageCars","GarageArea","GarageQual","GarageCond","PavedDrive","WoodDeckSF",
    "OpenPorchSF","EnclosedPorch","3SsnPorch","ScreenPorch","PoolArea","PoolQC",
    "Fence","MiscFeature","MiscVal","MoSold","YrSold","SaleType","SaleCondition"
]


def load_pipeline():
    if not os.path.exists(PIPELINE_PATH):
        print(f"❌ Error: Pipeline not found at {PIPELINE_PATH}")
        sys.exit(1)
    print(f"📦 Loading pipeline from {PIPELINE_PATH}...")
    pipe = joblib.load(PIPELINE_PATH)
    print("   ✅ Pipeline loaded successfully")
    return pipe


def align_and_cast(df: pd.DataFrame) -> pd.DataFrame:
    """Reindex to RAW_SCHEMA_FALLBACK and cast dtypes."""
    expected = set(RAW_SCHEMA_FALLBACK)
    incoming = set(df.columns)

    missing = sorted(expected - incoming)
    extra = sorted(incoming - expected)

    if missing:
        print(f"⚠️  Missing columns: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
    if extra:
        print(f"⚠️  Extra columns ignored: {extra[:10]}{' ...' if len(extra) > 10 else ''}")

    df = df.reindex(columns=RAW_SCHEMA_FALLBACK)

    # Drop target if accidentally present
    if "SalePrice" in df.columns:
        df = df.drop(columns=["SalePrice"])

    # Light type casting
    for col in df.columns:
        if col == "MSSubClass":
            df[col] = df[col].astype("string")
        elif df[col].dtype == object:
            df[col] = df[col].astype("string")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def predict(input_data, output_path=None):
    """Make predictions on new data."""
    pipe = load_pipeline()

    if isinstance(input_data, str):
        print(f"📊 Loading data from {input_data}...")
        df = pd.read_csv(input_data)
    else:
        df = input_data.copy()

    print(f"   Raw data shape: {df.shape}")

    df = align_and_cast(df)
    print(f"   Aligned data shape: {df.shape}")

    print("🔮 Making predictions...")
    preds = pipe.predict(df)

    print("\n✅ Predictions completed!")
    print(f"   Count: {len(preds)}")
    print(f"   Min: ${preds.min():,.2f}")
    print(f"   Max: ${preds.max():,.2f}")
    print(f"   Mean: ${preds.mean():,.2f}")
    print(f"   Median: ${np.median(preds):,.2f}")

    if output_path:
        pd.DataFrame({"predicted_price": preds}).to_csv(output_path, index=False)
        print(f"\n💾 Predictions saved to {output_path}")

    return preds


def main():
    import argparse
    parser = argparse.ArgumentParser(description="House Price Prediction Inference")
    parser.add_argument("input", type=str, help="Path to input CSV")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save predictions CSV")
    args = parser.parse_args()

    print("=" * 60)
    print("🏠 House Price Prediction - Inference")
    print("=" * 60)

    if not os.path.exists(args.input):
        print(f"❌ Input file not found at {args.input}")
        sys.exit(1)

    try:
        predict(args.input, output_path=args.output)
        print("\n" + "=" * 60)
        print("✅ Inference completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Inference failed: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
