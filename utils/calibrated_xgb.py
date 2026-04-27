"""
utils/calibrated_xgb.py
========================
Serialisable wrapper class for the calibrated XGBoost v3 model.
Must be importable from the same module path at both training and inference time.
"""

import numpy as np


class CalibratedXGB:
    """XGBoost + Platt scaling wrapper. Serialisable via joblib."""

    def __init__(self, base, platt, threshold):
        self.base      = base
        self.platt     = platt
        self.threshold = threshold
        self.classes_  = np.array([0, 1])

    def predict_proba(self, X):
        raw = self.base.predict_proba(X)[:, 1].reshape(-1, 1)
        p1  = self.platt.predict_proba(raw)[:, 1]
        return np.column_stack([1 - p1, p1])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= self.threshold).astype(int)

    @property
    def feature_importances_(self):
        return self.base.feature_importances_
