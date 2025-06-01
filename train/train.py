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
from common.model import ResNetRegressor
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
        """
        self.df = pd.read_csv(csv_path)
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
            raise ValueError("CSV must contain a 'developsettings' column (JSON‐encoded).")

        # Parse developsettings JSON strings into Python dicts for each row
        parsed_list = []
        for raw in self.df["developsettings"]:
            if pd.isna(raw) or raw == "":
                parsed_list.append({})
            else:
                try:
                    parsed_list.append(json.loads(raw))
                except Exception:
                    parsed_list.append(eval(raw))
        self.df["__parsed"] = parsed_list

        # Determine the slider keys from the first non‐empty developsettings
        example = next((d for d in parsed_list if isinstance(d, dict) and d.get("sliders")), {})
        if "sliders" not in example or not isinstance(example["sliders"], dict):
            raise ValueError("Each developsettings must contain a 'sliders' dict.")
        self.slider_keys = list(example["sliders"].keys())
        self.n_sliders = len(self.slider_keys)

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
        devdict = row["__parsed"]
        slider_vals = []
        for k in self.slider_keys:
            slider_vals.append(float(devdict["sliders"].get(k, 0.0)))

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

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for imgs, targets in loader:
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
