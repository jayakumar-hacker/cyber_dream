"""
prediction_heads.py
======================
Stage 5 of the CyberDreamer pipeline: Prediction Heads.

Defines the interface for task-specific heads that read the RSSM belief
state (from `world_model.py`) and produce concrete predictions:

  - RiskScoreHead: a continuous anomaly/risk score for the current
    window.
  - MitreStageClassifierHead: a categorical prediction of the current
    (or imagined) MITRE ATT&CK-aligned kill-chain stage.

Configuration surface: `configs/default.yaml -> prediction_heads`.

NOTE: This module intentionally contains no layer definitions or forward
logic (no `nn.Linear`, no loss computation). It only defines the
interface contract that the WS-core implementation must satisfy.
"""

from __future__ import annotations

from typing import Any, Protocol


class PredictionHead(Protocol):
    """
    Generic interface for a head that maps RSSM belief-state features to
    a task-specific prediction.
    """

    def predict(self, state_features: Any) -> Any:
        """
        Produce this head's prediction given RSSM state features
        (as returned by `WorldModel.get_features`).
        """
        ...


class RiskScoreHead(PredictionHead):
    """
    Placeholder for a regression head producing a continuous
    anomaly/risk score in [0, 1] (or unbounded, depending on final
    design) for the current window or an imagined future window.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def predict(self, state_features: Any) -> Any:
        raise NotImplementedError


class MitreStageClassifierHead(PredictionHead):
    """
    Placeholder for a classification head over MITRE ATT&CK-aligned
    kill-chain stages (num_classes defined in
    `configs/default.yaml -> prediction_heads`).
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def predict(self, state_features: Any) -> Any:
        raise NotImplementedError


def build_prediction_heads(config: dict[str, Any]) -> dict[str, PredictionHead]:
    """
    Factory function: construct all configured prediction heads from
    `configs/default.yaml -> prediction_heads.heads`.

    Left unimplemented — concrete head architectures belong to the ML
    research workstream, not this scaffold.
    """
    raise NotImplementedError
