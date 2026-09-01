"""
tests/test_pipeline.py
=======================
Tests for Stage 1 (feature_fusion.py) of the CyberDream pipeline.

Uses synthetic CTU-13-style netflow data (argus column naming:
StartTime, Dur, Proto, SrcAddr, Sport, DstAddr, Dport, State, sTos,
dTos, TotPkts, TotBytes, Label) and the project's real
configs/default.yaml, so this also validates the config schema itself.

Run with:  pytest tests/test_pipeline.py -v
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from src.pipeline.feature_fusion import FeatureFusionEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"


def _make_ctu13_sample(n: int = 400, seed: int = 42) -> pd.DataFrame:
    """Synthetic CTU-13-style netflow rows, one every 2 seconds."""
    rng = np.random.default_rng(seed)
    start = datetime(2024, 1, 1)

    return pd.DataFrame({
        "StartTime": [start + timedelta(seconds=i * 2) for i in range(n)],
        "Dur": rng.exponential(2.0, n),
        "Proto": rng.choice(["tcp", "udp"], n),
        "SrcAddr": rng.choice(["10.0.0.1", "10.0.0.2", "10.0.0.3"], n),
        "Sport": rng.choice([1024, 2048, 4096], n).astype(str),
        "DstAddr": rng.choice(["10.0.0.9", "10.0.0.10"], n),
        "Dport": rng.choice([80, 443, 22, 53], n).astype(str),
        "State": rng.choice(["CON", "FIN", "REQ"], n),
        "sTos": rng.choice([0, 1], n),
        "dTos": rng.choice([0, 1], n),
        "TotPkts": rng.integers(1, 200, n),
        "TotBytes": rng.integers(64, 20000, n),
        "Label": rng.choice(["Background", "Botnet"], n, p=[0.9, 0.1]),
    })


@pytest.fixture
def config(tmp_path: Path) -> dict:
    """Real feature_pipeline config, repointed at a temp raw_path/output dir."""
    with open(CONFIG_PATH) as f:
        full_config = yaml.safe_load(f)

    fp_config = full_config["feature_pipeline"]

    raw_dir = tmp_path / "raw" / "CTU-13"
    raw_dir.mkdir(parents=True)
    _make_ctu13_sample().to_csv(raw_dir / "ctu13_sample.csv", index=False)

    fp_config["datasets"] = [{"name": "CTU-13", "raw_path": str(raw_dir)}]
    fp_config["processed_output_path"] = str(tmp_path / "processed")
    fp_config["normalization"]["per_feature_stats_path"] = str(
        tmp_path / "processed" / "feature_stats.json"
    )

    return fp_config


def test_default_yaml_has_required_keys():
    with open(CONFIG_PATH) as f:
        full_config = yaml.safe_load(f)

    fp = full_config["feature_pipeline"]
    for key in ("window_size", "stride", "datasets", "normalization", "label_column"):
        assert key in fp, f"feature_pipeline.{key} missing from default.yaml"
    assert fp["normalization"]["method"] == "z_score"


def test_pipeline_runs_end_to_end(config):
    engine = FeatureFusionEngine(config)
    output_path = engine.run()

    assert output_path.exists()
    result = pd.read_parquet(output_path)
    assert len(result) > 0


def test_sliding_window_creates_overlap(config):
    """window_size (60) > stride (10) -> each record should appear in
    multiple windows, not just one (the bug in the original script)."""
    engine = FeatureFusionEngine(config)
    output_path = engine.run()
    result = pd.read_parquet(output_path)

    n_raw_rows = 400  # from _make_ctu13_sample
    assert len(result) > n_raw_rows, (
        "Expected overlapping sliding windows to multiply row count; "
        "got no overlap -- window_size is probably being ignored."
    )

    # Windows are 60s wide, spaced 10s apart -> ~6x overlap expected.
    ratio = len(result) / n_raw_rows
    assert 4 <= ratio <= 6.5


def test_categorical_columns_not_normalized(config):
    engine = FeatureFusionEngine(config)
    output_path = engine.run()
    result = pd.read_parquet(output_path)

    # Sport/Dport were written as strings in the fixture and shouldn't be
    # touched either way, but Proto/State should retain original values.
    assert set(result["Proto"].unique()) <= {"tcp", "udp"}
    assert set(result["State"].unique()) <= {"CON", "FIN", "REQ"}


def test_continuous_columns_are_normalized(config):
    engine = FeatureFusionEngine(config)
    output_path = engine.run()
    result = pd.read_parquet(output_path)

    # Dur/TotPkts/TotBytes are continuous -> should look z-scored (mean ~0).
    for col in ("Dur", "TotPkts", "TotBytes"):
        assert abs(result[col].mean()) < 0.5, f"{col} does not look normalized"


def test_entity_ids_extracted_from_ctu13_columns(config):
    engine = FeatureFusionEngine(config)
    output_path = engine.run()
    result = pd.read_parquet(output_path)

    assert set(result["entity_id"].unique()) == {"10.0.0.1", "10.0.0.2", "10.0.0.3"}
    assert set(result["dst_entity_id"].unique()) == {"10.0.0.9", "10.0.0.10"}


def test_label_column_untouched(config):
    engine = FeatureFusionEngine(config)
    output_path = engine.run()
    result = pd.read_parquet(output_path)

    assert set(result["Label"].unique()) == {"Background", "Botnet"}


def test_feature_stats_saved_and_excludes_categoricals(config):
    engine = FeatureFusionEngine(config)
    engine.run()

    stats_path = Path(config["normalization"]["per_feature_stats_path"])
    assert stats_path.exists()

    with open(stats_path) as f:
        stats = json.load(f)

    ctu13_stats = stats["CTU-13"]
    assert "Dur" in ctu13_stats
    assert "mean" in ctu13_stats["Dur"] and "std" in ctu13_stats["Dur"]
    assert "sTos" not in ctu13_stats  # excluded categorical
    assert "Label" not in ctu13_stats  # excluded label


def test_missing_dataset_raises_clear_error(config):
    config["datasets"] = []
    engine = FeatureFusionEngine(config)
    with pytest.raises(ValueError, match="No datasets configured"):
        engine.run()


def test_bad_missing_value_strategy_rejected(config):
    config["missing_value_strategy"] = "not_a_real_strategy"
    with pytest.raises(NotImplementedError):
        FeatureFusionEngine(config)
