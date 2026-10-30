import torch
import torch.nn as nn
import math
import json

from diffusers import UNet2DConditionModel
import sys
import time
import numpy as np
import os
import zipfile


def load_inference_weights(model_factory, config, model_path):
    """Avoid allocating initialized parameters alongside the full checkpoint.

    ZIP checkpoints can stay file-backed until used. Legacy checkpoints still
    load safely with weights_only, but cannot use PyTorch's mmap option.
    No partially loaded model is returned if strict validation fails.
    """
    with torch.device("meta"):
        model = model_factory(**config)
    weights = torch.load(
        model_path, map_location="cpu", weights_only=True,
        mmap=zipfile.is_zipfile(model_path),
    )
    model.load_state_dict(weights, strict=True, assign=True)
    del weights
    if any(t.is_meta for t in list(model.parameters()) + list(model.buffers())):
        raise RuntimeError("Animation checkpoint left model tensors uninitialized.")
    return model.eval().requires_grad_(False)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model=384, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        b, seq_len, d_model = x.size()
        pe = self.pe[:, :seq_len, :]
        x = x + pe.to(x.device)
        return x
    
class UNet():
    def __init__(self, 
                 unet_config,
                 model_path,
                 use_float16=False,
                 device=None
        ):
        with open(unet_config, 'r') as f:
            unet_config = json.load(f)
        self.model = load_inference_weights(UNet2DConditionModel, unet_config, model_path)
        self.pe = PositionalEncoding(d_model=384)
        if device != None:
            self.device = device
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if use_float16:
            self.model = self.model.half()
        self.model.to(self.device)
    
if __name__ == "__main__":
    unet = UNet()
