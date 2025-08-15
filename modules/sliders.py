def postprocess(slider_name: str, value: float, target_norm_meta: dict | None):
    if target_norm_meta and target_norm_meta.get("type") == "zscore":
        idx = target_norm_meta.get("index_map", {}).get(slider_name)
        if idx is not None:
            mean_list = target_norm_meta.get("mean", [])
            std_list = target_norm_meta.get("std", [])
            if idx < len(mean_list) and idx < len(std_list):
                mean = mean_list[idx]
                std = std_list[idx]
                value = value * std + mean
    spec = _get_spec_for_name(slider_name)
    if spec:
        if spec.get("min") is not None:
            value = max(spec["min"], value)
        if spec.get("max") is not None:
            value = min(spec["max"], value)
        if spec.get("step") is not None and spec["step"] > 0:
            value = round(value / spec["step"]) * spec["step"]
    return float(value)

def _get_spec_for_name(slider_name: str):
    # Direct lookup first
    spec = SLIDER_SPECS.get(slider_name)
    if spec is not None:
        return spec
    try:
        inv = {v: k for k, v in SLIDER_NAME_MAP.items()}
        mapped = SLIDER_NAME_MAP.get(slider_name)
        if isinstance(mapped, str):
            spec = SLIDER_SPECS.get(mapped)
            if spec is not None:
                return spec
        mapped_back = inv.get(slider_name)
        if isinstance(mapped_back, str):
            spec = SLIDER_SPECS.get(mapped_back)
            if spec is not None:
                return spec
    except Exception:
        pass
    return None


SLIDER_SPECS = {
    # Primary
    "Temperature": {"min": 2000.0, "max": 50000.0, "step": 1.0},
    "Tint": {"min": -150.0, "max": 150.0, "step": 1.0},
    "Exposure2012": {"min": -5.0, "max": 5.0, "step": 0.01},
    "Contrast2012": {"min": -100.0, "max": 100.0, "step": 1.0},
    "Whites2012": {"min": -100.0, "max": 100.0, "step": 1.0},
    "Highlights2012": {"min": -100.0, "max": 100.0, "step": 1.0},
    "Shadows2012": {"min": -100.0, "max": 100.0, "step": 1.0},
    "Blacks2012": {"min": -100.0, "max": 100.0, "step": 1.0},
    # Tone curve
    "ParametricHighlights": {"min": -100.0, "max": 100.0, "step": 1.0},
    "ParametricLights": {"min": -100.0, "max": 100.0, "step": 1.0},
    "ParametricDarks": {"min": -100.0, "max": 100.0, "step": 1.0},
    "ParametricShadows": {"min": -100.0, "max": 100.0, "step": 1.0},
    # Presence
    "Vibrance": {"min": -100.0, "max": 100.0, "step": 1.0},
    "Saturation": {"min": -100.0, "max": 100.0, "step": 1.0},
    # HSL - Hue
    "HueAdjustmentAqua": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentBlue": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentGreen": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentMagenta": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentOrange": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentPurple": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentRed": {"min": -100.0, "max": 100.0, "step": 1.0},
    "HueAdjustmentYellow": {"min": -100.0, "max": 100.0, "step": 1.0},
    # HSL - Saturation
    "SaturationAdjustmentAqua": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentBlue": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentGreen": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentMagenta": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentOrange": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentPurple": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentRed": {"min": -100.0, "max": 100.0, "step": 1.0},
    "SaturationAdjustmentYellow": {"min": -100.0, "max": 100.0, "step": 1.0},
    # HSL - Luminance
    "LuminanceAdjustmentAqua": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentBlue": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentGreen": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentMagenta": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentOrange": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentPurple": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentRed": {"min": -100.0, "max": 100.0, "step": 1.0},
    "LuminanceAdjustmentYellow": {"min": -100.0, "max": 100.0, "step": 1.0},
}


SLIDER_NAME_MAP = {
    # Primary sliders
    "temperature": "Temperature",
    "tint": "Tint",
    "exposure": "Exposure2012",
    "contrast": "Contrast2012",
    "whites": "Whites2012",
    "highlights": "Highlights2012",
    "shadows": "Shadows2012",
    "blacks": "Blacks2012",
    # Curve sliders
    "curve_highlights": "ParametricHighlights",
    "curve_lights": "ParametricLights",
    "curve_darks": "ParametricDarks",
    "curve_shadows": "ParametricShadows",
    # Presence sliders
    "vibrance": "Vibrance",
    "saturation": "Saturation",
    # HSL - Hue sliders
    "hue_adjust_aqua": "HueAdjustmentAqua",
    "hue_adjust_blue": "HueAdjustmentBlue",
    "hue_adjust_green": "HueAdjustmentGreen",
    "hue_adjust_magenta": "HueAdjustmentMagenta",
    "hue_adjust_orange": "HueAdjustmentOrange",
    "hue_adjust_purple": "HueAdjustmentPurple",
    "hue_adjust_red": "HueAdjustmentRed",
    "hue_adjust_yellow": "HueAdjustmentYellow",
    # HSL - Saturation
    "saturation_adjust_aqua": "SaturationAdjustmentAqua",
    "saturation_adjust_blue": "SaturationAdjustmentBlue",
    "saturation_adjust_green": "SaturationAdjustmentGreen",
    "saturation_adjust_magenta": "SaturationAdjustmentMagenta",
    "saturation_adjust_orange": "SaturationAdjustmentOrange",
    "saturation_adjust_purple": "SaturationAdjustmentPurple",
    "saturation_adjust_red": "SaturationAdjustmentRed",
    "saturation_adjust_yellow": "SaturationAdjustmentYellow",
    # HSL - Luminance
    "luminance_adjust_aqua": "LuminanceAdjustmentAqua",
    "luminance_adjust_blue": "LuminanceAdjustmentBlue",
    "luminance_adjust_green": "LuminanceAdjustmentGreen",
    "luminance_adjust_magenta": "LuminanceAdjustmentMagenta",
    "luminance_adjust_orange": "LuminanceAdjustmentOrange",
    "luminance_adjust_purple": "LuminanceAdjustmentPurple",
    "luminance_adjust_red": "LuminanceAdjustmentRed",
    "luminance_adjust_yellow": "LuminanceAdjustmentYellow",
}
