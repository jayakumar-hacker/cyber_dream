"""
test_pipeline.py
===================
Unit test stubs for `src/pipeline/` (feature_fusion.py, graph_constructor.py).

These tests are placeholders — they assert the interface exists and is
importable, but do not yet exercise real logic (which is unimplemented,
by design, in this scaffold).
"""

import pytest

from src.pipeline.feature_fusion import FeatureFusionEngine
from src.pipeline.graph_constructor import GraphConstructor


def test_feature_fusion_engine_is_constructible():
    engine = FeatureFusionEngine(config={})
    assert engine.config == {}


def test_feature_fusion_engine_run_not_implemented():
    engine = FeatureFusionEngine(config={})
    with pytest.raises(NotImplementedError):
        engine.load_raw_sources(raw_dir=None)


def test_graph_constructor_is_constructible():
    constructor = GraphConstructor(config={})
    assert constructor.config == {}


def test_graph_constructor_run_not_implemented():
    constructor = GraphConstructor(config={})
    with pytest.raises(NotImplementedError):
        constructor.build_nodes(feature_table=None, window_id="w0")


# TODO(WS1/WS2): replace the above smoke tests with real fixtures once
# feature_fusion.py / graph_constructor.py are implemented:
#   - test windowing correctness on a synthetic CIC-IDS-2018 sample
#   - test node/edge schema conformance against configs/default.yaml
