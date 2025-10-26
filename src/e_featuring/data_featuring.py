"""
Feature engineering functions for house price prediction.
Handles domain-specific feature engineering and creates the complete feature space pipeline.
"""

import numpy as np
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline

from ..processing.data_processing import build_feature_lists, make_preprocessor


def add_domain_features(df):
    """Add domain-specific features for real estate data"""
    df = df.copy()

    # Total square footage
    for c in ["TotalBsmtSF", "1stFlrSF", "2ndFlrSF"]:
        if c not in df.columns:
            df[c] = 0
    df["TotalSF"] = (
        df["TotalBsmtSF"].fillna(0)
        + df["1stFlrSF"].fillna(0)
        + df["2ndFlrSF"].fillna(0)
    )

    # Total bathrooms
    for c in ["FullBath", "HalfBath", "BsmtFullBath", "BsmtHalfBath"]:
        if c not in df.columns:
            df[c] = 0
    df["TotalBath"] = (
        df["FullBath"].fillna(0)
        + 0.5 * df["HalfBath"].fillna(0)
        + df["BsmtFullBath"].fillna(0)
        + 0.5 * df["BsmtHalfBath"].fillna(0)
    )

    # Age features
    for c in ["YrSold", "YearBuilt", "YearRemodAdd", "GarageYrBlt"]:
        if c not in df.columns:
            df[c] = np.nan
    df["HouseAge"] = (df["YrSold"] - df["YearBuilt"]).astype(float)
    df["RemodAge"] = (df["YrSold"] - df["YearRemodAdd"]).astype(float)
    df["GarageAge"] = (df["YrSold"] - df["GarageYrBlt"]).astype(float)

    # Binary features
    df["IsRemodeled"] = (
        df.get("YearRemodAdd", df["YearBuilt"]) != df["YearBuilt"]
    ).astype(int)
    df["Has2ndFlr"] = (df["2ndFlrSF"] > 0).astype(int)

    # Total porch area
    for c in ["OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch", "WoodDeckSF"]:
        if c not in df.columns:
            df[c] = 0
    df["TotalPorchSF"] = (
        df["OpenPorchSF"]
        + df["EnclosedPorch"]
        + df["3SsnPorch"]
        + df["ScreenPorch"]
        + df["WoodDeckSF"]
    )

    # Ratio features
    df["BathPerBedroom"] = df.get("TotalBath", 0) / np.maximum(
        df.get("BedroomAbvGr", 1), 1
    )
    df["RoomsPerArea"] = df.get("TotRmsAbvGrd", 0) / np.maximum(
        df.get("GrLivArea", 1), 1
    )
    df["LotAreaRatio"] = df.get("LotArea", 0) / np.maximum(df.get("GrLivArea", 1), 1)

    # Seasonal features
    if "MoSold" in df.columns:
        df["MoSold_sin"] = np.sin(2 * np.pi * (df["MoSold"].astype(float) / 12.0))
        df["MoSold_cos"] = np.cos(2 * np.pi * (df["MoSold"].astype(float) / 12.0))

    # Interaction features
    if ("Neighborhood" in df.columns) and ("BldgType" in df.columns):
        df["Neighborhood_BldgType"] = (
            df["Neighborhood"].astype(str) + "|" + df["BldgType"].astype(str)
        )

    # Log transformation
    df["Ln_TotalSF"] = np.log1p(df.get("TotalSF", 0).astype(float))

    # Quality-area interactions
    if "OverallQual" in df.columns:
        df["IQ_OQ_GrLiv"] = df["OverallQual"].astype(float) * df.get(
            "GrLivArea", 0
        ).astype(float)
        df["IQ_OQ_TotalSF"] = df["OverallQual"].astype(float) * df.get(
            "TotalSF", 0
        ).astype(float)

    # Winsorization for heavy tails
    if "LotArea" in df.columns:
        q_hi = df["LotArea"].quantile(0.99)
        df["LotArea_clip"] = np.minimum(df["LotArea"], q_hi)

    return df


def make_feature_space(
    df_train, df_test=None, te_cols=None, te_alpha=30.0, rare_min_count=15
):
    """Create the complete feature engineering pipeline"""
    if df_test is None:
        df_test = df_train

    df_train_aug = add_domain_features(df_train.copy())
    df_test_aug = add_domain_features(df_test.copy())
    cat_cols, ord_cols, num_cont, num_abs = build_feature_lists(
        df_train_aug, df_test_aug
    )

    # Default target encoder columns if not provided
    if te_cols is None:
        te_cols = [
            "Neighborhood",
            "MSZoning",
            "Exterior1st",
            "Exterior2nd",
            "SaleCondition",
            "BldgType",
            "Neighborhood_BldgType",
        ]

    return Pipeline(
        [
            ("add_domain", FunctionTransformer(add_domain_features)),
            (
                "preproc",
                make_preprocessor(
                    cat_cols,
                    ord_cols,
                    num_cont,
                    num_abs,
                    te_cols,
                    te_alpha,
                    rare_min_count,
                ),
            ),
        ]
    )
