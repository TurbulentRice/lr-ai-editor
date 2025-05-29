# import torch
import torch.nn as nn
import torchvision.models as models

# --------------------------------------------------------------------------- #
# Model - ResNet18 backbone with MLP head for regression
# --------------------------------------------------------------------------- #
class ResNetRegressor(nn.Module):
    def __init__(self, n_outputs: int):
        super().__init__()
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT, progress=False)
        # Replace classification head
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, n_outputs),
        )

    def forward(self, x):
        return self.backbone(x)