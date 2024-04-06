from .utils import align_int_value, clamp

import torch

class AdjustAndRoundDimensions:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 2560, "min": 1, "max": 8192, "step": 1}),
                "height": ("INT", {"default": 1440, "min": 1, "max": 8192, "step": 1}),
                "alignment": ("INT", {"default": 16, "min": 1, "max": 64, "step": 1}),                
                "factor": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 8.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "FLOAT", "INT", "INT", "INT")
    RETURN_NAMES = ("original_width", "original_height", 
                    "generation_width", "generation_height", 
                    "factor",
                    "min_value", "max_value",
                    "compression_factor")
    FUNCTION = "adjust_dimensions_with_min_max"

    CATEGORY = "Nimbus-Pack/Utils"

    @staticmethod
    def calculate_compression_factor(max_value, target=24):
        return max(1, round(max_value / target))
    
    def adjust_dimensions_with_min_max(self, width, height, alignment, factor):
        # Ensure the factor is at least 1 to prevent division by zero
        factor = max(1, factor)
        
        # Calculate new dimensions divided by factor and rounded to nearest multiple of 8
        adjusted_rounded_width = align_int_value(max(1, int(width / factor)), alignment)
        adjusted_rounded_height = align_int_value(max(1, int(height / factor)), alignment)
        
        # Determine the minimum and maximum values among the adjusted dimensions
        min_value = min(adjusted_rounded_width, adjusted_rounded_height)
        max_value = max(adjusted_rounded_width, adjusted_rounded_height)

        # Calculate the compression factor to approximate the max value to the target
        compression_factor = clamp(self.calculate_compression_factor(max_value), 32, 42)

        return (width, height, adjusted_rounded_width, adjusted_rounded_height, factor, min_value, max_value, compression_factor)



class AspectRatioMobileDevices:

    @classmethod
    def INPUT_TYPES(cls):
        resolutions = {
            "iPhone 14-15 Pro Max": (1290, 2796),
            "iPhone 14-15 Pro": (1179, 2556),
            "iPhone 13 Pro Max": (1284, 2778),
            "iPhone 13 Pro": (1170, 2532),
            "iPhone 13": (1170, 2532),
            "iPhone 13 Mini": (1080, 2340),
            "iPhone 12 Pro Max": (1284, 2778),
            "iPhone 12 Pro": (1170, 2532),
            "iPhone 12": (1170, 2532),
            "iPhone 12 Mini": (1080, 2340),
            "iPhone 11 Pro Max": (1242, 2688),
            "iPhone 11 Pro": (1125, 2436),
            "iPhone 11": (828, 1792),
            "iPad Pro 12.9-inch (5th generation)": (2048, 2732),
            "iPad Pro 11-inch (3rd generation)": (1668, 2388),
            "iPad Air (4th generation)": (1640, 2360),
            "iPad (9th generation)": (1620, 2160),
            "iPad Mini (6th generation)": (1488, 2266),
            "Samsung Galaxy Tab S7+": (2800, 1752),
        }

        # Generating the device_resolutions list from the keys of resolutions
        device_resolutions = [f"{device} - {res[0]}x{res[1]}" for device, res in resolutions.items()]

        return {
            "required": {
                "device_resolution": (device_resolutions,),
                "swap_dimensions": (["Off", "On"],),
                "upscale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "prescale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64})
            }
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT", "FLOAT", "INT", "LATENT", "STRING")
    RETURN_NAMES = ("width", "height", "upscale_factor", "prescale_factor", "batch_size", "empty_latent", "show_help")
    FUNCTION = "Adjust_Resolution_For_Mobile"
    CATEGORY = "Nimbus-Pack/Utils"

    def Adjust_Resolution_For_Mobile(self, device_resolution, swap_dimensions, upscale_factor, prescale_factor, batch_size):
        # Extracting the resolution from the selected device
        device_name, _, resolution = device_resolution.rpartition(" - ")
        width, height = map(int, resolution.split("x"))

        if swap_dimensions == "On":
            width, height = height, width

        width = int(width * prescale_factor)
        height = int(height * prescale_factor)

        latent = torch.zeros([batch_size, 4, height // 8, width // 8])
        show_help = ""

        return (width, height, upscale_factor, prescale_factor, batch_size, {"samples": latent}, show_help,)

class PopularScreenResolutions:

    @classmethod
    def INPUT_TYPES(cls):
        resolutions = {
            "Full HD (1080p)": (1920, 1080),
            "2K (QHD)": (2560, 1440),
            "4K (UHD)": (3840, 2160),
            "8K (UHD)": (7680, 4320),
            "iPhone 12/13/14 Pro Max": (1284, 2778),
            "Samsung Galaxy S22 Ultra": (1440, 3088),
            "Google Pixel 6": (1080, 2400),
            "OnePlus 9 Pro": (1440, 3216),
            "iPad Pro 12.9-inch": (2048, 2732),
            "MacBook Pro 16-inch": (3072, 1920),
            "Dell XPS 15": (3456, 2160),
            "Surface Laptop 4 (15\")": (2496, 1664),
        }

        # Generating the resolution options list from the keys of resolutions
        resolution_options = [f"{name} - {res[0]}x{res[1]}" for name, res in resolutions.items()]

        return {
            "required": {
                "screen_resolution": (resolution_options,),
                "swap_dimensions": (["Off", "On"],),
                "upscale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "prescale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64})
            }
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT", "FLOAT", "INT", "LATENT", "STRING")
    RETURN_NAMES = ("width", "height", "upscale_factor", "prescale_factor", "batch_size", "empty_latent", "show_help")
    FUNCTION = "Adjust_Screen_Resolution"
    CATEGORY = "Nimbus-Pack/Utils"

    def Adjust_Screen_Resolution(self, screen_resolution, swap_dimensions, upscale_factor, prescale_factor, batch_size):
        # Extracting the resolution from the selected screen option
        _, _, resolution_str = screen_resolution.partition(" - ")
        width, height = map(int, resolution_str.split("x"))

        if swap_dimensions == "On":
            width, height = height, width

        width = int(width * prescale_factor)
        height = int(height * prescale_factor)

        latent = torch.zeros([batch_size, 4, height // 8, width // 8])
        show_help = ""

        return (width, height, upscale_factor, prescale_factor, batch_size, {"samples": latent}, show_help,)
