"""
session_state.py
==================
Placeholder for Streamlit session-state / caching helpers shared across
`app/pages/*.py`.

Intended to eventually hold: cached model/config loading
(`st.cache_resource`), cached graph/rollout results
(`st.cache_data`), and typed accessors into `st.session_state` for
selections made on the Upload page.

NOTE: Left as an interface stub — no caching logic implemented yet.
"""

from __future__ import annotations

from typing import Any


def get_or_init(key: str, default: Any) -> Any:
    """
    Get a value from `st.session_state`, initializing it to `default`
    if not already present.

    Left unimplemented — depends on final session-state schema design.
    """
    raise NotImplementedError


def cache_model(config_path: str) -> Any:
    """
    Load and cache (via `st.cache_resource`) the full CyberDreamer
    model stack (encoder + world model + heads) for reuse across page
    navigations within a session.

    Left unimplemented — depends on the finished model-loading API.
    """
    raise NotImplementedError
