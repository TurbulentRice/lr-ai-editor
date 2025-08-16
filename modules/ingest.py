"""
Unified data ingest logic callable from both CLI and Streamlit.
Lightweight data ingest script for reading multiple Lightroom .lrcat files
contents, decoding, parsing, and formatting into a single .csv dataset.
"""
from pathlib import Path
import pandas as pd
import json

from lrtools.lrcat import LRCatDB, LRCatException
from lrtools.lrselectgeneric import LRSelectException

from modules.lua import unserialize
from modules.xmp import decode_xmp_blob

# ---------------------------------------
# Ingest function
# ---------------------------------------
def ingest(catalog: Path, out_csv: Path = None, criteria: str = ""):
    lrtools_columns = "id, name, datecapt, camera, lens, iso, focal, aperture, speed, modcount, xmp"

    # Use Lightroom-SQL-tools to extract XMP and metadata
    try:
        lrdb = LRCatDB(str(catalog))
    except LRCatException as e:
        print(' ==> FAILED to open LRCatDB: %s' % e)
        return pd.DataFrame()

    # Retrieve column names for Adobe_imageDevelopSettings
    lrdb.cursor.execute("PRAGMA table_info(Adobe_imageDevelopSettings)")
    develop_settings_columns = [row[1] for row in lrdb.cursor.fetchall()]

    data = []
    try:
        rows = lrdb.lrphoto.select_generic(lrtools_columns, criteria).fetchall()
    except LRSelectException as e:
        print(' ==> FAILED to get catalog lrtools data: %s' % e)
        rows = []
            
    for row in rows:
        # Unpack row values
        values = dict(zip(lrtools_columns.split(', '), row))

        try:
            # Fetch develop settings for this image ID
            # Unfortunately, lrtools doesn't have methods for Adobe_imageDevelopSettings table cols,
            # so we have to use LRCatDB's underlying cursor to run our own SQL
            image_id = values.get("id")
            lrdb.cursor.execute(
                "SELECT * FROM Adobe_imageDevelopSettings WHERE image = ?", (image_id,)
            )
            develop_settings_row = lrdb.cursor.fetchone()
        except Exception as e:
            print(' ==> FAILED to get catalog develop settings data: %s' % e)

        values['developsettings'] = {}
        if develop_settings_row is not None:
            try:
                develop_settings = dict(zip(develop_settings_columns, develop_settings_row))

                # Slider data is under 'text' col, and is in a lua-like format
                # Parsing it is not cheap, and slows down ingest process significantly,
                # but this is really the most important data so it's necessary.
                slider_text = develop_settings.get("text")
                develop_settings['sliders'] = unserialize(slider_text[4:] if slider_text is not None and slider_text.startswith("s = ") else slider_text)
                del develop_settings['text']
                values['developsettings'] = json.dumps(develop_settings)
            except Exception as e:
                print(f" ==> WARNING: failed to parse sliders for image {image_id}: {e}")

        # Decompress XMP data under 'xmp' and replace
        raw_xmp = values.get("xmp", "")
        decoded = decode_xmp_blob(raw_xmp)
        # Save parsing for later
        # parsed = parse_xmp(decoded) if decoded else {}
        values["xmp"] = decoded

        data.append(values)

    df = pd.DataFrame(data)
    if out_csv is not None:
        df.to_csv(out_csv, index=False)

    return df


"""
Invoke directly via CL from the project root like:

python -m modules.ingest \
    --catalog /data/raw/catalog.lrcat \
    --out_csv /data/models \
    --criteria "flag=flagged,colorlabel=green"
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ingest Lightroom catalog data.")
    parser.add_argument("--catalog",    required=True, type=str, help="Path to LRCAT file")
    parser.add_argument("--out_csv",    required=True, type=str, help="Path to save dataset CSV")
    parser.add_argument("--criteria",   type=str,   default="", help="Comma-separated string of criteria")
    args = parser.parse_args()

    ingest(
        catalog=args.catalog,
        out_csv=args.out_csv,
        criteria=args.criteria,
    )

if __name__ == "__main__":
    main()
