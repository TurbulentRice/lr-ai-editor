from __future__ import annotations

from pathlib import Path
from datetime import datetime
import streamlit as st
import torch
import time

from ui import state
from modules.predict import predict_sliders


@st.cache_resource
def _load_model_cached(model_path: str, n_out: int, device_key: str):
    from modules.predict import build_model
    model, dev = build_model(model_path, n_out, device_key)
    return model, str(dev)


# Cached inspector for model file
@st.cache_data
def _inspect_model_file(model_path: str, cache_buster: float = 0.0):
    p = Path(model_path)
    if not p.exists():
        return {"exists": False}
    info = {"exists": True, "size": p.stat().st_size, "mtime": p.stat().st_mtime}
    try:
        obj = torch.load(str(p), map_location="cpu")
        if isinstance(obj, dict) and "weights" in obj and "metadata" in obj:
            info["package"] = True
            meta = obj.get("metadata", {}) or {}
            info["metadata"] = meta  # keep raw for detailed view (safe dict)
            # sliders
            sliders = meta.get("slider_friendly")
            if isinstance(sliders, list):
                info["num_sliders"] = len(sliders)
                info["slider_list"] = sliders
            # preprocess
            pp = meta.get("preprocess", {}) or {}
            if pp:
                info["preprocess"] = pp
            # normalization presence
            tn = meta.get("target_norm")
            info["has_target_norm"] = bool(tn)
            # app version if present
            if isinstance(meta, dict) and "app_version" in meta:
                info["app_version"] = meta["app_version"]
        else:
            info["raw_state_dict"] = True
            # Best-effort guess for output size
            if isinstance(obj, dict):
                n_out = None
                for k, v in obj.items():
                    try:
                        if isinstance(v, torch.Tensor):
                            if v.ndim == 2:
                                n_out = int(v.shape[0])
                            elif v.ndim == 1:
                                n_out = int(v.shape[0])
                    except Exception:
                        pass
                if n_out is not None:
                    info["guessed_n_outputs"] = n_out
        return info
    except Exception as e:
        info["error"] = str(e)
        return info


def main():
    state.ensure()
    st.title("Inference")

    # Sidebar controls (persisted defaults)
    _tr = state.get("Train", {})
    _pr = state.get("Predict", {})
    default_model = _pr.get("model_path", _tr.get("out_model", "data/models/model.pt"))
    default_device = _pr.get("device", "Auto")
    model_path = st.sidebar.text_input("Model path", value=default_model)
    device_choice = st.sidebar.selectbox(
        "Device",
        options=["Auto", "CPU", "GPU"],
        index=["Auto","CPU","GPU"].index(default_device) if default_device in ["Auto","CPU","GPU"] else 0
    )

    # Model status/metadata preview in sidebar
    try:
        mtime = Path(model_path).stat().st_mtime if Path(model_path).exists() else 0.0
    except Exception:
        mtime = 0.0
    model_info = _inspect_model_file(model_path, cache_buster=mtime)

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

    with st.expander("Model details", expanded=False):
        if not model_info.get("exists"):
            st.info("No model file found at the specified path.")
        elif model_info.get("error"):
            st.warning(f"Could not read model: {model_info['error']}")
        else:
            size_mb = model_info.get("size", 0) / (1024 * 1024)
            when = datetime.fromtimestamp(model_info.get("mtime", 0)).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(f"**Path:** `{model_path}`")
            st.markdown(f"**Size:** {size_mb:.1f} MB &nbsp;&nbsp; • &nbsp;&nbsp; **Modified:** {when}")

            fmt = "Package (weights + metadata)" if model_info.get("package") else ("Raw state_dict" if model_info.get("raw_state_dict") else "Unknown")
            st.markdown(f"**Format:** {fmt}")

            if model_info.get("package"):
                app_v = model_info.get("app_version")
                if app_v:
                    st.markdown(f"**App version:** `{app_v}`")
                pp = model_info.get("preprocess") or {}
                if pp:
                    st.markdown("**Preprocess:**")
                    st.json(pp, expanded=False)
                tn = (model_info.get("metadata") or {}).get("target_norm")
                st.markdown("**Target normalization:** " + ("Yes" if tn else "No"))
                sliders = model_info.get("slider_list")
                if isinstance(sliders, list):
                    st.markdown(f"**Sliders ({len(sliders)}):**")
                    head = sliders[:16]
                    tail = sliders[16:]
                    st.code(", ".join(head))
                    if tail:
                        with st.expander("Show all sliders", expanded=False):
                            st.code(", ".join(sliders))
            else:
                if model_info.get("guessed_n_outputs"):
                    st.markdown(f"**Guessed outputs:** {model_info['guessed_n_outputs']}")

    with st.sidebar:
        if not model_info.get("exists"):
            st.error("Model file not found")
        elif model_info.get("error"):
            st.warning(f"Model could not be read: {model_info['error']}")
        else:
            st.success("Model OK")
            size_mb = model_info.get("size", 0) / (1024 * 1024)
            st.caption(f"Size: {size_mb:.1f} MB")
            if model_info.get("package"):
                st.caption("Format: Package (weights + metadata)")
            elif model_info.get("raw_state_dict") and model_info.get("guessed_n_outputs"):
                st.caption(f"Outputs (guessed): {model_info['guessed_n_outputs']}")

    # Persist current Predict settings
    state.update("Predict", {"model_path": model_path, "device": device_choice})
    state.save_if_changed()

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

        for filename, results in results_list:
            st.subheader(f"Results for {filename}")
            st.json(results)


if __name__ == "__main__":
    main()
