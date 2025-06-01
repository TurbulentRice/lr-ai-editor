"""
Unified training logic callable from both CLI and Streamlit.

Lightweight training script for the Lightroom-style slider-prediction model.

Example (inside container):
    python train.py \
        --csv /data/dataset/sliders.csv \
        --previews /data/previews \
        --out_model /data/models \
        --epochs 5 \
        --batch_size 32

"""
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
from typing import Tuple, List
from common.model import ResNetRegressor

torch.classes.__path__ = []  # Neutralizes the path inspection

# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
class PreviewDataset(Dataset):
    def __init__(self, csv_path: Path, previews_dir: Path, transform=None):
        """
        Dataset for loading image previews and their corresponding slider values.
        
        Args:
            csv_path (Path): Path to CSV file containing image names and slider values
            previews_dir (Path): Directory containing JPEG preview images
            transform (callable, optional): Transform to apply to images. Defaults to resize + ToTensor.
            
        The CSV must contain:
            - An 'image' column with image filenames (without extension)
            - One or more columns containing slider values as floats
            
        Example CSV format:
            image,Exposure2012,Contrast2012,Shadows2012
            DSC_0001,0.5,10.0,-15.0
            DSC_0002,-0.5,5.0,0.0
        """
        self.df = pd.read_csv(csv_path)
        self.previews_dir = Path(previews_dir)
        self.transform = transform or T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
            ]
        )

        # Identify slider columns (float) by excluding the "image" column
        self.slider_cols = [c for c in self.df.columns if c.lower() != "image"]
        if not self.slider_cols:
            raise ValueError("No slider columns found in CSV.")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.previews_dir / row["image"]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        sliders = torch.tensor(row[self.slider_cols].values, dtype=torch.float32)
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
    # Load dataset
    ds = PreviewDataset(Path(csv_path), Path(previews_dir))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, num_workers=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ResNetRegressor(n_outputs=len(ds.slider_cols)).to(device)
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

    return model, losses, ds.slider_cols


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train slider prediction model.")
    parser.add_argument("--csv", required=True, type=str, help="Path to dataset CSV")
    parser.add_argument("--previews", required=True, type=str, help="Directory of previews")
    parser.add_argument("--out_model", required=True, type=str, help="Path to save model .pt")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    model, losses, slider_cols = train_model(
        csv_path=args.csv,
        previews_dir=args.previews,
        out_model_path=args.out_model,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )