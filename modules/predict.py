import torch
from PIL import Image
import torchvision.transforms as T
from modules.model import ResNetRegressor

def predict_sliders(uploaded_files, model_path: str, slider_cols):
    """
    Given a list of uploaded file-like objects, a path to a .pt model file, and
    a list of slider column names, return a list of (filename, results_dict).
    """
    results_list = []

    # Load the trained model
    model = ResNetRegressor(n_outputs=len(slider_cols))
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # Preprocessing transform (224x224 resize + normalize to tensor)
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
    ])

    # For each uploaded file, open, transform, predict
    for uploaded_file in uploaded_files:
        # Open and preprocess
        img = Image.open(uploaded_file).convert("RGB")
        tensor = transform(img).unsqueeze(0)  # add batch dimension

        # Forward pass
        with torch.no_grad():
            preds = model(tensor).detach().cpu().numpy()[0]

        # Build a dict mapping each slider to its predicted value
        results = {col: float(val) for col, val in zip(slider_cols, preds)}
        results_list.append((uploaded_file.name, results))

    return results_list
