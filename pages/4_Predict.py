from __future__ import annotations

from pathlib import Path
from datetime import datetime
import streamlit as st
import time
import pandas as pd

from ui import state
from modules.predict import predict_sliders, build_model, inspect_model_file


st.set_page_config(page_title="Predict", page_icon="logo.svg", layout="wide")

@st.cache_resource
def _load_model_cached(model_path: str, n_out: int, device_key: str):
    model, dev = build_model(model_path, n_out, device_key)
    return model, str(dev)


# Cached inspector for model file
@st.cache_data
def _inspect_model_file(model_path: str, cache_buster: float = 0.0):
    return inspect_model_file(model_path)


def main():
    state.ensure()
    st.title("Inference")

    # Sidebar controls (persisted defaults)
    _tr = state.get("Train", {})
    _pr = state.get("Predict", {})
    default_model = _pr.get("model_path", _tr.get("out_model", "data/models/model.pt"))
    default_device = _pr.get("device", "Auto")
    default_out_csv = _pr.get("out_csv", "data/predictions/prediction.csv")

    model_path = st.sidebar.text_input("Model path", value=default_model)
    if Path(model_path).exists() and not _inspect_model_file(model_path).get("error"):
        st.sidebar.markdown("✅ Model file loaded")
    else:
        st.sidebar.markdown("⚠️ Model unreadable")
    device_choice = st.sidebar.selectbox(
        "Device",
        options=["Auto", "CPU", "GPU"],
        index=["Auto","CPU","GPU"].index(default_device) if default_device in ["Auto","CPU","GPU"] else 0
    )
    out_csv_path = st.sidebar.text_input(
        "Predictions output path",
        value=default_out_csv,
        help="Where to write predictions CSV automatically after inference."
    )

    # Model status/metadata preview in sidebar
    try:
        mtime = Path(model_path).stat().st_mtime if Path(model_path).exists() else 0.0
    except Exception:
        mtime = 0.0
    model_info = _inspect_model_file(model_path, cache_buster=mtime)

    # Persist current Predict settings (including out_csv_path)
    state.update("Predict", {"model_path": model_path, "device": device_choice, "out_csv": out_csv_path})
    state.save_if_changed()

    # Create a horizontal row at the top of main content area for Model details and file uploader
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### Model details")
        # Removed expander, show model details always with only essential fields
        if not model_info.get("exists"):
            st.info("No model file found at the specified path.")
        elif model_info.get("error"):
            st.warning(f"Could not read model: {model_info['error']}")
        else:
            left_col, right_col = st.columns(2)
            with left_col:
                st.markdown(f"**Path:** `{model_path}`")

                size_mb = model_info.get("size", 0) / (1024 * 1024)
                st.markdown(f"**Size:** {size_mb:.2f} MB")
                
                last_mod = datetime.fromtimestamp(model_info.get("mtime", 0)).strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"**Last modified:** {last_mod}")

                fmt = "Package (weights + metadata)" if model_info.get("package") else ("Raw state_dict" if model_info.get("raw_state_dict") else "Unknown")
                st.markdown(f"**Format:** {fmt}")
            with right_col:

                if "metadata" in model_info:
                    st.markdown("**Metadata:**")
                    st.json(model_info["metadata"], expanded=False)

    with col2:
        uploaded = st.file_uploader(
            "Upload image(s)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="predict_uploads",
        )

    if uploaded:
        st.info(f"{len(uploaded)} image(s) selected for prediction.")
        st.session_state["uploaded_files"] = uploaded
    else:
        # Clear saved uploads if user removes them
        st.session_state.pop("uploaded_files", None)

    # Last predictions (persisted) — will render after predictions table if available
    last_pred = state.get("PredictLastRun")

    predictions_table_rendered = False

    if uploaded and st.sidebar.button("Predict Sliders"):
        cols = st.session_state.get("slider_cols", None)
        if not cols:
            # Fall back to the selection used on the Train page (may differ in order from true training order)
            cols = _tr.get("selected_sliders", None)
        if not cols:
            st.error("Could not determine slider order. Train a model first, or open the Train page to select sliders.")
            return

        if not Path(model_path).exists():
            st.error(f"Model not found at {model_path}. Set the correct path or train a new model.")
            return

        # Cache & load model
        model_obj, resolved_device = _load_model_cached(
            model_path,
            len(cols),
            selected_device := {"auto": "auto", "cpu": "cpu", "gpu": "gpu"}[device_choice.lower()]
        )

        # Progress UI with placeholders (so we can clear/replace when done)
        prog_ph = st.empty()
        status_ph = st.empty()
        prog = prog_ph.progress(0)
        def _cb(done: int, total: int, stage: str):
            frac = (done / total) if total else 1.0
            prog.progress(min(max(frac, 0.0), 1.0))
            status_ph.text(f"{stage}… {done}/{total}")

        t0 = time.perf_counter()
        with st.spinner("Running inference…"):
            results_list = predict_sliders(
                uploaded,
                model_path,
                cols,
                device=selected_device,
                model=model_obj,
                progress_cb=_cb,
            )
        t1 = time.perf_counter()
        # Clear progress UI and show completion
        prog_ph.empty()
        status_ph.empty()
        st.success(f"Inference complete: processed {len(results_list)} image(s) in {t1 - t0:.2f}s on device {resolved_device}.")

        # --- Aggregate table + AUTO-WRITE CSV ---
        try:
            from modules.export import predictions_to_dataframe, save_predictions_csv
            df = predictions_to_dataframe(results_list)
            if not df.empty:
                # Ensure parent folder exists and write to disk
                out_csv_path_obj = Path(out_csv_path)
                out_csv_path_obj.parent.mkdir(parents=True, exist_ok=True)
                save_predictions_csv(results_list, out_csv_path_obj)

                # Persist summary for future pageloads
                last_pred_summary = {
                    "out_csv_path": str(out_csv_path_obj),
                    "num_images": len(results_list),
                    "num_rows": int(df.shape[0]),
                    "num_cols": int(df.shape[1]),
                }
                state.update("PredictLastRun", last_pred_summary)
                state.save_if_changed()

                # Display from the saved CSV (source of truth)
                try:
                    df_saved = pd.read_csv(out_csv_path_obj)
                    st.markdown("### Predictions table")
                    st.dataframe(df_saved, use_container_width=True)
                    st.caption(
                        f"Saved to `{out_csv_path_obj}` • Rows: {len(df_saved)} • "
                        "Values are denormalized and clamped/rounded to Lightroom ranges."
                    )
                    predictions_table_rendered = True
                except Exception as e:
                    st.warning(f"CSV was written, but couldn't be read back for display: {e}")
            else:
                st.info("No predictions to export.")
        except Exception as e:
            st.warning(f"Couldn't build/save CSV: {e}")

    # Render Last predictions expander after predictions table if available
    if last_pred and predictions_table_rendered:
        p = Path(last_pred.get("out_csv_path", ""))
        with st.expander(f"Last predictions: {p}", expanded=False):
            if p.exists():
                try:
                    df_prev = pd.read_csv(p)
                    st.dataframe(df_prev, use_container_width=True, height=300)
                    st.caption(f"Rows: {len(df_prev)} • Saved: {datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    st.warning(f"Could not read previous predictions CSV: {e}")
            else:
                st.info("The previously saved predictions CSV could not be found. Run inference to create it.")

    # If no predictions table rendered, show last predictions expander here
    if last_pred and not predictions_table_rendered:
        p = Path(last_pred.get("out_csv_path", ""))
        with st.expander(f"Last predictions: {p}", expanded=False):
            if p.exists():
                try:
                    df_prev = pd.read_csv(p)
                    st.dataframe(df_prev, use_container_width=True, height=300)
                    st.caption(f"Rows: {len(df_prev)} • Saved: {datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    st.warning(f"Could not read previous predictions CSV: {e}")
            else:
                st.info("The previously saved predictions CSV could not be found. Run inference to create it.")


if __name__ == "__main__":
    main()
