"""
Shared image transform builders for training and inference.
Keep preprocessing definitions in one place to prevent drift.
"""
from typing import Optional, Sequence
import torchvision.transforms as T

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

def get_preprocess_transform(
    size: int = 224,
    mean: Optional[Sequence[float]] = None,
    std: Optional[Sequence[float]] = None,
) -> T.Compose:
    """
    Build the canonical preprocessing transform used by both training and inference.

    Defaults align with current project behavior (Resize to square + ToTensor()).
    If `mean` and `std` are provided, a Normalize step is appended in that order.

    Args:
        size: Final square size fed to the model (HxW).
        mean: Optional per-channel mean for normalization.
        std:  Optional per-channel std  for normalization.
    Returns:
        A torchvision.transforms.Compose pipeline.
    """
    ops = [
        T.Resize((size, size)),
        T.ToTensor(),
    ]
    if mean is not None and std is not None:
        ops.append(T.Normalize(mean=mean, std=std))
    return T.Compose(ops)
