"""
utils/shap_explain.py
SHAP-based explainability for individual predictions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def shap_waterfall(model, X_row: pd.DataFrame, feature_names: list, top_n: int = 10):
    """
    Generate a SHAP waterfall-style bar chart for a single prediction.
    Works with tree-based models (RF, XGBoost).
    Falls back to feature importances if SHAP not installed.
    """
    try:
        import shap
        explainer   = shap.TreeExplainer(model)
        shap_vals   = explainer.shap_values(X_row)
        # Binary classification: use class-1 values
        sv = shap_vals[1] if isinstance(shap_vals, list) else shap_vals
        sv = sv[0]  # single row

        df_shap = pd.DataFrame({'feature': feature_names, 'shap': sv})
        df_shap = df_shap.reindex(df_shap['shap'].abs().sort_values(ascending=False).index)
        df_shap = df_shap.head(top_n).sort_values('shap')

        colors = ['#dc2626' if v > 0 else '#16a34a' for v in df_shap['shap']]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(df_shap['feature'], df_shap['shap'], color=colors, edgecolor='none')
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_xlabel('SHAP value (impact on prediction)', fontsize=11)
        ax.set_title(f'Top {top_n} factors driving this prediction', fontsize=12)
        plt.tight_layout()
        return fig

    except ImportError:
        # Fallback: plain feature importances
        if hasattr(model, 'feature_importances_'):
            imp = pd.Series(model.feature_importances_, index=feature_names)
            imp = imp.sort_values(ascending=True).tail(top_n)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(imp.index, imp.values, color='#4f46e5', edgecolor='none')
            ax.set_title(f'Top {top_n} feature importances (install shap for SHAP values)', fontsize=11)
            plt.tight_layout()
            return fig
        return None


def shap_summary_fig(model, X_test: pd.DataFrame, feature_names: list):
    """
    Global SHAP summary bar chart for the model comparison page.
    """
    try:
        import shap
        explainer  = shap.TreeExplainer(model)
        shap_vals  = explainer.shap_values(X_test)
        sv = shap_vals[1] if isinstance(shap_vals, list) else shap_vals

        fig, ax = plt.subplots(figsize=(9, 6))
        shap.summary_plot(sv, X_test, feature_names=feature_names,
                          show=False, plot_type='bar', ax=ax)
        ax.set_title('Global SHAP Feature Importance', fontsize=13)
        plt.tight_layout()
        return fig
    except ImportError:
        return None
