from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import pandas as pd


def predictions_to_dataframe(
    predictions: Iterable[Tuple[str, Dict[str, float]]]
) -> pd.DataFrame:
    """
    Convert predictions into a pandas DataFrame.

    Input format:
      predictions = [
        ("IMG_0001.jpg", {"Exposure2012": 0.3, "Contrast2012": -10, ...}),
        ("IMG_0002.jpg", {...}),
        ...
      ]

    Output columns:
      - 'stem' (filename without extension)
      - slider columns in the same order as produced by the model (as given by dict order)
    """
    rows: List[Dict[str, float]] = []
    slider_order: List[str] | None = None

    for name, result in predictions:
        stem = Path(name).stem
        if slider_order is None:
            # Preserve the exact order produced by predict_sliders (dict preserves insertion order)
            slider_order = list(result.keys())
        # Build row
        row: Dict[str, float] = {"stem": stem}
        for k in slider_order:
            row[k] = float(result.get(k, 0.0))
        rows.append(row)

    if slider_order is None:
        # No predictions; return empty frame with only 'stem' column
        return pd.DataFrame(columns=["stem"])

    cols = ["stem"] + slider_order
    df = pd.DataFrame(rows, columns=cols)
    return df


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to UTF-8 CSV bytes without the index.
    """
    return df.to_csv(index=False).encode("utf-8")


def save_predictions_csv(
    predictions: Iterable[Tuple[str, Dict[str, float]]],
    out_path: str | Path,
) -> Path:
    """
    Convenience function if caller wants to write a CSV to disk.
    """
    df = predictions_to_dataframe(predictions)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path