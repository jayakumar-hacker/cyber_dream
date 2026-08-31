"""
test_core.py
==============
Unit test stubs for `src/core/` (spatial_encoder.py, world_model.py).

These tests are placeholders — they assert the interface exists and is
importable, but do not yet exercise real logic (which is unimplemented,
by design, in this scaffold).
"""

import pytest

from src.core.spatial_encoder import build_spatial_encoder
from src.core.world_model import build_world_model


def test_build_spatial_encoder_not_implemented():
    with pytest.raises(NotImplementedError):
        build_spatial_encoder(config={})


def test_build_world_model_not_implemented():
    with pytest.raises(NotImplementedError):
        build_world_model(config={})


# TODO(ML Research Lead): replace the above smoke tests with real tests
# once spatial_encoder.py / world_model.py are implemented:
#   - test output embedding dimensionality matches configs/default.yaml
#   - test WorldModel.observe_step vs imagine_step state shape parity
