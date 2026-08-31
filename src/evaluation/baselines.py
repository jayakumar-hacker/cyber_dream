"""
baselines.py
==============
Stage 8 of the CyberDreamer pipeline: Evaluation — baseline models.

Defines the interface for simple, non-graph baseline predictors used as
comparison points against the full CyberDreamer model in ablation
studies:

  - LogisticRegressionBaseline: flat-feature logistic regression over
    the windowed feature table (no graph structure, no temporal model).
  - LstmOnlyBaseline: a sequence-only model (no graph structure) that
    consumes windowed features as a plain time series.

Configuration surface: `configs/default.yaml -> evaluation`.

NOTE: This module intentionally contains no model implementation logic
(no sklearn `.fit()` calls, no `nn.LSTM` definitions). It only defines
the interface contract that WS-evaluation must satisfy.
"""

from __future__ import annotations

from typing import Any, Protocol


class Baseline(Protocol):
    """
    Generic interface for a baseline predictor used in ablation
    benchmarking against the full CyberDreamer model.
    """

    def fit(self, train_data: Any) -> None:
        """Fit the baseline on training data."""
        ...

    def predict(self, eval_data: Any) -> Any:
        """Produce predictions on evaluation data."""
        ...


class LogisticRegressionBaseline(Baseline):
    """
    Placeholder for a flat-feature logistic regression baseline (no
    graph structure, no temporal modeling).
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def fit(self, train_data: Any) -> None:
        raise NotImplementedError

    def predict(self, eval_data: Any) -> Any:
        raise NotImplementedError


class LstmOnlyBaseline(Baseline):
    """
    Placeholder for a sequence-only baseline (temporal modeling via
    LSTM, but no graph structure / GNN encoder).
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def fit(self, train_data: Any) -> None:
        raise NotImplementedError

    def predict(self, eval_data: Any) -> Any:
        raise NotImplementedError
