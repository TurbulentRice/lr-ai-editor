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
from modules.sliders import SLIDER_NAME_MAP

PREVIEW_EXTS = [".jpg", ".jpeg", ".webp", ".png"]


torch.classes.__path__ = []  # Neutralizes the path inspection


# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
class PreviewDataset(Dataset):
    def __init__(
        self,
        csv_path: Path,
        previews_dir: Path,
        transform=None,
        selected_friendly_sliders: List[str] | None = None,
        slider_name_map: dict = SLIDER_NAME_MAP,
    ):
        """
        Dataset for loading image previews and their corresponding developsettings slider values.

        CSV must contain:
          - A 'name' column with image filenames (without extension or with extension as appropriate)
          - A 'developsettings' column containing a JSON string with {"sliders": { ... }}

        By default, uses all sliders defined in SLIDER_NAME_MAP. You can pass a subset via
        `selected_friendly_sliders` to train on only those.
        """
        self.df = pd.read_csv(csv_path, usecols=["name", "developsettings"])
        self.previews_dir = Path(previews_dir)
        self.transform = transform or T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                # optionally: T.Normalize(mean, std)
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

        # Verify structure has 'sliders' dict somewhere
        example = next((d for d in self.df["developsettings"] if isinstance(d, dict) and d.get("sliders")), {})
        if "sliders" not in example or not isinstance(example["sliders"], dict):
            raise ValueError("Each developsettings must contain a 'sliders' dict.")

        # Determine which sliders to use (friendly names) while preserving the canonical order
        self.slider_name_map = slider_name_map
        if not selected_friendly_sliders:
            selected_friendly_sliders = list(self.slider_name_map.keys())
        self.slider_friendly = [k for k in self.slider_name_map.keys() if k in selected_friendly_sliders]
        self.slider_raw = [self.slider_name_map[k] for k in self.slider_friendly]
        self.n_sliders = len(self.slider_friendly)
        if self.n_sliders == 0:
            raise ValueError("No sliders selected. Provide at least one slider to train on.")

        # ------------------------------------------------------------
        # Resolve preview file paths (recursive, case-insensitive, stem-aware)
        # 1) Try exact join (previews_dir / name)
        # 2) Try case-insensitive name match anywhere under previews_dir
        # 3) Try matching by stem regardless of extension/subfolder
        prev_dir = self.previews_dir
        preview_paths = []
        if prev_dir.exists():
            for ext in PREVIEW_EXTS:
                preview_paths.extend(prev_dir.rglob(f"*{ext}"))
        name_map = {p.name.lower(): p for p in preview_paths}
        stem_map = {}
        for p in preview_paths:
            key = p.stem.lower()
            # prefer first seen; don't overwrite to keep deterministic selection
            if key not in stem_map:
                stem_map[key] = p

        def _resolve_path(name: str) -> Path | None:
            raw = Path(str(name))
            # 1) exact join
            p1 = prev_dir / raw
            if p1.exists():
                return p1
            # 2) name/lower
            p2 = name_map.get(raw.name.lower())
            if p2 is not None and p2.exists():
                return p2
            # 3) stem
            p3 = stem_map.get(raw.stem.lower())
            if p3 is not None and p3.exists():
                return p3
            return None

        self.df["__preview_path"] = self.df["name"].astype(str).apply(_resolve_path)
        self.df["__exists"] = self.df["__preview_path"].apply(lambda p: p is not None and Path(p).exists())
        missing_ct = int((~self.df["__exists"]).sum())
        if missing_ct > 0:
            print(f"[PreviewDataset] Skipping {missing_ct} row(s) with missing previews under {self.previews_dir}")
        self.df = self.df[self.df["__exists"]].reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Load resolved preview image path
        img_path = Path(row["__preview_path"])  # resolved in __init__
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        # Extract selected slider values from parsed developsettings
        develop_settings = row.get("developsettings", {})
        sliders_src = develop_settings.get("sliders", {}) if isinstance(develop_settings, dict) else {}
        slider_vals = [float(sliders_src.get(raw_key, 0.0)) for raw_key in self.slider_raw]

        sliders = torch.tensor(slider_vals, dtype=torch.float32)
        return image, sliders


def train_model(
    csv_path: str,
    previews_dir: str,
    out_model_path: str,
    epochs: int = 5,
    batch_size: int = 32,
    selected_friendly_sliders: List[str] | None = None,
) -> Tuple[torch.nn.Module, List[float], List[str]]:
    """
    Train a slider-prediction model using the CSV and previews directory.
    Only the user-selected sliders (friendly names) are used.
    Returns (model, losses, slider_friendly_names_in_order).
    """
    # Load dataset: previews + selected developsettings sliders
    ds = PreviewDataset(
        Path(csv_path),
        Path(previews_dir),
        selected_friendly_sliders=selected_friendly_sliders,
    )
    # TODO: make num_workers configurable. Set to 0 for now to suppress streamlit runtime errors
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, num_workers=0)

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

    # Return friendly slider names in the exact order used for training
    return model, losses, ds.slider_friendly


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
    parser.add_argument(
        "--sliders",
        type=str,
        default="",
        help="Comma-separated list of slider names (friendly). Leave empty to use all.",
    )
    args = parser.parse_args()

    train_model(
        csv_path=args.csv,
        previews_dir=args.previews,
        out_model_path=args.out_model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        selected_friendly_sliders=[s.strip() for s in args.sliders.split(",") if s.strip()] or None,
    )

if __name__ == "__main__":
    main()
