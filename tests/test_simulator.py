"""
test_simulator.py
====================
Unit test stubs for `src/simulator/` (rollout_engine.py).

These tests are placeholders — they assert the interface exists and is
importable, but do not yet exercise real logic (which is unimplemented,
by design, in this scaffold).
"""

import pytest

from src.simulator.rollout_engine import build_rollout_engine


def test_build_rollout_engine_not_implemented():
    with pytest.raises(NotImplementedError):
        build_rollout_engine(world_model=None, config={})


# TODO(ML Research Lead): replace the above smoke test with real tests
# once rollout_engine.py is implemented:
#   - test rollout() returns the configured number of trajectories/steps
#   - test counterfactual_rollout() diverges from the unmodified rollout
