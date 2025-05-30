# Lightroom AI Editor

Teach a pre-trained AI model to edit like you with this tiny [Streamlit](https://streamlit.io/) app that runs locally and opens in your browser. Drag-and-drop images and Lightroom catalog files, train and save models, and create predictive edits. 

## Requirements

- Python 3.9+

To install dependencies, run one of the following:
```
# UNIX-like environments
./run.sh

# Cross-platform Python launcher
python run.py
```

## Ingest

Easy uploading and previewing of metadata files, images, and predictive edits.

## [Train](./train/)

This is leftover from when training was it's own service, and still has some useful stuff so leaving here for now.

```sh
docker-compose build train # add --build-arg BASE_IMAGE=... for GPU
docker-compose up -d train [-h] --csv CSV --previews PREVIEWS --out_model OUT_MODEL [--epochs EPOCHS] [--batch_size BATCH_SIZE] [--lr LR] []  
```

## Lightroom Tools

Using [Lightroom-SQL-tools](https://github.com/fdenivac/Lightroom-SQL-tools) to handle extracting data from `.lrcat` files.

See the [full .lrcat table schema here](./lrcat_schema.sql).

From my digging, the tables of interest are:
1.	`Adobe_AdditionalMetadata`
  - Column: xmp (TEXT) — contains the full XMP side-car XML for each image.
2.	`Adobe_imageDevelopSettings`
  - Columns: numeric fields like grayscale, hasPointColor, but not slider values (Lightroom moved to XMP). You can still pick up a handful of basic flags here, but the heavy lifting lives in the XMP.
3.	`AgHarvestedExifMetadata`
  - Columns: aperture, shutterSpeed, isoSpeedRating, cameraModelRef, dateYear/dateMonth/dateDay, etc.
