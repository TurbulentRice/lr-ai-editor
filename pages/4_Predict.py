from __future__ import annotations

from pathlib import Path
import streamlit as st

from ui import state
from modules.predict import predict_sliders


@st.cache_resource
def _load_model_cached(model_path: str, n_out: int, device_key: str):
    from modules.predict import build_model
    model, dev = build_model(model_path, n_out, device_key)
    return model, str(dev)


def main():
    state.ensure()
    st.title("Inference")

    # Sidebar controls (persisted defaults)
    _tr = state.get("Train", {})
    _pr = state.get("Predict", {})
    default_model = _pr.get("model_path", _tr.get("out_model", "model.pt"))
    default_device = _pr.get("device", "Auto")
    model_path = st.sidebar.text_input("Model path", value=default_model)
    device_choice = st.sidebar.selectbox(
        "Device",
        options=["Auto", "CPU", "GPU"],
        index=["Auto","CPU","GPU"].index(default_device) if default_device in ["Auto","CPU","GPU"] else 0
    )

    uploaded = st.file_uploader(
        "Upload image(s)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

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

        # Progress UI
        prog = st.progress(0)
        status = st.empty()
        def _cb(done: int, total: int, stage: str):
            frac = (done / total) if total else 1.0
            prog.progress(min(max(frac, 0.0), 1.0))
            status.text(f"{stage}… {done}/{total}")

        with st.spinner("Running inference…"):
            results_list = predict_sliders(
                uploaded,
                model_path,
                cols,
                device=selected_device,
                model=model_obj,
                progress_cb=_cb,
            )

        for filename, results in results_list:
            st.subheader(f"Results for {filename}")
            st.json(results)


if __name__ == "__main__":
    main()
