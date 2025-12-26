import torch
import numpy as np

class AutoLevelsNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "black_point": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 49.0, "step": 0.1, "display": "number", "tooltip": "Percentage of darkest pixels to clip to black"}),
                "white_point": ("FLOAT", {"default": 99.0, "min": 51.0, "max": 100.0, "step": 0.1, "display": "number", "tooltip": "Percentage of brightest pixels to clip to white"}),
                "channel_independent": ("BOOLEAN", {"default": True, "label_on": "Channel Independent (Auto Levels)", "label_off": "Global (Auto Contrast)", "tooltip": "Calculate levels per channel (rebalances color) or globally (maintains color balance)"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_auto_levels"

    CATEGORY = "Nimbus-Pack/Image Enhancement"

    def apply_auto_levels(self, image, black_point, white_point, channel_independent):
        # image is [B, H, W, C] tensor in range [0, 1]
        
        # Convert to numpy for easier percentile handling
        img_np = image.cpu().numpy()
        
        # Prepare output array
        out_np = np.empty_like(img_np)
        
        # Process each image in batch independently
        for i in range(img_np.shape[0]):
            img = img_np[i] # [H, W, C]
            
            if channel_independent:
                # Apply per channel
                for c in range(img.shape[2]):
                    channel_data = img[:, :, c]
                    
                    # Calculate percentiles
                    # black_point is e.g. 1.0 -> 1st percentile
                    # white_point is e.g. 99.0 -> 99th percentile
                    p_low, p_high = np.percentile(channel_data, (black_point, white_point))
                    
                    # Avoid division by zero
                    if p_high > p_low:
                        # Stretch contrast
                        # Formula: (x - min) * (new_max - new_min) / (max - min) + new_min
                        # We map [p_low, p_high] to [0.0, 1.0]
                        channel_data = (channel_data - p_low) / (p_high - p_low)
                    else:
                        # If image is flat color, centering it might be weird, but let's just 
                        # clamp it or leave it. If max == min, we can't stretch.
                        # Usually we can just shift it to 0 or leave it. 
                        # Let's subtract min and clip.
                        channel_data = channel_data - p_low
                    
                    out_np[i, :, :, c] = channel_data
            else:
                # Global calculation across all channels for this image
                p_low, p_high = np.percentile(img, (black_point, white_point))
                
                if p_high > p_low:
                    out_np[i] = (img - p_low) / (p_high - p_low)
                else:
                    out_np[i] = img - p_low

        # Clip final result to ensure we stay in valid range, though we mapped to 0-1 theoretically, 
        # outliers outside the percentiles will be <0 or >1
        out_np = np.clip(out_np, 0.0, 1.0)
        
        # Convert back to tensor
        return (torch.from_numpy(out_np),)
