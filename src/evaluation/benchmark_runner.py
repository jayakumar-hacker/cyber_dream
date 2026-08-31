"""
benchmark_runner.py
======================
Stage 8 of the CyberDreamer pipeline: Evaluation — benchmarking & ablation
orchestration.

Defines the interface for running the full CyberDreamer model alongside
the baselines in `baselines.py` on a shared evaluation split, computing
the metrics defined in `configs/default.yaml -> evaluation.metrics`, and
producing an ablation comparison table.

NOTE: This module intentionally contains no metric computation or model
invocation logic. It only defines the interface contract that
WS-evaluation must satisfy.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class BenchmarkRunner:
    """
    Orchestrates running the full model and configured baselines on a
    shared test split and assembling an ablation results table.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Args:
            config: The `evaluation` section of the loaded config
                (metrics, test_split_path, num_eval_rollouts, etc.).
        """
        self.config = config

    def load_test_split(self, test_split_path: Path) -> Any:
        """
        Load the held-out test split referenced in
        `evaluation.test_split_path`.
        """
        raise NotImplementedError

    def evaluate_model(self, model: Any, test_data: Any) -> dict[str, float]:
        """
        Compute all configured metrics (`evaluation.metrics`) for a
        single model (full CyberDreamer model or a baseline) on the
        test split.
        """
        raise NotImplementedError

    def run_ablation(self, models: dict[str, Any], test_data: Any) -> Any:
        """
        Evaluate every model in `models` (name -> model instance) and
        assemble a comparison table.

        Returns:
            An implementation-defined tabular results object (e.g. a
            pandas DataFrame) with one row per model, one column per
            metric.
        """
        raise NotImplementedError

    def save_results(self, results_table: Any, output_path: Path) -> Path:
        """
        Persist the ablation results table under `experiments/`.
        """
        raise NotImplementedError
