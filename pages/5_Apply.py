from pathlib import Path
import shutil
import streamlit as st
import pandas as pd
from modules.apply import apply_predictions_to_catalog, load_predictions
from modules.ingest import ingest
from ui.state import ensure, save_if_changed, get, update

if "apply_predictions_btn" not in st.session_state:
    st.session_state["apply_predictions_btn"] = False
if "is_applying" not in st.session_state:
    st.session_state["is_applying"] = False

ensure()

st.set_page_config(page_title="Predict", page_icon="logo.svg", layout="wide")

st.title("Apply Predictions to Lightroom Catalog")
st.markdown("Use this page to apply your AI-generated predictions to your Lightroom catalog.")

import os

predictions_folder = "data/predictions/"
try:
    prediction_files = [f for f in os.listdir(predictions_folder) if f.endswith(".csv")]
except FileNotFoundError:
    prediction_files = []

with st.sidebar:
    st.markdown("### Select prediction file")
    if prediction_files:
        prediction_file_name = st.selectbox(
            "Select Prediction CSV",
            options=prediction_files,
            help="Select a prediction CSV file from the data/predictions/ folder"
        )
        prediction_file_path = os.path.join(predictions_folder, prediction_file_name)
        if prediction_file_name:
            file_size_kb = os.path.getsize(prediction_file_path) / 1024
            st.write(f"**Selected file:** {prediction_file_name} ({file_size_kb:.2f} KB)")
            try:
                df_predictions = pd.read_csv(prediction_file_path)
                st.write(f"**Rows:** {df_predictions.shape[0]}")
                st.success("✅ CSV loaded")
            except Exception as e:
                st.warning(f"Failed to read prediction file: {e}")
                df_predictions = None
        else:
            df_predictions = None
    else:
        st.warning("No prediction CSV files found in 'data/predictions/' folder.")
        prediction_file_name = None
        prediction_file_path = None
        df_predictions = None

    apply_predictions_btn = None

st.markdown("### Upload Lightroom Catalog (.lrcat)")
uploaded_file = st.file_uploader(
    "Upload your Lightroom Catalog file (.lrcat)",
    type=["lrcat"],
    help="Upload your Lightroom catalog file to apply predictions"
)

catalog_temp_dir = Path("session")
catalog_temp_dir.mkdir(exist_ok=True)
catalog_temp_path = catalog_temp_dir / "uploaded_catalog.lrcat"
edited_catalog_path = catalog_temp_dir / "uploaded_catalog_edited.lrcat"

if uploaded_file is not None:
    with open(catalog_temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        df = ingest(catalog_temp_path)
        if df is not None and not df.empty:
            if df_predictions is not None and not df_predictions.empty:
                if "name" in df.columns and "stem" in df_predictions.columns:
                    catalog_stems = set(Path(name).stem for name in df["name"])
                    pred_stems = set(df_predictions["stem"])
                    matched = catalog_stems.intersection(pred_stems)
                    st.caption(f"Rows: {df.shape[0]} · Matches in CSV: {len(matched)} of {len(pred_stems)}")
                    st.success("Catalog file loaded successfully!")
                else:
                    st.warning("The catalog or prediction file is missing the required columns ('name' in catalog, 'stem' in predictions). Skipping file matching.")
                    st.caption(f"Rows: {df.shape[0]}")
                    st.success("Catalog file loaded successfully!")
            else:
                st.caption(f"Rows: {df.shape[0]}")
                st.success("Catalog file loaded successfully!")
        else:
            st.warning("Catalog file appears to be empty or could not be parsed.")
    except Exception as e:
        st.warning(f"Failed to read catalog: {e}")

apply_ready = (
    'prediction_file_path' in locals() and prediction_file_path is not None and
    uploaded_file is not None
)
with st.sidebar:
    if apply_ready:
        apply_predictions_btn = st.button(
            "Apply Predictions",
            key="apply_predictions_btn",
            disabled=st.session_state.get("is_applying", False)
        )
    else:
        st.button("Apply Predictions", key="apply_predictions_btn_disabled", disabled=True)

if apply_ready and apply_predictions_btn and not st.session_state.get("is_applying", False):
    try:
        st.session_state["is_applying"] = True
        shutil.copy2(str(catalog_temp_path), str(edited_catalog_path))
        with st.spinner("Applying predictions to catalog..."):
            predictions = load_predictions(prediction_file_path)
            num_updated = apply_predictions_to_catalog(
                str(edited_catalog_path),
                predictions
            )
        st.success(f"Predictions applied! {num_updated} records updated in the catalog.")
        with open(edited_catalog_path, "rb") as f:
            st.download_button(
                label="Download Edited Catalog",
                data=f,
                file_name=edited_catalog_path.name,
                mime="application/octet-stream"
            )
    except Exception as e:
        st.error(f"An error occurred while applying predictions: {e}")
    finally:
        st.session_state["is_applying"] = False
