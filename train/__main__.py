"""
Invoke directly via CL from the project root like:
    python -m train \
        --csv /data/dataset/sliders.csv \
        --previews /data/previews \
        --out_model /data/models \
        --epochs 5 \
        --batch_size 32
"""

import argparse
from .train import train_model

def main():
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