"""
attention.py
=============
Stage 7 of the CyberDreamer pipeline: Explainability — attention-based
attribution.

Defines the interface for extracting and summarizing GNN attention
weights (from `spatial_encoder.py`, when the configured architecture is
attention-based, e.g. GAT) to identify which nodes/edges most influenced
a given prediction.

Configuration surface: `configs/default.yaml -> explainability`
(top_k_contributing_nodes, top_k_contributing_edges, etc.)

NOTE: This module intentionally contains no attention-extraction or
scoring logic. It only defines the interface contract.
"""

from __future__ import annotations

from typing import Any


class AttentionExplainer:
    """
    Extracts and ranks attention-derived node/edge contributions for a
    given graph snapshot and prediction.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def extract_attention_weights(self, encoder: Any, graph_snapshot: Any) -> Any:
        """
        Pull raw attention weights out of the spatial encoder's forward
        pass for a given snapshot.
        """
        raise NotImplementedError

    def top_k_nodes(self, attention_weights: Any, k: int) -> Any:
        """
        Rank and return the top-k contributing nodes by aggregated
        attention weight.
        """
        raise NotImplementedError

    def top_k_edges(self, attention_weights: Any, k: int) -> Any:
        """
        Rank and return the top-k contributing edges by attention
        weight.
        """
        raise NotImplementedError
