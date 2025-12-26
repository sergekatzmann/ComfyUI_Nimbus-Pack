import torch

class ImageExtractRect:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 100, "min": 1, "max": 8192, "step": 1}),
                "height": ("INT", {"default": 100, "min": 1, "max": 8192, "step": 1}),
                "corner": (["top-left", "top-right", "bottom-left", "bottom-right"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract_rect"
    CATEGORY = "Nimbus-Pack/Image"

    def extract_rect(self, image, width, height, corner):
        # image is [B, H, W, C]
        _, img_h, img_w, _ = image.shape
        
        # Determine start coordinates
        if corner == "top-left":
            start_x = 0
            start_y = 0
        elif corner == "top-right":
            start_x = img_w - width
            start_y = 0
        elif corner == "bottom-left":
            start_x = 0
            start_y = img_h - height
        elif corner == "bottom-right":
            start_x = img_w - width
            start_y = img_h - height
        
        # Ensure coordinates are within valid bounds (handle negative starts if width > img_w)
        start_x = max(0, min(start_x, img_w - width))
        start_y = max(0, min(start_y, img_h - height))
        
        # Ensure width/height don't exceed image dimensions
        valid_width = min(width, img_w - start_x)
        valid_height = min(height, img_h - start_y)
        
        crop = image[:, start_y:start_y+valid_height, start_x:start_x+valid_width, :]
        return (crop,)

class ImageCombineRect:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "destination_image": ("IMAGE",),
                "source_image": ("IMAGE",),
                "corner": (["top-left", "top-right", "bottom-left", "bottom-right"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "combine_rect"
    CATEGORY = "Nimbus-Pack/Image"

    def combine_rect(self, destination_image, source_image, corner):
        # dest: [B, H, W, C], source: [B_src, h, w, C]
        # We assume source fits into destination. Only one source image usually or simplified batching.
        
        dest_h, dest_w = destination_image.shape[1], destination_image.shape[2]
        src_h, src_w = source_image.shape[1], source_image.shape[2]
        
        # Determine paste coordinates
        if corner == "top-left":
            start_x = 0
            start_y = 0
        elif corner == "top-right":
            start_x = dest_w - src_w
            start_y = 0
        elif corner == "bottom-left":
            start_x = 0
            start_y = dest_h - src_h
        elif corner == "bottom-right":
            start_x = dest_w - src_w
            start_y = dest_h - src_h

        # Clamp start coordinates to be within destination
        # If source is larger than dest, this logic might be tricky. 
        # But per requirements/watermark workflow, it's usually smaller.
        # We will attempt to paste what fits.
        
        # Adjust start if negative (e.g. source wider than dest and right-aligned)
        paste_x = max(0, start_x)
        paste_y = max(0, start_y)
        
        # Calculate dimensions to paste
        paste_w = min(src_w, dest_w - paste_x)
        paste_h = min(src_h, dest_h - paste_y)
        
        if paste_w <= 0 or paste_h <= 0:
            return (destination_image,)

        # Create output clone
        output = destination_image.clone()
        
        # Handle batch broadcasting if needed. 
        # Case 1: Same batch size.
        # Case 2: Source has batch 1, Dest has batch N -> Broadcast source.
        # Case 3: Source N, Dest 1 -> Maybe error or broadcast dest? Comfy usually expands inputs.
        # For simplicity, we assume broadcasting works or they match.
        # However, manual slicing requires care with batches.
        
        # If sizes match in batch dim or one is 1
        src_batch = source_image.shape[0]
        dst_batch = destination_image.shape[0]
        
        # Source start offsets if we had to crop source (e.g. if start_x was negative)
        src_start_x = 0 if start_x >= 0 else -start_x
        src_start_y = 0 if start_y >= 0 else -start_y
        
        # This slice logic applies source[..., src_slice_y, src_slice_x, :] to output[..., dst_slice_y, dst_slice_x, :]
        # If batch dims differ, we loop? Comfy/Torch might handle assignment with broadcast but slices must match size.
        
        # Let's try direct assignment. If dimensions mismatch, it will raise error.
        # We take the relevant region from source
        source_region = source_image[:, src_start_y:src_start_y+paste_h, src_start_x:src_start_x+paste_w, :]
        
        if src_batch != dst_batch and src_batch == 1:
            source_region = source_region.expand(dst_batch, -1, -1, -1)
        
        output[:, paste_y:paste_y+paste_h, paste_x:paste_x+paste_w, :] = source_region
        
        return (output,)
