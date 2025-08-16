from pathlib import Path
import torch
from PIL import Image
import torchvision.transforms as T
from modules.model import ResNetRegressor
from modules.transforms import get_preprocess_transform, IMAGENET_MEAN, IMAGENET_STD
from modules.sliders import postprocess
from typing import Callable, Optional, List, Tuple, Any

def inspect_model_file(model_path: str) -> dict[str, Any]:
    p = Path(model_path)
    if not p.exists():
        return {"exists": False}
    info = {"exists": True, "size": p.stat().st_size, "mtime": p.stat().st_mtime}
    try:
        obj = torch.load(p, map_location="cpu")
        if isinstance(obj, dict) and "weights" in obj and "metadata" in obj:
            info["package"] = True
            meta = obj.get("metadata", {}) or {}
            info["metadata"] = meta  # keep raw for detailed view (safe dict)
            # sliders
            sliders = meta.get("slider_friendly")
            if isinstance(sliders, list):
                info["num_sliders"] = len(sliders)
                info["slider_list"] = sliders
            # preprocess
            pp = meta.get("preprocess", {}) or {}
            if pp:
                info["preprocess"] = pp
            # normalization presence
            tn = meta.get("target_norm")
            info["has_target_norm"] = bool(tn)
            # app version if present
            if isinstance(meta, dict) and "app_version" in meta:
                info["app_version"] = meta["app_version"]
        else:
            info["raw_state_dict"] = True
            # Best-effort guess for output size
            if isinstance(obj, dict):
                n_out = None
                for k, v in obj.items():
                    try:
                        if isinstance(v, torch.Tensor):
                            if v.ndim == 2:
                                n_out = int(v.shape[0])
                            elif v.ndim == 1:
                                n_out = int(v.shape[0])
                    except Exception:
                        pass
                if n_out is not None:
                    info["guessed_n_outputs"] = n_out
        return info
    except Exception as e:
        info["error"] = str(e)
        return info

def _resolve_device(device_str: str) -> torch.device:
    device_str = (device_str or "auto").lower()
    if device_str == "cpu":
        return torch.device("cpu")
    if device_str == "gpu" or device_str == "cuda":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # auto
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_model(model_path: str, n_outputs: int, device: str = "auto") -> Tuple[torch.nn.Module, torch.device]:
    """Load a model on the requested device and return (model, device)."""
    dev = _resolve_device(device)
    model = ResNetRegressor(n_outputs=n_outputs)
    try:
        state = torch.load(model_path, map_location=dev)
    except Exception:
        state = torch.load(model_path, map_location="cpu")
        dev = torch.device("cpu")
    meta = {}
    weights = state
    if isinstance(state, dict) and "weights" in state and "metadata" in state:
        weights = state["weights"]
        meta = state.get("metadata", {})
    model.load_state_dict(weights)
    model._pkg_meta = meta
    model.to(dev)
    model.eval()
    return model, dev

def predict_sliders(
    uploaded_files,
    model_path: str,
    slider_cols,
    device: str = "auto",
    model: Optional[torch.nn.Module] = None,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
):
    """
    Given a list of uploaded file-like objects, a path to a .pt model file, and
    a list of slider column names, return a list of (filename, results_dict).
    The device parameter can be 'auto', 'cpu', or 'gpu' to select where to run the model.
    Uses context managers for image I/O and supports CPU/GPU via map_location.
    If the model package contains a slider list and preprocessing metadata,
    those are used by default and override inputs.
    """
    results_list = []

    # Determine device and load model if not provided
    if model is None:
        model, device_t = build_model(model_path, n_outputs=len(slider_cols), device=device)
    else:
        device_t = next(model.parameters()).device

    meta = getattr(model, "_pkg_meta", {}) or {}
    preprocess = meta.get("preprocess", {}) if isinstance(meta, dict) else {}
    size = int(preprocess.get("size", 224))
    mean = preprocess.get("mean")
    std = preprocess.get("std")

    if mean is None or std is None:
        mean = IMAGENET_MEAN
        std = IMAGENET_STD

    if isinstance(meta, dict) and meta.get("slider_friendly"):
        slider_cols = meta["slider_friendly"]

    # Shared preprocessing (kept in sync with training)
    transform = get_preprocess_transform(size=size, mean=mean, std=std)

    names: List[str] = []
    tensors: List[torch.Tensor] = []
    total = len(uploaded_files)
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            with Image.open(uploaded_file) as im:
              img = im.convert("RGB").copy()
            tensor = transform(img)
            tensors.append(tensor)
            names.append(uploaded_file.name)
        except Exception as e:
            # Skip problematic file but continue processing others
            names.append(getattr(uploaded_file, "name", f"file_{idx}"))
            tensors.append(None)
        if progress_cb:
            progress_cb(idx + 1, total, "preprocess")
    # Filter out Nones if any
    valid_pairs = [(n, t) for n, t in zip(names, tensors) if t is not None]
    if not valid_pairs:
        return []
    names, tensors = zip(*valid_pairs)
    batch = torch.stack(list(tensors), dim=0).to(device_t)
    with torch.no_grad():
        outputs = model(batch).detach().cpu().numpy()
    # Validate output size
    if outputs.shape[1] != len(slider_cols):
        raise RuntimeError(
            f"Model output size ({outputs.shape[1]}) does not match number of sliders ({len(slider_cols)}). "
            "Ensure the model and slider list come from the same training run."
        )
    if progress_cb:
        progress_cb(total, total, "inference")
    results_list = []
    target_norm_meta = meta.get("target_norm")
    for name, row in zip(names, outputs):
        results = {col: postprocess(col, float(val), target_norm_meta) for col, val in zip(slider_cols, row)}
        results_list.append((name, results))
    return results_list
