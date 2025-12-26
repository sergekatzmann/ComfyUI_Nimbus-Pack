import os
import torch
import numpy as np
from PIL import Image, ImageOps

class LoadImagesFromFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": ""}),
            },
        }

    @classmethod
    def IS_CHANGED(s, folder_path):
        return float("NaN")

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "load_images"
    CATEGORY = "Nimbus-Pack/Image"

    def load_images(self, folder_path):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        valid_extensions = ['.png', '.jpg', '.jpeg']
        image_files = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and 
               os.path.splitext(f)[1].lower() in valid_extensions
        ]
        
        image_files.sort()

        images = []
        for file_name in image_files:
            image_path = os.path.join(folder_path, file_name)
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            if img.mode == 'I':
                img = img.point(lambda i: i * (1 / 256)).convert('RGB')
            img = img.convert("RGB")
            img = np.array(img).astype(np.float32) / 255.0
            img = torch.from_numpy(img)[None,]
            images.append(img)

        if not images:
             # Return an empty tensor if no images found, though this might cause issues downstream if not handled.
             # Better to raise an error or return a dummy. For now, let's raise an error to alert the user.
             raise ValueError(f"No valid images found in {folder_path} with extensions {valid_extensions}")

        return (images,)
