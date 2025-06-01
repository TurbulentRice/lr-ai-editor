import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from datetime import date

from train import train_model
from ingest import ingest
from predict import predict_sliders

today = date.today()
ten_years_ago = date(today.year - 10, today.month, today.day)

# ---------------------------------------
# Cache resources
# ---------------------------------------
@st.cache_resource
def run_train_model(csv_path: str, previews_dir: str, out_model_path: str, epochs: int = 5, batch_size: int = 32):
    return train_model(csv_path, previews_dir, out_model_path, epochs, batch_size)

# ---------------------------------------
# Streamlit UI
# ---------------------------------------
st.set_page_config(page_title="LR-AI-Editor", layout="wide")
# st.markdown(
#     """
#     <style>
#     </style>
#     """,
#     unsafe_allow_html=True
# )
st.title("LR-AI-Editor")
mode = st.sidebar.radio("Mode", ["Ingest", "Train", "Predict"] )

if mode == "Ingest":
    st.sidebar.header("Catalog Ingest")
    catalog_files = st.sidebar.file_uploader("Lightroom .lrcat file(s)", type=['lrcat'], accept_multiple_files=True)
    previews_dir = st.sidebar.text_input("Previews directory path", value="data/previews")
    out_csv = st.sidebar.text_input("Output CSV path", value="data/dataset/sliders.csv")

    # Ingest criteria options
    flagged = st.sidebar.checkbox("Only flagged images")
    edited = st.sidebar.checkbox("Only edited images")
    use_date = st.sidebar.checkbox("Filter by date range")
    if use_date:
        start_date = st.sidebar.date_input(
            "Start date",
            value=ten_years_ago,
            min_value=date(1970, 1, 1),
            max_value=today
        )
        end_date = st.sidebar.date_input(
            "End date",
            value=today,
            min_value=date(1970, 1, 2),
            max_value=today
        )
    color_label = st.sidebar.selectbox(
        "Color label", options=["Any", "Red", "Yellow", "Green", "Blue", "Purple"]
    )

    if st.sidebar.button("Run Ingest"):
        if not catalog_files:
            st.error("Please upload at least one .lrcat file first.")
        else:
            # Build criteria string
            criteria_parts = []
            if flagged:
                criteria_parts.append("flag=flagged")
            if use_date:
                criteria_parts.append(f"datecapt=>={start_date.isoformat()}")
                criteria_parts.append(f"datecapt=<={end_date.isoformat()}")
            # Neither of these work unfortunately, have to do it with pandas below
            # if edited:
            #     criteria_parts.append("modcount=>0")
            #     criteria_parts.append("extfile=xmp")
            if color_label != "Any":
                # The names in the database are localized, e.g. Bleu, Rouge, but this'll do for now
                mapping = {"Red":1, "Yellow":2, "Green":3, "Blue":4, "Purple":5}
                criteria_parts.append(f"colorlabel={mapping[color_label]}")
            criteria = ", ".join(criteria_parts)

            all_dfs = []
            for catalog_file in catalog_files:
                with st.spinner(f"Ingesting {catalog_file.name}…"):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".lrcat")
                    tmp.write(catalog_file.read())
                    tmp.flush()
                    tmp_path = Path(tmp.name)
                    df = ingest(tmp_path, Path(previews_dir), Path(out_csv), criteria)
                    # Locally filter for edited images since </> operators aren't supported for modcount 
                    if edited:
                        df = df[df["modcount"].astype(int) > 0]
                st.success(f"Ingested {len(df)} records from {catalog_file.name}")
                st.header(catalog_file.name)
                st.dataframe(df)
                all_dfs.append(df)
            # Show combined results
            if (len(catalog_files) > 1):
                combined = pd.concat(all_dfs, ignore_index=True)
                st.header("Combined Ingested Data")
                st.dataframe(combined)

elif mode == "Train":
    st.sidebar.header("Model Training")
    csv_path = st.sidebar.text_input("CSV path", value="data/dataset/sliders.csv")
    previews_dir = st.sidebar.text_input("Previews directory path", value="data/previews")
    out_model = st.sidebar.text_input("Output model path", value="model.pt")
    epochs = st.sidebar.number_input("Epochs", min_value=1, value=5)
    batch_size = st.sidebar.number_input("Batch size", min_value=1, value=16)

    if st.sidebar.button("Train Model"):
        with st.spinner("Training model…"):
            model, losses, slider_cols = run_train_model(csv_path, previews_dir, out_model, epochs, batch_size)
        st.success("Training complete")
        st.line_chart(losses)

elif mode == "Predict":
    st.sidebar.header("Inference")
    uploaded = st.file_uploader("Upload image(s)", type=['jpg','jpeg','png'], accept_multiple_files=True)
    if uploaded and st.sidebar.button("Predict Sliders"):
        cols = st.session_state.get('slider_cols', None)
        model_path = "model.pt"
        if not cols or not Path(model_path).exists():
            st.error("Model not found. Please train first.")
        else:
            # Call the helper to get all predictions
            results_list = predict_sliders(uploaded, model_path, cols)
            for filename, results in results_list:
                st.write(f"**Results for {filename}:**")
                st.json(results)
