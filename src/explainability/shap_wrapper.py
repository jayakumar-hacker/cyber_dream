"""
shap_wrapper.py
=================
Stage 7 of the CyberDreamer pipeline: Explainability — SHAP-based
attribution over prediction heads.

Defines the interface for wrapping `prediction_heads.py` outputs with a
SHAP explainer (e.g. `shap.DeepExplainer` / `shap.GradientExplainer`) to
produce per-feature attribution scores for a given prediction.

Configuration surface: `configs/default.yaml -> explainability`.

NOTE: This module intentionally contains no SHAP invocation or
background-sample logic. It only defines the interface contract.
"""

from __future__ import annotations

from typing import Any


class ShapExplainer:
    """
    Wraps a prediction head with a SHAP explainer to produce per-feature
    attribution scores.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def fit_background(self, background_samples: Any) -> None:
        """
        Fit/cache the background distribution SHAP uses as its
        reference point for attribution.
        """
        raise NotImplementedError

    def explain(self, head: Any, state_features: Any) -> Any:
        """
        Produce SHAP attribution values for a single prediction made by
        `head` on `state_features`.
        """
        raise NotImplementedError

    def save_explanation(self, explanation: Any, output_path: Any) -> Any:
        """
        Persist an explanation to
        `explainability.explanation_output_path`.
        """
        raise NotImplementedError
