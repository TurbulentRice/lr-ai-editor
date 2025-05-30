"""
train.py
=========

Lightweight training script for the Lightroom-style slider-prediction model.

Expected directory layout (mounted via docker-compose):
    /mnt/previews/          JPEG previews   (e.g. DSC_0001.jpg …)
    /mnt/dataset/sliders.csv    CSV mapping image → slider values
    /mnt/models/            output checkpoint(s)

CSV must contain at least the columns:
    image, Exposure2012, Contrast2012, Shadows2012, Highlights2012,
    Whites2012, Blacks2012, Vibrance, Saturation
Feel free to add more sliders; the script will detect them automatically.

Example (inside container):
    python train.py \
        --csv /mnt/dataset/sliders.csv \
        --previews /mnt/previews \
        --out_model /mnt/models/model.pt \
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
# import torchvision.models as models
from tqdm import tqdm
from common.model import ResNetRegressor

torch.classes.__path__ = []  # Neutralizes the path inspection

# --------------------------------------------------------------------------- #
# Dataset
# --------------------------------------------------------------------------- #
class PreviewDataset(Dataset):
    def __init__(self, csv_path: Path, previews_dir: Path, transform=None):
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


# # --------------------------------------------------------------------------- #
# # Model - ResNet18 backbone with MLP head for regression
# # --------------------------------------------------------------------------- #
# class ResNetRegressor(nn.Module):
#     def __init__(self, n_outputs: int):
#         super().__init__()
#         self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
#         # Replace classification head
#         in_features = self.backbone.fc.in_features
#         self.backbone.fc = nn.Sequential(
#             nn.Linear(in_features, 256),
#             nn.ReLU(inplace=True),
#             nn.Linear(256, n_outputs),
#         )

#     def forward(self, x):
#         return self.backbone(x)


# --------------------------------------------------------------------------- #
# Training loop
# --------------------------------------------------------------------------- #
def train(
    model,
    loader,
    device,
    epochs: int,
    lr: float,
    out_model: Path,
    val_split: float = 0.1,
):
    n_total = len(loader.dataset)
    n_val = int(n_total * val_split)
    n_train = n_total - n_val
    train_ds, val_ds = torch.utils.data.random_split(loader.dataset, [n_train, n_val])

    train_loader = DataLoader(
        train_ds, batch_size=loader.batch_size, shuffle=True, num_workers=2
    )
    val_loader = DataLoader(
        val_ds, batch_size=loader.batch_size, shuffle=False, num_workers=2
    )

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_val = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{epochs}", ncols=80)
        for imgs, targets in pbar:
            imgs, targets = imgs.to(device), targets.to(device)

            optimizer.zero_grad()
            preds = model(imgs)
            loss = criterion(preds, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * imgs.size(0)
            pbar.set_postfix(loss=loss.item())

        avg_loss = total_loss / n_train

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for imgs, targets in val_loader:
                imgs, targets = imgs.to(device), targets.to(device)
                preds = model(imgs)
                val_loss += criterion(preds, targets).item() * imgs.size(0)
        val_loss /= n_val
        print(f"Epoch {epoch}: train={avg_loss:.4f}  val={val_loss:.4f}")

        # Checkpoint best model
        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), out_model)
            print(f"  ↳ New best model saved to {out_model} (val={best_val:.4f})")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def parse_args():
    p = argparse.ArgumentParser(description="Train slider prediction model.")
    p.add_argument("--csv", required=True, type=Path, help="Path to dataset CSV")
    p.add_argument("--previews", required=True, type=Path, help="Directory of previews")
    p.add_argument("--out_model", required=True, type=Path, help="Output .pt file")
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    ds = PreviewDataset(args.csv, args.previews)
    loader = DataLoader(ds, batch_size=args.batch_size, shuffle=True, num_workers=2)

    model = ResNetRegressor(n_outputs=len(ds.slider_cols)).to(device)
    print(f"Predicting {len(ds.slider_cols)} sliders: {ds.slider_cols}")

    args.out_model.parent.mkdir(parents=True, exist_ok=True)
    train(model, loader, device, args.epochs, args.lr, args.out_model)


if __name__ == "__main__":
    main()
    