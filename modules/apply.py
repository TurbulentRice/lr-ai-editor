from modules.lua import unserialize, serialize
from modules.sliders import SLIDER_NAME_MAP, postprocess
import sqlite3
import copy

def load_predictions(prediction_file_path: str) -> dict:
    """
    Reads the prediction CSV and returns a dict mapping filename stem (without extension) to a dict of predicted sliders.
    The CSV format is: first column is an unnamed index, second is 'stem', and the rest are predictions.
    """
    import pandas as pd
    df = pd.read_csv(prediction_file_path)
    if "stem" not in df.columns:
        raise ValueError("'stem' column not found in predictions CSV.")
    predictions = {
        row["stem"]: row.drop("stem").to_dict()
        for _, row in df.iterrows()
    }
    return predictions


def update_developsettings(existing_lua: str, new_sliders: dict) -> str:
    """
    Unpacks the existing Lua string, updates only the predicted sliders, and repacks it.
    """
    settings = unserialize(existing_lua)
    # Use a copy to avoid mutating input
    updated = copy.deepcopy(settings)
    for pred_name, pred_value in new_sliders.items():
        # Map to Lightroom slider name
        lr_name = SLIDER_NAME_MAP.get(pred_name)
        if not lr_name:
            continue
        # Postprocess to ensure bounds etc.
        value = postprocess(pred_name, pred_value, None)
        updated[lr_name] = value
    return serialize(updated)


def apply_predictions_to_catalog(lrcat_path: str, predictions: dict[str, dict]) -> int:
    """
    Connects to the SQLite catalog, updates Adobe_imageDevelopSettings.developSettings for images whose
    paths match prediction filenames (by stem), and returns the number of updated records.
    """
    conn = sqlite3.connect(lrcat_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Query to join AgLibraryFile, AgLibraryFolder, Adobe_images, Adobe_imageDevelopSettings
    # and get filename (AgLibraryFile.baseName), extension, and developSettings (Adobe_imageDevelopSettings.text), and the developsettings row id.
    c.execute("""
        SELECT
            AgLibraryFile.baseName,
            AgLibraryFile.extension,
            Adobe_imageDevelopSettings.text,
            Adobe_imageDevelopSettings.id_local
        FROM Adobe_images
        JOIN AgLibraryFile
            ON Adobe_images.rootFile = AgLibraryFile.id_local
        JOIN AgLibraryFolder
            ON AgLibraryFile.folder = AgLibraryFolder.id_local
        JOIN Adobe_imageDevelopSettings
            ON Adobe_images.id_local = Adobe_imageDevelopSettings.image
    """)
    rows = c.fetchall()
    updated = 0
    for row in rows:
        base_name = row["baseName"]
        extension = row["extension"]
        dev_settings = row["text"]
        dev_id = row["id_local"]
        # Compose stem to match predictions key (filename without extension)
        stem = base_name
        if stem not in predictions:
            continue
        # Update developSettings
        new_settings = update_developsettings(dev_settings, predictions[stem])
        c.execute(
            "UPDATE Adobe_imageDevelopSettings SET text = ? WHERE id_local = ?",
            (new_settings, dev_id)
        )
        updated += 1
    conn.commit()
    conn.close()
    return updated