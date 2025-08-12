from __future__ import annotations

import json
from pathlib import Path
import streamlit as st
from typing import Any, Dict

# Single file at repo root to persist cross-page settings
APP_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = APP_ROOT / ".lr_ai_editor_state.json"


def _load() -> Dict[str, Any]:
    try:
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text())
    except Exception:
        pass
    return {}


def _save(data: Dict[str, Any]) -> None:
    try:
        STATE_PATH.write_text(json.dumps(data, indent=2))
    except Exception:
        # best-effort persistence
        pass


def ensure() -> None:
    """
    Ensure persistent state is loaded into st.session_state.
    Initializes two keys:
      - 'persist': the JSON-compatible dict with user settings
      - '_persist_last': a stable JSON string used to detect changes
    """
    if "persist" not in st.session_state:
        st.session_state["persist"] = _load()
        st.session_state["_persist_last"] = json.dumps(st.session_state["persist"], sort_keys=True)


def save_if_changed() -> None:
    """
    Write the 'persist' object to disk only if it changed since last save.
    """
    try:
        cur = json.dumps(st.session_state.get("persist", {}), sort_keys=True)
        last = st.session_state.get("_persist_last", "")
        if cur != last:
            _save(st.session_state["persist"])
            st.session_state["_persist_last"] = cur
    except Exception:
        pass


# Convenience helpers ---------------------------------------------------------

def get(ns: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Read a namespaced settings dict from 'persist'. Does not create it.
    """
    persist = st.session_state.get("persist", {})
    val = persist.get(ns, None)
    if val is None:
        return {} if default is None else default
    return val


def update(ns: str, values: Dict[str, Any]) -> None:
    """
    Update a namespaced settings dict and mark it dirty for save_if_changed().
    """
    persist = st.session_state.setdefault("persist", {})
    bucket = persist.setdefault(ns, {})
    bucket.update(values or {})