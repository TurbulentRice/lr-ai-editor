"""
Unified training logic callable from both CLI and Streamlit.
Lightweight training script for Lightroom slider-prediction model.
"""
from pathlib import Path
import pandas as pd
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
from typing import Tuple, List
from modules.model import ResNetRegressor
import json

torch.classes.__path__ = []  # Neutralizes the path inspection

# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
class PreviewDataset(Dataset):
    def __init__(self, csv_path: Path, previews_dir: Path, transform=None):
        """
        Dataset for loading image previews and their corresponding developsettings slider values.

        CSV must contain:
          - A 'name' column with image filenames (without extension or with extension as appropriate)
          - A 'developsettings' column containing a JSON string with {"sliders": { ... }}

        As of now, "name" and "developsettings" are the only columns we look at. Everything else from the CSV is ignored.
        Eventually the user will select which columns to use for training, or at least choose between
        using developsettings and XMP, but for now we'll just look at the sliders.
        """

        self.df = pd.read_csv(csv_path, usecols=["name", "developsettings"])
        self.previews_dir = Path(previews_dir)
        self.transform = transform or T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
            ]
        )

        # Ensure required columns exist
        if "name" not in self.df.columns:
            raise ValueError("CSV must contain a 'name' column for image filenames.")
        if "developsettings" not in self.df.columns:
            raise ValueError("CSV must contain a 'developsettings' column (JSON-encoded).")

        # Parse developsettings JSON strings into Python dicts for each row
        self.df["developsettings"] = self.df["developsettings"].apply(
            lambda x: {} if pd.isna(x) or x == "" else json.loads(x) if isinstance(x, str) else x
        )

        # Determine the slider keys from the first non-empty developsettings
        example = next((d for d in self.df["developsettings"] if isinstance(d, dict) and d.get("sliders")), {})
        if "sliders" not in example or not isinstance(example["sliders"], dict):
            raise ValueError("Each developsettings must contain a 'sliders' dict.")
        self.slider_keys = list(example["sliders"].keys())
        self.n_sliders = len(self.slider_keys)

        # We'll eventually want to flatten this out so that sliders aren't nested in a dict

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Load preview image
        img_name = row["name"]
        img_path = self.previews_dir / img_name
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        # Extract slider values from parsed developsettings
        # This will be easier once we figure out what values we need earlier on and send this fn
        # a flattened view of them so it won't have to do as much work
        develop_settings = row["developsettings"]
        slider_vals = [float(develop_settings["sliders"].get(k, 0.0)) for k in self.slider_keys]

        sliders = torch.tensor(slider_vals, dtype=torch.float32)
        return image, sliders


def train_model(
    csv_path: str,
    previews_dir: str,
    out_model_path: str,
    epochs: int = 5,
    batch_size: int = 32,
) -> Tuple[torch.nn.Module, List[float], List[str]]:
    """
    Train a slider-prediction model using the CSV and previews directory.
    Returns (model, losses, slider_cols).
    """
    # Load dataset: previews + developsettings sliders
    ds = PreviewDataset(Path(csv_path), Path(previews_dir))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, num_workers=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ResNetRegressor(n_outputs=ds.n_sliders).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    losses = []

    # Training loop
    for epoch in range(1, epochs + 1):
        print(f"... Starting epoch {epoch}")
        model.train()
        running_loss = 0.0

        for imgs, targets in loader:
            print(f"imgs: {imgs.shape}, targets: {targets.shape}")
            raise Exception("Stop here")
            imgs, targets = imgs.to(device), targets.to(device)
            optimizer.zero_grad()
            preds = model(imgs)
            loss = criterion(preds, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * imgs.size(0)

        avg_loss = running_loss / len(ds)
        losses.append(avg_loss)
        print(f"Epoch {epoch}/{epochs} - Loss: {avg_loss:.4f}")

    # Save final model checkpoint
    out_path = Path(out_model_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), str(out_path))
    print(f"Model saved to {out_path}")

    return model, losses, ds.slider_keys


"""
Invoke directly via CL from the project root like:

python -m modules.train \
    --csv /data/dataset/sliders.csv \
    --previews /data/previews \
    --out_model /data/models \
    --epochs 5 \
    --batch_size 32
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train slider prediction model.")
    parser.add_argument("--csv",       required=True, type=str, help="Path to dataset CSV")
    parser.add_argument("--previews",  required=True, type=str, help="Directory of previews")
    parser.add_argument("--out_model", required=True, type=str, help="Path to save model .pt")
    parser.add_argument("--epochs",    type=int,   default=5,   help="Number of epochs")
    parser.add_argument("--batch_size",type=int,   default=32,  help="Batch size")
    args = parser.parse_args()

    train_model(
        csv_path=args.csv,
        previews_dir=args.previews,
        out_model_path=args.out_model,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )

if __name__ == "__main__":
    main()