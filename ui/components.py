from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Data preview helper
# ---------------------------------------------------------------------------

def build_preview_table(
    csv_path: str | Path,
    selected_friendly: List[str],
    limit: int = 200,
    slider_name_map: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Create a lightweight preview table with filename and selected slider columns (friendly names).
    Values are pulled from developsettings.sliders and default to 0.0 when missing.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    # Late import to avoid hard dependency when unused
    if slider_name_map is None:
        try:
            from modules.train import SLIDER_NAME_MAP  # type: ignore
            slider_name_map = SLIDER_NAME_MAP
        except Exception:
            slider_name_map = {}

    usecols = ["name", "developsettings"]
    df = pd.read_csv(csv_path, usecols=usecols)
    if limit:
        df = df.head(int(limit))

    def _parse(js):
        if isinstance(js, dict):
            return js
        if not isinstance(js, str) or js.strip() == "":
            return {}
        try:
            return json.loads(js)
        except Exception:
            return {}

    parsed = df["developsettings"].apply(_parse)
    out = pd.DataFrame({"filename": df["name"]})
    for friendly in selected_friendly:
        raw = (slider_name_map or {}).get(friendly)
        if not raw:
            continue
        out[friendly] = parsed.apply(
            lambda d: float(d.get("sliders", {}).get(raw, 0.0)) if isinstance(d, dict) else 0.0
        )
    return out


# ---------------------------------------------------------------------------
# Thumbnail grid (paginated)
# ---------------------------------------------------------------------------

def render_thumbnail_grid(
    previews_dir: str | Path,
    *,
    per_page: int = 24,
    state_prefix: str = "thumb",
    caption: str | None = None,
) -> dict:
    """
    Render a paginated thumbnail grid from a previews directory.
    Returns a dict with {total, page, num_pages}.
    """
    outdir = Path(previews_dir)
    files = list(outdir.glob("*.jpg")) + list(outdir.glob("*.jpeg")) + list(outdir.glob("*.webp"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    total = len(files)
    meta = {"total": total, "page": 1, "num_pages": 1}

    if total == 0:
        st.info(f"No preview images found in {outdir}.")
        return meta

    last_key = f"{state_prefix}_last_dir"
    page_key = f"{state_prefix}_page"
    # Initialize / reset pagination when directory changes
    if last_key not in st.session_state or st.session_state[last_key] != str(outdir):
        st.session_state[last_key] = str(outdir)
        st.session_state[page_key] = 1
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    num_pages = (total + per_page - 1) // per_page
    meta["num_pages"] = num_pages
    meta["page"] = st.session_state[page_key]

    # Controls
    cprev, cmid, cnext = st.columns([1, 3, 1])
    with cprev:
        if st.button("⟨ Prev", key=f"{state_prefix}_prev"):
            st.session_state[page_key] = max(1, st.session_state[page_key] - 1)
    with cnext:
        if st.button("Next ⟩", key=f"{state_prefix}_next"):
            st.session_state[page_key] = min(num_pages, st.session_state[page_key] + 1)
    with cmid:
        st.write(f"Page {st.session_state[page_key]} of {num_pages} • {total} images")

    # Page slice
    page = st.session_state[page_key]
    start = (page - 1) * per_page
    end = start + per_page
    samples = files[start:end]

    # Grid
    if caption:
        st.caption(caption)
    else:
        st.caption(f"Outputs in: {outdir}")
    n_cols = 6
    rows = (len(samples) + n_cols - 1) // n_cols
    for r in range(rows):
        cols = st.columns(n_cols)
        for c in range(n_cols):
            i = r * n_cols + c
            if i < len(samples):
                with cols[c]:
                    st.image(str(samples[i]), use_container_width=True)

    return meta


# ---------------------------------------------------------------------------
# Grouped slider selector
# ---------------------------------------------------------------------------

def render_grouped_slider_selector(
    all_sliders: List[str],
    *,
    selected_groups_default: Optional[List[str]] = None,
    selected_sliders_default: Optional[List[str]] = None,
    sidebar: bool = True,
    groups_key: Optional[str] = None,
    sliders_key: Optional[str] = None,
    restrict_to_groups: bool = True,
) -> tuple[list[str], list[str], list[str], dict[str, list[str]]]:
    """
    Render grouped slider selection UI.
    Returns (selected_groups, selected_sliders, effective_sliders, groups_map).

    Notes:
    - When restrict_to_groups=True, the fine-tune multiselect is limited to sliders
      that belong to the currently chosen groups. This keeps the UI consistent with
      the "effective" set and avoids confusion.
    """
    # Group by prefix before "_" (no underscore -> "primary")
    groups: dict[str, list[str]] = {}
    for k in all_sliders:
        prefix = k.split("_", 1)[0] if "_" in k else "primary"
        groups.setdefault(prefix, []).append(k)
    all_groups = sorted(groups.keys(), key=lambda g: (g != "primary", g))

    container = st.sidebar if sidebar else st
    sel_groups_default = selected_groups_default or all_groups
    selected_groups = container.multiselect(
        "Groups",
        options=all_groups,
        default=[g for g in sel_groups_default if g in all_groups] or all_groups,
        help='Toggle entire slider groups (e.g., "curve_*").',
        key=groups_key,
    )

    sliders_in_selected_groups = [s for g in selected_groups for s in groups[g]]
    # Fine-tune options are limited to the current groups if restrict_to_groups
    fine_tune_options = sliders_in_selected_groups if restrict_to_groups else all_sliders
    sel_sliders_default = selected_sliders_default or sliders_in_selected_groups
    selected_sliders = container.multiselect(
        "Fine-tune sliders within selected groups",
        options=fine_tune_options,
        default=[s for s in sel_sliders_default if s in fine_tune_options] or sliders_in_selected_groups,
        help="Deselect any sliders you don't want to include in training.",
        key=sliders_key,
    )

    effective_sliders = [s for s in selected_sliders if s in sliders_in_selected_groups]
    container.caption(f"Using {len(effective_sliders)} sliders across {len(selected_groups)} group(s).")
    return selected_groups, selected_sliders, effective_sliders, groups