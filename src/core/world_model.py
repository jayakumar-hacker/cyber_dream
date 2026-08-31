"""
world_model.py
================
Stage 4 of the CyberDreamer pipeline: RSSM Core (the "world model").

Defines the interface for the Recurrent State-Space Model that fuses the
sequence of per-window graph embeddings (from `spatial_encoder.py`) into
a recurrent latent belief state describing the network's evolving
condition over time. This belief state is what `prediction_heads.py`
reads from, and what `rollout_engine.py` recursively advances during
imagination.

Configuration surface: `configs/default.yaml -> rssm_core`
(deterministic_state_dim, stochastic_state_dim, kl_balance_alpha, etc.)

NOTE: This module intentionally contains no recurrent cell definitions or
forward logic (no `nn.GRU`/`nn.LSTM`/custom cell implementations). It
only defines the interface contract that the WS-core implementation must
satisfy.
"""

from __future__ import annotations

from typing import Any, Protocol


class WorldModel(Protocol):
    """
    Interface contract for the RSSM latent dynamics model.

    A world model maintains a belief state composed of a deterministic
    component (recurrent hidden state) and a stochastic component
    (sampled latent), updated at every observed time window and
    extendable via `imagine_step` for future (unobserved) steps.
    """

    def initial_state(self, batch_size: int) -> Any:
        """
        Return a zero/prior belief state to seed a new sequence.
        """
        ...

    def observe_step(self, prev_state: Any, graph_embedding: Any) -> Any:
        """
        Update the belief state given the previous state and the current
        observed graph embedding (posterior update).
        """
        ...

    def imagine_step(self, prev_state: Any) -> Any:
        """
        Advance the belief state one step *without* a new observation,
        sampling from the learned prior transition dynamics (used by
        Stage 6 imagination rollouts).
        """
        ...

    def get_features(self, state: Any) -> Any:
        """
        Flatten/concatenate a belief state into a single feature vector
        suitable for consumption by prediction heads.
        """
        ...


def build_world_model(config: dict[str, Any]) -> WorldModel:
    """
    Factory function: construct the configured RSSM instance from
    `configs/default.yaml -> rssm_core`.

    Left unimplemented — the concrete recurrent/stochastic transition
    logic belongs to the ML research workstream, not this scaffold.
    """
    raise NotImplementedError
