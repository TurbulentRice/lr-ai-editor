from pathlib import Path
import time
import pandas as pd
import streamlit as st

from modules.previews import start_previews_job, is_job_active, find_active_job
from ui import state
from ui.components import render_thumbnail_grid


def main():
    state.ensure()

    st.title("Generate Previews")
    _pv = state.get("Previews", {})

    # Sidebar controls (persisted defaults)
    src_dir = st.sidebar.text_input("RAW source folder", value=_pv.get("src_dir", "data/raw"))
    previews_dir = st.sidebar.text_input("Previews output folder", value=_pv.get("previews_dir", "data/previews"))
    size_mode = st.sidebar.selectbox(
        "Size mode",
        ["exact_224", "short256_center224", "none"],
        index=["exact_224", "short256_center224", "none"].index(_pv.get("size_mode", "exact_224")),
    )
    fmt = st.sidebar.selectbox("Format", ["jpeg", "webp"], index=["jpeg", "webp"].index(_pv.get("fmt", "jpeg")))
    quality = st.sidebar.slider("Quality", 60, 95, int(_pv.get("quality", 88)))
    recursive = st.sidebar.checkbox("Recurse subfolders", bool(_pv.get("recursive", True)))
    overwrite = st.sidebar.checkbox("Overwrite existing", bool(_pv.get("overwrite", False)))
    max_workers = st.sidebar.number_input("Workers", min_value=1, max_value=16, value=int(_pv.get("max_workers", 4)))
    limit = st.sidebar.number_input("Limit files (0 = no limit)", min_value=0, value=int(_pv.get("limit", 0)))

    limit_by_csv = st.sidebar.checkbox("Limit to images listed in a dataset CSV", value=bool(_pv.get("limit_by_csv", False)))
    csv_filter_path = st.sidebar.text_input(
        "Dataset CSV (optional)",
        value=_pv.get("csv_filter_path", ""),
        help="If enabled, only RAW files whose stem appears in the CSV 'name' column will be converted.",
    )

    include_stems = None
    if limit_by_csv and csv_filter_path.strip():
        try:
            df_names = pd.read_csv(csv_filter_path, usecols=["name"])
            include_stems = set(Path(n).stem for n in df_names["name"].astype(str).tolist())
            st.sidebar.caption(f"CSV filter active: {len(include_stems)} filenames")
        except Exception as e:
            st.sidebar.warning(f"Could not read CSV names: {e}")
            include_stems = None

    # Reclaim or get active job
    job = st.session_state.get("previews_job", None)
    if job is None:
        reclaimed = find_active_job(Path(src_dir), Path(previews_dir))
        if reclaimed is not None:
            job = reclaimed
            st.session_state["previews_job"] = job

    c1, c2 = st.sidebar.columns(2)
    if c1.button("Start"):
        if is_job_active(job):
            st.sidebar.warning("A job is already running.")
        else:
            job = start_previews_job(
                Path(src_dir),
                Path(previews_dir),
                size_mode=size_mode,
                fmt=fmt,
                quality=int(quality),
                recursive=recursive,
                overwrite=overwrite,
                max_workers=int(max_workers),
                limit=(int(limit) or None),
                include_stems=include_stems,
            )
            st.session_state["previews_job"] = job

    if c2.button("Cancel"):
        if is_job_active(job):
            job.cancel()

    st.header("Preview generation status")
    if job is None:
        st.info("No active job. Configure options and click Start.")
    else:
        st.write(f"Status: **{job.status}**")
        st.write(f"Total: {job.total} • Completed: {job.completed} • Skipped: {job.skipped} • Failed: {job.failed}")
        st.progress(job.progress())

        # Recent file results
        if job.logs:
            logs_df = pd.DataFrame(job.logs[-200:])
            st.dataframe(logs_df, use_container_width=True, height=300)

    # Persist current Previews settings
    state.update("Previews", {
        "src_dir": src_dir,
        "previews_dir": previews_dir,
        "size_mode": size_mode,
        "fmt": fmt,
        "quality": int(quality),
        "recursive": bool(recursive),
        "overwrite": bool(overwrite),
        "max_workers": int(max_workers),
        "limit": int(limit),
        "limit_by_csv": bool(limit_by_csv),
        "csv_filter_path": csv_filter_path,
    })
    state.save_if_changed()

    # Thumbnails from the configured Previews output folder (paginated, always shown)
    try:
        render_thumbnail_grid(previews_dir, per_page=24, state_prefix="thumb", caption=f"Outputs in: {previews_dir}")
    except Exception:
        pass

    # Auto-refresh every 2s while a job is active
    if job is not None and is_job_active(job):
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()
