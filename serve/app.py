"""
serve/app.py
============

FastAPI inference micro-service for Lightroom-style slider prediction.

Environment variables
---------------------
MODEL_PATH   Path to Torch checkpoint (default: /mnt/models/model.pt)
SLIDER_LIST  Comma-sep list of slider names, in the same order the model was
             trained on. Example:
             "Exposure2012,Contrast2012,Shadows2012,Highlights2012..."
"""

import io
import os
from pathlib import Path
from typing import List

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import torch
import torchvision.transforms as T

from common.model import ResNetRegressor  # reuse the model class

# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
MODEL_PATH = Path(os.getenv("MODEL_PATH", "/mnt/models/model.pt"))
SLIDER_LIST: List[str] = os.getenv(
    "SLIDER_LIST",
    "Exposure2012,Contrast2012,Shadows2012,Highlights2012,"
    "Whites2012,Blacks2012,Vibrance,Saturation",
).split(",")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRANSFORM = T.Compose(
    [
        T.Resize((224, 224)),
        T.ToTensor(),
    ]
)

# --------------------------------------------------------------------------- #
# Load model once
# --------------------------------------------------------------------------- #
if not MODEL_PATH.exists():
    raise RuntimeError(f"MODEL_PATH {MODEL_PATH} does not exist")

model = ResNetRegressor(len(SLIDER_LIST))
# state = torch.load(MODEL_PATH, map_location=DEVICE)
# model.load_state_dict(state)
# model.to(DEVICE).eval()

print(f"[serve] model loaded: {MODEL_PATH} - predicting {SLIDER_LIST}")

# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #
app = FastAPI(title="LR-AI-Editor Inference API")


@app.get("/ready")
def ready():
    return {"status": "ok"}


@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    return_xmp: bool = Query(False, description="Return XMP side-car as file"),
):
    # --- load image ---
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    img_bytes = await image.read()
    try:
        pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")
    
    return 200;

    # tensor = TRANSFORM(pil).unsqueeze(0).to(DEVICE)

    # # --- inference ---
    # with torch.no_grad():
    #     preds = model(tensor).cpu().numpy()[0]

    # sliders = {name: float(val) for name, val in zip(SLIDER_LIST, preds)}

    # if not return_xmp:
    #     return JSONResponse(sliders)

    # # --- generate XMP side-car ---
    # xmp = build_xmp(sliders)
    # return StreamingResponse(
    #     io.BytesIO(xmp.encode()),
    #     media_type="application/xml",
    #     headers={"Content-Disposition": 'attachment; filename="prediction.xmp"'},
    # )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def build_xmp(sliders: dict) -> str:
    """
    Tiny XML builder - creates a Lightroom-compatible DevelopSettings fragment.
    Extend as needed for more sliders!
    """
    slider_tags = "\n    ".join(
        f'<crs:{k}>{v:.4f}</crs:{k}>' for k, v in sliders.items()
    )
    return f"""<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"
           xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
       xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
    {slider_tags}
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""


# --------------------------------------------------------------------------- #
# Local dev entry
# --------------------------------------------------------------------------- #
# Allows: `python app.py` for quick local test without uvicorn CLI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

"""
serve/app.py

Stub server for LR-AI-Editor UI. Serves built frontend from '../ui/dist'.
"""

app = FastAPI(title="LR-AI-Editor UI Server")

# Mount the frontend build directory (relative to this file) at root
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "/app/ui/dist"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="ui")