from PIL import Image
import torch
import numpy as np

from .utils import pil2tensor, tensor2pil


class ImageSquareAdapterNode:
    """
    A custom node for ComfyUI to fit an image into a square frame,
    resizing and padding it as necessary, with options for resampling, supersampling,
    and various fitting modes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "target_size": ("INT", {"default": 224, "min": 1, "max": 10000, "step": 1}),
                "fill_color": ("STRING", {"default": "255,255,255"}),
                "resampling": (["lanczos", "nearest", "bilinear", "bicubic"], {"default": "lanczos"}),
                "supersample": (["true", "false"], {"default": "false"}),
                "fitting_mode": (["none", "top", "bottom", "center"], {"default": "none"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "image_fit_in_square"

    CATEGORY = "Nimbus-Pack/Image"

    def image_fit_in_square(self, image, target_size=224, fill_color='255,255,255', resampling='lanczos',
                            supersample='false', fitting_mode='none'):
        scaled_images = []
        for img in image:
            scaled_images.append(
                self.apply_fit_image(tensor2pil(img), target_size, fill_color, resampling, supersample, fitting_mode))

        scaled_images = torch.cat(scaled_images, dim=0)

        return (scaled_images,)

    def apply_fit_image(self, image: Image.Image, target_size: int, fill_color: str, resample: str, supersample: str,
                        fitting_mode: str):
        # Convert fill_color string to tuple
        fill_color = tuple(map(int, fill_color.split(',')))

        # Define a dictionary of resampling filters
        resample_filters = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC,
            'lanczos': Image.LANCZOS
        }

        # Calculate scaling factor and new size
        scaling_factor = target_size / float(max(image.size))
        new_size = tuple([int(x * scaling_factor) for x in image.size])

        # Apply supersample if needed
        if supersample == 'true':
            image = image.resize((new_size[0] * 8, new_size[1] * 8), resample=resample_filters[resample])

        # Resize the image
        image = image.resize(new_size, resample=resample_filters[resample])

        # Adjust image fitting based on the mode
        if fitting_mode == 'none':
            # Current behavior - centering the image
            new_img = Image.new("RGB", (target_size, target_size), fill_color)
            position = ((target_size - new_size[0]) // 2, (target_size - new_size[1]) // 2)
            new_img.paste(image, position)
        else:
            # Resize width to target size, adjust height placement based on the fitting_mode
            width, height = image.size
            new_height = int(height * (target_size / float(width)))
            image = image.resize((target_size, new_height), resample=resample_filters[resample])
            new_img = Image.new("RGB", (target_size, target_size), fill_color)

            if fitting_mode == 'top':
                position = (0, 0)
            elif fitting_mode == 'bottom':
                position = (0, target_size - new_height)
            elif fitting_mode == 'center':
                position = (0, (target_size - new_height) // 2)

            new_img.paste(image, position)

        return pil2tensor(new_img)


NODE_CLASS_MAPPINGS = {
    "ImageSquareAdapterNode": ImageSquareAdapterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSquareAdapterNode": "Image Square Adapter Node"
}
