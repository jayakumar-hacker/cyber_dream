"""
spatial_encoder.py
====================
Stage 3 of the CyberDreamer pipeline: GNN Encoder.

Defines the interface for the spatial (graph-structured) encoder that
compresses each per-window graph snapshot (from `graph_constructor.py`)
into a fixed-size latent embedding, to be consumed by the RSSM world
model in `world_model.py`.

Intended backbone options (selected via
`configs/default.yaml -> gnn_encoder.architecture`): GAT, GraphSAGE, GCN,
or GIN.

NOTE: This module intentionally contains no layer definitions or forward
logic (no `nn.Module` subclasses, no `GATConv`/`SAGEConv` usage). It only
defines the interface contract that the WS-core implementation must
satisfy.
"""

from __future__ import annotations

from typing import Any, Protocol


class SpatialEncoder(Protocol):
    """
    Interface contract for a graph snapshot encoder.

    Implementations should map a single graph snapshot (PyG `Data` /
    `HeteroData`) to:
      - a per-node embedding tensor, and
      - a single graph-level embedding (via a configured readout/
        aggregation function),
    with dimensionality controlled by
    `configs/default.yaml -> gnn_encoder.output_embedding_dim`.
    """

    def encode_nodes(self, graph_snapshot: Any) -> Any:
        """
        Produce per-node latent embeddings for a single graph snapshot.
        """
        ...

    def encode_graph(self, graph_snapshot: Any) -> Any:
        """
        Produce a single graph-level latent embedding for a snapshot,
        via the configured aggregation/readout strategy
        (`gnn_encoder.aggregation`).
        """
        ...


def build_spatial_encoder(config: dict[str, Any]) -> SpatialEncoder:
    """
    Factory function: construct the configured spatial encoder
    architecture (GAT / GraphSAGE / GCN / GIN) from
    `configs/default.yaml -> gnn_encoder`.

    Left unimplemented — the concrete encoder class(es) and their layer
    definitions belong to the ML research workstream, not this scaffold.
    """
    raise NotImplementedError
