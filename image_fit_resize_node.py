from PIL import Image
import torch
import numpy as np

# Assuming pil2tensor and tensor2pil are utility functions provided in your environment
from .utils import pil2tensor, tensor2pil


class ImageResizeAndCropNode:
    """
    A custom node for ComfyUI to fit an image into a specified frame,
    resizing and cropping it as necessary, with options for resampling, supersampling,
    and various alignment modes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 224, "min": 1, "max": 10000, "step": 1}),
                "height": ("INT", {"default": 224, "min": 1, "max": 10000, "step": 1}),
                "alignment": (["center", "left-top", "left-center", "left-bottom", "center-top", "center-center", "center-bottom", "right-top", "right-center", "right-bottom"], {"default": "center"}),
                "resampling": (["lanczos", "nearest", "bilinear", "bicubic"], {"default": "lanczos"}),
                "supersample": (["true", "false"], {"default": "false"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "image_resize_and_crop"

    CATEGORY = "Nimbus-Pack/Image"

    def image_resize_and_crop(self, image, width=224, height=224, alignment='center', resampling='lanczos',
                              supersample='false'):
        scaled_images = []
        for img in image:
            scaled_images.append(
                self.apply_resize_and_crop(tensor2pil(img), width, height, alignment, resampling, supersample))

        scaled_images = torch.cat(scaled_images, dim=0)

        return (scaled_images,)

    def apply_resize_and_crop(self, image: Image.Image, width: int, height: int, alignment: str, resample: str, supersample: str):
        # Define a dictionary of resampling filters
        resample_filters = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC,
            'lanczos': Image.LANCZOS
        }

        # Calculate the ratio and the size for scaling
        original_ratio = image.width / image.height
        target_ratio = width / height

        if original_ratio > target_ratio:
            # Image is wider than the target ratio
            new_height = height
            new_width = int(original_ratio * new_height)
        else:
            # Image is taller than the target ratio
            new_width = width
            new_height = int(new_width / original_ratio)

        # Apply supersample if needed
        if supersample == 'true':
            factor = 8  # Factor by which to scale up before scaling down
            image = image.resize((new_width * factor, new_height * factor), resample=resample_filters[resample])

        # Resize the image
        image = image.resize((new_width, new_height), resample=resample_filters[resample])

        # Determine cropping coordinates
        left, top = 0, 0

        if 'center' in alignment:
            left = (new_width - width) / 2
            top = (new_height - height) / 2
        if 'left' in alignment:
            left = 0
        elif 'right' in alignment:
            left = new_width - width
        if 'top' in alignment:
            top = 0
        elif 'bottom' in alignment:
            top = new_height - height

        right = left + width
        bottom = top + height

        # Crop the image
        image = image.crop((int(left), int(top), int(right), int(bottom)))

        return pil2tensor(image)
