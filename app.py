# app.py
# A unified Streamlit application for ingesting, training, and inference
# Usage: streamlit run app.py

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as T
from PIL import Image
from common.model import ResNetRegressor

from lrtools.lrcat import LRCatDB  # make sure Lightroom-SQL-tools is installed

torch.classes.__path__ = []  # Neutralizes the path inspection

# ---------------------------------------
# Ingest function
# ---------------------------------------
def run_ingest(catalog_path: Path, previews_dir: Path, out_csv: Path):
    # Use Lightroom-SQL-tools to extract XMP blobs
    db = LRCatDB(str(catalog_path))
    rows = db.fetchall("SELECT image, xmp FROM Adobe_AdditionalMetadata")
    data = []
    for image_id, xmp in rows:
        data.append({'image': image_id, 'xmp': xmp})
    df = pd.DataFrame(data)
    df.to_csv(out_csv, index=False)
    return df

# ---------------------------------------
# Dataset and Train function
# ---------------------------------------
class PreviewDataset(Dataset):
    def __init__(self, df: pd.DataFrame, previews_dir: Path, transform=None):
        self.df = df
        self.previews_dir = previews_dir
        self.transform = transform or T.Compose([
            T.Resize((224,224)),
            T.ToTensor()
        ])
        self.slider_cols = [c for c in df.columns if c not in ('image','xmp')]

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_file = self.previews_dir / f"{row['image']}.jpg"
        image = Image.open(img_file).convert('RGB')
        if self.transform:
            image = self.transform(image)
        sliders = torch.tensor(
            row[self.slider_cols].values,
            dtype=torch.float32
        )
        return image, sliders

@st.cache_resource
def train_model(csv_path, previews_dir, epochs=5, batch_size=32):
    df = pd.read_csv(csv_path)
    ds = PreviewDataset(df, Path(previews_dir))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    model = ResNetRegressor(n_outputs=len(ds.slider_cols)).to('cpu')
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    losses = []
    for epoch in range(epochs):
        total_loss = 0.0
        for imgs, targets in loader:
            preds = model(imgs)
            loss = loss_fn(preds, targets)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(loader)
        losses.append(avg_loss)
    return model, losses, ds.slider_cols

# ---------------------------------------
# Streamlit UI
# ---------------------------------------
st.set_page_config(page_title="LR-AI-Editor", layout="wide")
st.title("LR-AI-Editor")
mode = st.sidebar.radio("Mode", ["Ingest", "Train", "Predict"] )

if mode == "Ingest":
    st.sidebar.header("Catalog Ingest")
    catalog_file = st.sidebar.file_uploader("Lightroom .lrcat file", type=['lrcat'])
    previews_dir = st.sidebar.text_input("Previews directory path", value="data/previews")
    out_csv = st.sidebar.text_input("Output CSV path", value="data/sliders.csv")

    if st.sidebar.button("Run Ingest"):
        if catalog_file is None:
            st.error("Please upload a .lrcat file first.")
        else:
            with st.spinner("Ingesting catalog…"):
                # Write uploaded catalog to temp file
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".lrcat")
                tmp.write(catalog_file.read())
                tmp.flush()
                tmp_path = Path(tmp.name)
                df = run_ingest(tmp_path, Path(previews_dir), Path(out_csv))
            st.success(f"Ingested {len(df)} records")
            st.dataframe(df.head())

elif mode == "Train":
    st.sidebar.header("Model Training")
    csv_path = st.sidebar.text_input("CSV path", value="data/sliders.csv")
    previews_dir = st.sidebar.text_input("Previews directory path", value="data/previews")
    epochs = st.sidebar.number_input("Epochs", min_value=1, value=5)
    batch_size = st.sidebar.number_input("Batch size", min_value=1, value=16)

    if st.sidebar.button("Train Model"):
        with st.spinner("Training model…"):
            model, losses, slider_cols = train_model(csv_path, previews_dir, epochs, batch_size)
            # Save model
            torch.save(model.state_dict(), "model.pt")
        st.success("Training complete")
        st.line_chart(losses)

elif mode == "Predict":
    st.sidebar.header("Inference")
    uploaded = st.file_uploader("Upload an image", type=['jpg','jpeg','png'])
    if uploaded and st.sidebar.button("Predict Sliders"):
        # Image.open(io.BytesIO(uploaded))
        img = Image.open(uploaded).convert("RGB")
        transform = T.Compose([T.Resize((224,224)), T.ToTensor()])
        tensor = transform(img).unsqueeze(0)
        # Load model and slider columns
        cols = st.session_state.get('slider_cols', None)
        if not cols or not Path("model.pt").exists():
            st.error("Model not found. Please train first.")
        else:
            model = ResNetRegressor(n_outputs=len(cols))
            model.load_state_dict(torch.load("model.pt"))
            model.eval()
            preds = model(tensor).detach().numpy()[0]
            results = {col: float(val) for col, val in zip(cols, preds)}
            st.json(results)
