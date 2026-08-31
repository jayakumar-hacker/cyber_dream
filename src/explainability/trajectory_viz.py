"""
trajectory_viz.py
====================
Stage 7 of the CyberDreamer pipeline: Explainability — latent trajectory
visualization.

Defines the interface for projecting sequences of RSSM belief states
(observed and/or imagined, from `world_model.py` / `rollout_engine.py`)
into a low-dimensional space (e.g. via UMAP) so the demo UI can render
"where the network is heading" as a 2D/3D path.

NOTE: This module intentionally contains no dimensionality-reduction or
plotting logic. It only defines the interface contract.
"""

from __future__ import annotations

from typing import Any


class TrajectoryVisualizer:
    """
    Projects latent belief-state trajectories into a low-dimensional
    space for visualization in the demo UI.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def fit_projection(self, historical_states: Any) -> None:
        """
        Fit a dimensionality-reduction model (e.g. UMAP) on a corpus of
        historical belief states.
        """
        raise NotImplementedError

    def project(self, state_sequence: Any) -> Any:
        """
        Project a sequence of belief states (observed or imagined) into
        the fitted low-dimensional space for plotting.
        """
        raise NotImplementedError

    def to_plotly_figure(self, projected_points: Any) -> Any:
        """
        Package projected points into a Plotly figure object consumable
        by `app/pages/3_Rollout.py` and `app/pages/4_Explain.py`.
        """
        raise NotImplementedError
