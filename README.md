Lightroom AI Editor

## Ingest

```sh
docker-compose build ingest
docker-compose up -d --build ingest [-h] [--catalog CATALOG] [--out_csv OUT_CSV] [--previews_dir PREVIEWS_DIR]
```

## Train

```sh
docker-compose build train # add --build-arg BASE_IMAGE=... for GPU
docker-compose up train [-h] --csv CSV --previews PREVIEWS --out_model OUT_MODEL [--epochs EPOCHS] [--batch_size BATCH_SIZE] [--lr LR] []  
```

## Notes
•	Volumes - shared ./data folder keeps artefacts on your host so containers stay disposable.
•	GPU - remove the devices stanza if you only have CPU.

## Serve

```sh
docker-compose up --build serve --build-arg BASE_IMAGE=pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
curl -F image=@/path/to/test.jpg "http://localhost:8000/predict"
# or request an XMP:
curl -o out.xmp -F image=@test.jpg "http://localhost:8000/predict?return_xmp=1"
```
