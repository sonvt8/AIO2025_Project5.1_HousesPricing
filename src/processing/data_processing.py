"""
Data processing pipeline for house price prediction.
Handles ordinal mapping, feature lists building, and preprocessing pipeline creation.
"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    OneHotEncoder,
    QuantileTransformer,
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from .transformers import (
    OrdinalMapper,
    MissingnessIndicator,
    RarePooler,
    TargetEncoderTransformer,
    FiniteCleaner,
    DropAllNaNColumns,
)


# Canonical ordinal mapping for Ames Housing dataset
ORDINAL_MAP_CANONICAL = {
    "ExterQual": ["Po", "Fa", "TA", "Gd", "Ex"],
    "ExterCond": ["Po", "Fa", "TA", "Gd", "Ex"],
    "BsmtQual": ["NA", "Po", "Fa", "TA", "Gd", "Ex"],
    "BsmtCond": ["NA", "Po", "Fa", "TA", "Gd", "Ex"],
    "BsmtExposure": ["NA", "No", "Mn", "Av", "Gd"],
    "BsmtFinType1": ["NA", "Unf", "LwQ", "Rec", "BLQ", "ALQ", "GLQ"],
    "BsmtFinType2": ["NA", "Unf", "LwQ", "Rec", "BLQ", "ALQ", "GLQ"],
    "HeatingQC": ["Po", "Fa", "TA", "Gd", "Ex"],
    "KitchenQual": ["Po", "Fa", "TA", "Gd", "Ex"],
    "FireplaceQu": ["NA", "Po", "Fa", "TA", "Gd", "Ex"],
    "GarageFinish": ["NA", "Unf", "RFn", "Fin"],
    "GarageQual": ["NA", "Po", "Fa", "TA", "Gd", "Ex"],
    "GarageCond": ["NA", "Po", "Fa", "TA", "Gd", "Ex"],
    "PoolQC": ["NA", "Fa", "TA", "Gd", "Ex"],
    "Fence": ["NA", "MnWw", "GdWo", "MnPrv", "GdPrv"],
    "Functional": ["Sal", "Sev", "Maj2", "Maj1", "Mod", "Min2", "Min1", "Typ"],
    "PavedDrive": ["N", "P", "Y"],
    "Street": ["Grvl", "Pave"],
    "Alley": ["NA", "Grvl", "Pave"],
    "CentralAir": ["N", "Y"],
}


def build_feature_lists(df_train, df_test):
    """
    Build feature lists for different preprocessing pipelines.

    Args:
        df_train: Training dataframe
        df_test: Test dataframe

    Returns:
        tuple: (cat_cols, ord_cols, num_cont, num_abs_candidates)
    """
    for df in (df_train, df_test):
        if "MSSubClass" in df.columns:
            df["MSSubClass"] = df["MSSubClass"].astype(str)

    all_cols = df_train.drop(columns=["SalePrice"], errors="ignore").columns

    ord_cols = [c for c in ORDINAL_MAP_CANONICAL.keys() if c in all_cols]
    cat_cols = [
        c for c in all_cols if (df_train[c].dtype == "object") and (c not in ord_cols)
    ]
    num_cols = [
        c
        for c in all_cols
        if pd.api.types.is_numeric_dtype(df_train[c]) and c not in ord_cols
    ]

    num_abs_candidates = []
    for c in num_cols:
        if df_train[c].isna().any() or df_test[c].isna().any():
            num_abs_candidates.append(c)

    num_cont = [c for c in num_cols if c not in num_abs_candidates]
    return cat_cols, ord_cols, num_cont, num_abs_candidates


def make_preprocessor(
    cat_cols, ord_cols, num_cont, num_absence, te_cols, te_alpha=30.0, rare_min_count=15
):
    """
    Create the preprocessing pipeline.

    Args:
        cat_cols: Categorical columns list
        ord_cols: Ordinal columns list
        num_cont: Continuous numeric columns list
        num_absence: Numeric columns with missing values list
        te_cols: Target encoder columns list
        te_alpha: Target encoder smoothing parameter
        rare_min_count: Minimum count for rare category pooling

    Returns:
        Pipeline: Complete preprocessing pipeline
    """
    pre_steps = [
        ("ordinal_map", OrdinalMapper(ORDINAL_MAP_CANONICAL)),
        ("missing_flags", MissingnessIndicator(cols=None, auto_numeric=True)),
        ("rare_pool", RarePooler(cat_cols, min_count=rare_min_count)),
        (
            "te",
            TargetEncoderTransformer(
                cols=[c for c in te_cols if c in cat_cols], alpha=te_alpha
            ),
        ),
    ]
    pre = Pipeline(steps=pre_steps)

    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    cat_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("ohe", ohe),
        ]
    )

    ord_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
        ]
    )

    num_cont_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            (
                "qntl",
                QuantileTransformer(
                    output_distribution="normal",
                    n_quantiles=200,
                    subsample=200000,
                    copy=True,
                ),
            ),
        ]
    )

    num_abs_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
        ]
    )

    ct = ColumnTransformer(
        transformers=[
            ("cats", cat_pipe, cat_cols),
            ("ords", ord_pipe, ord_cols),
            ("num_cont", num_cont_pipe, num_cont),
            ("num_abs", num_abs_pipe, num_absence),
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    return Pipeline(
        [
            ("prep", pre),
            ("ct", ct),
            ("finite", FiniteCleaner()),
            ("dropnan", DropAllNaNColumns()),
        ]
    )
