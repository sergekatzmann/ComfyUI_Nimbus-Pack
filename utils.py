from PIL import Image
import torch
import numpy as np

# Tensor to PIL
def tensor2pil(img):
    return Image.fromarray(np.clip(255. * img.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

# PIL to Tensor
def pil2tensor(img):
    return torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

def round_up_to_divisible_by_eight(value):
        return ((value + 7) // 8) * 8

def align_int_value(value, alignment):
        return ((value + (alignment-1)) // alignment) * alignment

def clamp(value, min_value, max_value):
    """Ensure value falls within the range [min_value, max_value]."""
    return max(min_value, min(value, max_value))
