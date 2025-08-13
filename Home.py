from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

from ui import state
from modules.previews import find_active_job, is_job_active
from ui.components import render_thumbnail_grid


# Configure the app (only honored in the first script Streamlit runs)
st.set_page_config(page_title="Lightroom AI Editor", page_icon="🎞️", layout="wide")

# Load persisted settings
state.ensure()

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.title("Lightroom AI Editor")
st.write(
    "Build a training set from your Lightroom catalogs, generate fast image previews, "
    "train a slider-prediction model, and run inference – all in one place."
)

# Quick navigation
st.write(" ")
nav_cols = st.columns(4)
with nav_cols[0]:
    st.page_link("pages/1_Previews.py", label="🖼️ Previews")
with nav_cols[1]:
    st.page_link("pages/2_Ingest.py", label="📥 Ingest")
with nav_cols[2]:
    st.page_link("pages/3_Train.py", label="🏋️ Train")
with nav_cols[3]:
    st.page_link("pages/4_Predict.py", label="🎯 Predict")

st.divider()

# ---------------------------------------------------------------------------
# Status + helpful context
# ---------------------------------------------------------------------------
pv = state.get("Previews", {})
ing = state.get("Ingest", {})
trn = state.get("Train", {})

left, right = st.columns([2, 1])

with left:
    st.subheader("Project status")

    # Try to reclaim an active Previews job based on current settings
    src_dir = Path(pv.get("src_dir", "data/raw"))
    previews_dir = Path(pv.get("previews_dir", "data/previews"))
    job = find_active_job(src_dir, previews_dir)

    if job and is_job_active(job):
        st.success("Preview generation is running")
        st.write(
            f"**Status:** {job.status}  •  **Total:** {job.total}  •  "
            f"**Completed:** {job.completed}  •  **Skipped:** {job.skipped}  •  **Failed:** {job.failed}"
        )
        st.progress(job.progress())
    else:
        st.info("No preview job running. Visit **Previews** to start one.")

    # Recent outputs gallery (small, always visible)
    try:
        if previews_dir.exists():
            st.caption(f"Most recent previews in: {previews_dir}")
            render_thumbnail_grid(previews_dir, per_page=12, state_prefix="home_thumbs")
        else:
            st.caption("Set your preview output folder on the **Previews** page to see thumbnails here.")
    except Exception:
        pass

with right:
    st.subheader("Current settings")
    st.markdown(
        f"""
        **Previews**  
        • RAW: `{pv.get('src_dir', 'data/raw')}`  
        • Output: `{pv.get('previews_dir', 'data/previews')}`  
        • Size: `{pv.get('size_mode', 'exact_224')}` • Format: `{pv.get('fmt', 'jpeg')}` • Quality: `{pv.get('quality', 88)}`

        **Ingest**  
        • Previews dir: `{ing.get('previews_dir', 'data/previews')}`  
        • CSV: `{ing.get('out_csv', 'data/dataset/sliders.csv')}`

        **Train**  
        • CSV: `{trn.get('csv_path', 'data/dataset/sliders.csv')}`  
        • Previews dir: `{trn.get('previews_dir', 'data/previews')}`  
        • Model out: `{trn.get('out_model', 'model.pt')}` • Epochs: `{trn.get('epochs', 5)}` • Batch: `{trn.get('batch_size', 16)}`
        """,
        help="Edit these on their respective pages. Settings persist across reloads.",
    )

    # Quick view of the user-defined CSV path
    st.subheader("Dataset CSV")
    csv_path_str = trn.get("csv_path", "data/dataset/sliders.csv")
    csv_path = Path(csv_path_str)
    if csv_path.exists():
        try:
            # Light-weight row count without rendering a table
            row_ct = pd.read_csv(csv_path, usecols=["name"]).shape[0]
            st.write(f"Path: `{csv_path}`  •  Rows: **{row_ct}**")
        except Exception as e:
            st.write(f"Path: `{csv_path}`")
            st.info(f"Could not read CSV row count. Error: {e}")
    else:
        st.info("No CSV found yet. Set the path on the **Train** or **Ingest** page to see details here.")

st.divider()

# ---------------------------------------------------------------------------
# Quick start checklist
# ---------------------------------------------------------------------------
st.subheader("Quick start")
st.markdown(
    """
    1. **Generate previews** from your RAWs on the **Previews** page (JPEG/WebP, 224×224 recommended).
    2. **Ingest** your Lightroom catalog(s) to produce a CSV with slider targets on **Ingest**.
    3. **Train** a model against your previews + CSV on **Train**, choosing which sliders to learn.
    4. **Predict** sliders for new images on **Predict**.
    """
)

st.caption(
    "Pro tip: you can switch pages at any time - background preview jobs keep running, "
    "and your settings are saved automatically."
)
