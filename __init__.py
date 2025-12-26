import os
import subprocess
import importlib.util
import sys

import __main__

python = sys.executable

def is_installed(package, package_overwrite=None):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        pass

    package = package_overwrite or package

    if spec is None:
        print(f"Installing {package}...")
        command = f'"{python}" -m pip install {package}'
  
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=os.environ)

        if result.returncode != 0:
            print(f"Couldn't install\nCommand: {command}\nError code: {result.returncode}")

is_installed("moviepy")

from .image_fitting_node import ImageSquareAdapterNode
from .image_fit_resize_node import ImageResizeAndCropNode
from .resolution import AspectRatioMobileDevices, AdjustAndRoundDimensions, PopularScreenResolutions
from .load_images_node import LoadImagesFromFolder
from .number_range_node import NumberRangeNode
from .slider_comparison_node import SliderComparisonNode
from .auto_levels_node import AutoLevelsNode
from .math_operation_node import MathOperationNode

from .image_patch_nodes import ImageExtractRect, ImageCombineRect

NODE_CLASS_MAPPINGS = {
    "ImageSquareAdapterNode": ImageSquareAdapterNode,
    "ImageResizeAndCropNode": ImageResizeAndCropNode,
    "AdjustAndRoundDimensions": AdjustAndRoundDimensions,
    "AspectRatioMobileDevices": AspectRatioMobileDevices,
    "PopularScreenResolutions" : PopularScreenResolutions,
    "LoadImagesFromFolder": LoadImagesFromFolder,
    "NumberRangeNode": NumberRangeNode,
    "SliderComparisonNode": SliderComparisonNode,
    "AutoLevelsNode": AutoLevelsNode,
    "MathOperationNode": MathOperationNode,
    "ImageExtractRect": ImageExtractRect,
    "ImageCombineRect": ImageCombineRect
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSquareAdapterNode": "Image Square Adapter Node",
    "ImageResizeAndCropNode": "Image Resize And Crop Node",
    "AdjustAndRoundDimensions" : "Resolution for 2-Stage Upscale with crop",
    "AspectRatioMobileDevices" : "Aspect Ratio Mobile Devices",
    "PopularScreenResolutions": "Aspect Ratio Popular",
    "LoadImagesFromFolder": "Load Images From Folder",
    "NumberRangeNode": "Number Range",
    "SliderComparisonNode": "Slider Comparison (Video)",
    "AutoLevelsNode": "Auto Levels (Image)",
    "MathOperationNode": "Math Operation (Min/Max)",
    "ImageExtractRect": "Image Extract Rect",
    "ImageCombineRect": "Image Combine Rect"
}

__all__ = NODE_CLASS_MAPPINGS

print('\033[34mNimbus Nodes: \033[92mLoaded\033[0m')
