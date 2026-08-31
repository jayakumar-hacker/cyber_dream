"""
config_loader.py
==================
Utility for loading `configs/default.yaml` (and optional experiment
override files) into a plain nested dict.

This is infrastructure/plumbing code, not a model component, so it is
fully implemented (unlike the pipeline/core/heads/simulator/
explainability/evaluation stubs, which are left for the research
workstreams to fill in).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path, overrides: str | Path | None = None) -> dict[str, Any]:
    """
    Load the base config YAML and optionally merge an experiment
    override YAML on top of it (shallow-then-deep dict merge).

    Args:
        config_path: Path to the base config, e.g. `configs/default.yaml`.
        overrides: Optional path to an experiment-specific override
            YAML, e.g. `configs/experiments/exp_001.yaml`.

    Returns:
        The merged configuration as a nested dict.
    """
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f) or {}

    if overrides is not None:
        overrides_path = Path(overrides)
        with overrides_path.open("r", encoding="utf-8") as f:
            override_config: dict[str, Any] = yaml.safe_load(f) or {}
        config = _deep_merge(config, override_config)

    return config


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge `override` into `base`, returning a new dict."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
