"""
rollout_engine.py
====================
Stage 6 of the CyberDreamer pipeline: Imagination Rollout & Counterfactuals.

Defines the interface for recursively advancing the RSSM world model's
*prior* dynamics (`WorldModel.imagine_step`) for K steps into the future,
without new real observations, to produce a distribution over plausible
near-future network states ("imagined trajectories").

Also hosts the interface for counterfactual rollouts (e.g. "what if this
host were isolated at step t?") used by the explainability stage.

Configuration surface: `configs/default.yaml -> imagination_rollout`
(k_rollout_steps, num_rollout_trajectories, rollout_policy, etc.)

NOTE: This module intentionally contains no rollout math or sampling
logic. It only defines the interface contract that the WS-core
implementation must satisfy.
"""

from __future__ import annotations

from typing import Any, Protocol


class RolloutEngine(Protocol):
    """
    Interface contract for K-step latent imagination.
    """

    def rollout(self, initial_state: Any, k_steps: int, num_trajectories: int) -> Any:
        """
        Produce `num_trajectories` imagined latent trajectories of
        length `k_steps`, starting from `initial_state`, by repeatedly
        calling `WorldModel.imagine_step`.

        Returns:
            An implementation-defined batch of imagined state
            sequences (e.g. shape [num_trajectories, k_steps, ...]).
        """
        ...

    def counterfactual_rollout(
        self, initial_state: Any, intervention: dict[str, Any], k_steps: int
    ) -> Any:
        """
        Produce an imagined trajectory under a specified structural
        intervention (e.g. removing/isolating a node) applied at the
        start of the rollout, for "what-if" analysis.

        Args:
            initial_state: The RSSM belief state to branch from.
            intervention: Description of the counterfactual change to
                apply (implementation-defined schema, e.g.
                {"remove_node_id": "...", "at_step": 0}).
            k_steps: Number of steps to imagine forward.
        """
        ...


def build_rollout_engine(world_model: Any, config: dict[str, Any]) -> RolloutEngine:
    """
    Factory function: construct the configured rollout engine, bound to
    a given `WorldModel` instance, from
    `configs/default.yaml -> imagination_rollout`.

    Left unimplemented — concrete rollout/sampling logic belongs to the
    ML research workstream, not this scaffold.
    """
    raise NotImplementedError
