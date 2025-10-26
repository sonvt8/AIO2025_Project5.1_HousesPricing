"""
Custom transformers for house price prediction pipeline.
These transformers handle ordinal encoding, missing value indicators,
rare category pooling, target encoding, and data cleaning.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class OrdinalMapper(BaseEstimator, TransformerMixin):
    """Maps ordinal categorical variables to numeric values based on predefined order"""

    def __init__(self, mapping):
        self.mapping = mapping
        self.maps_ = {}

    def fit(self, X, y=None):
        self.maps_ = {}
        for col, order in self.mapping.items():
            if col in X.columns:
                self.maps_[col] = {v: i for i, v in enumerate(order)}
        return self

    def transform(self, X):
        X = X.copy()
        for col, m in self.maps_.items():
            X[col] = X[col].map(m)
        return X


class MissingnessIndicator(BaseEstimator, TransformerMixin):
    """Creates binary indicators for missing values in numeric columns"""

    def __init__(self, cols=None, auto_numeric=True):
        self.cols = cols
        self.auto_numeric = auto_numeric
        self.cols_ = []

    def fit(self, X, y=None):
        if self.cols is not None:
            self.cols_ = [c for c in self.cols if c in X.columns]
        elif self.auto_numeric:
            num_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
            self.cols_ = [c for c in num_cols if X[c].isna().any()]
        else:
            self.cols_ = []
        return self

    def transform(self, X):
        X = X.copy()
        for c in self.cols_:
            X[f"{c}_was_missing"] = X[c].isna().astype(int)
        return X


class RarePooler(BaseEstimator, TransformerMixin):
    """Pools rare categories into 'Other' category"""

    def __init__(self, cols, min_count=20):
        self.cols = cols
        self.min_count = min_count
        self.keep_levels_ = {}

    def fit(self, X, y=None):
        self.keep_levels_ = {}
        for c in self.cols:
            if c in X.columns:
                vc = X[c].value_counts(dropna=False)
                self.keep_levels_[c] = set(vc[vc >= self.min_count].index.astype(str))
        return self

    def transform(self, X):
        X = X.copy()
        for c, keep in self.keep_levels_.items():
            if c in X.columns:
                X[c] = X[c].astype(str)
                X[c] = np.where(X[c].isin(keep), X[c], "Other")
        return X


class FiniteCleaner(BaseEstimator, TransformerMixin):
    """Converts infinite values to NaN"""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        mask = ~np.isfinite(X)
        if mask.any():
            X[mask] = np.nan
        return X


class DropAllNaNColumns(BaseEstimator, TransformerMixin):
    """Removes columns that are all NaN"""

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.keep_idx_ = np.where(~np.all(np.isnan(X), axis=0))[0]
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        return X[:, self.keep_idx_]


class TargetEncoderTransformer(BaseEstimator, TransformerMixin):
    """Target encoding with smoothing"""

    def __init__(self, cols=None, alpha=20.0):
        self.cols = cols
        self.alpha = float(alpha)
        self.global_mean_ = None
        self.maps_ = {}

    def fit(self, X, y=None):
        if y is None:
            raise ValueError("TargetEncoderTransformer requires y in fit.")
        y = pd.Series(y).astype(float)
        self.global_mean_ = float(y.mean())
        self.maps_ = {}
        if self.cols is None:
            return self

        Xc = X.copy()
        for c in self.cols:
            if c not in Xc.columns:
                continue
            g = Xc[c].astype(str).groupby(Xc[c].astype(str))
            stats = g.size().to_frame("cnt")
            stats["sumy"] = y.groupby(Xc[c].astype(str)).sum()
            stats["te"] = (stats["sumy"] + self.alpha * self.global_mean_) / (
                stats["cnt"] + self.alpha
            )
            self.maps_[c] = stats["te"].to_dict()
        return self

    def transform(self, X):
        X = X.copy()
        for c, m in self.maps_.items():
            if c in X.columns:
                X[f"TE_{c}"] = (
                    X[c].astype(str).map(m).fillna(self.global_mean_).astype(float)
                )
        return X
