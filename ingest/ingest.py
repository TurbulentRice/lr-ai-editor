from pathlib import Path
import pandas as pd

from lrtools.lrcat import LRCatDB, LRCatException
from lrtools.lrselectgeneric import LRSelectException

from common.helpers import decode_xmp_blob

# ---------------------------------------
# Ingest function
# ---------------------------------------
def ingest(catalog_path: Path, previews_dir: Path, out_csv: Path, criteria: str = ""):
    try:
        # Use Lightroom-SQL-tools to extract XMP and metadata
        lrdb = LRCatDB(str(catalog_path))
    except LRCatException as _e:
        print(' ==> FAILED: %s' % _e)

    columns = "name, datecapt, camera, lens, iso, focal, aperture, speed, modcount, xmp"
    # Use the criteria passed in; if empty, fetch all
    if criteria:
        rows = lrdb.lrphoto.select_generic(columns, criteria).fetchall()
    else:
        rows = lrdb.lrphoto.select_generic(columns).fetchall()

    data = []
    try:
        for row in rows:
            # Unpack row values
            values = dict(zip(columns.split(', '), row))
            # Decompress XMP data under 'xmp'
            raw_xmp = values.get("xmp", "")
            decoded = decode_xmp_blob(raw_xmp)
            # Save parsing for later
            # parsed = parse_xmp(decoded) if decoded else {}
            # Replace raw xmp string with decoded string
            values["xmp"] = decoded
            data.append(values)
    except LRSelectException as _e:
        print(' ==> FAILED: %s' % _e)

    df = pd.DataFrame(data)
    df.to_csv(out_csv, index=False)

    return df
