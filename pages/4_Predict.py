from __future__ import annotations

from pathlib import Path
import streamlit as st

from ui import state
from modules.predict import predict_sliders


def main():
    state.ensure()
    st.title("Inference")

    # Sidebar controls (persisted defaults)
    _tr = state.get("Train", {})
    _pr = state.get("Predict", {})
    default_model = _pr.get("model_path", _tr.get("out_model", "model.pt"))
    model_path = st.sidebar.text_input("Model path", value=default_model)

    uploaded = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Persist current Predict settings
    state.update("Predict", {"model_path": model_path})
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

        with st.spinner("Running inference…"):
            results_list = predict_sliders(uploaded, model_path, cols)

        for filename, results in results_list:
            st.subheader(f"Results for {filename}")
            st.json(results)


if __name__ == "__main__":
    main()
