import os
import folder_paths
import numpy as np
from PIL import Image
try:
    from moviepy.editor import VideoClip
except ImportError:
    # MoviePy v2.0+
    from moviepy.video.VideoClip import VideoClip
from .utils import tensor2pil

class SliderComparisonNode:
    """
    A custom node for ComfyUI to create a video comparison of two images with a sliding divider.
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_before": ("IMAGE",),
                "image_after": ("IMAGE",),
                "video_duration": ("FLOAT", {"default": 10.0, "min": 1.0, "max": 60.0, "step": 0.1}),
                "frame_rate": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1}),
                "slider_color": ("STRING", {"default": "255,0,0"}),
                "slider_thickness": ("INT", {"default": 5, "min": 1, "max": 20, "step": 1}),
                "target_height": ("INT", {"default": 1080, "min": 100, "max": 4096, "step": 1}),
                "filename_prefix": ("STRING", {"default": "slider_comparison"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "create_comparison_video"
    CATEGORY = "Nimbus-Pack/Video"
    OUTPUT_NODE = True

    def resize_and_center_image(self, image1, image2, background_color=(0, 0, 0)):
        """
        Resize image1 to fit within the resolution of image2 while maintaining its aspect ratio,
        and paste it centered onto a canvas of the same resolution as image2.
        """
        canvas = Image.new("RGB", image2.size, color=background_color)

        img1_aspect = image1.width / image1.height
        img2_aspect = image2.width / image2.height

        if img1_aspect > img2_aspect:
            new_width = image2.width
            new_height = int(new_width / img1_aspect)
        else:
            new_height = image2.height
            new_width = int(new_height * img1_aspect)

        image1_resized = image1.resize((new_width, new_height), Image.LANCZOS)
        paste_position = ((image2.width - new_width) // 2, (image2.height - new_height) // 2)
        canvas.paste(image1_resized, paste_position)

        return canvas

    def resize_image_to_height(self, image, target_height):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        new_height = target_height
        new_width = int(new_height * aspect_ratio)
        return image.resize((new_width, new_height), Image.LANCZOS)

    def create_comparison_video(self, image_before, image_after, video_duration, frame_rate, slider_color, slider_thickness, target_height, filename_prefix="slider_comparison"):
        # Convert tensors to PIL images
        # Handle batch of images - take the first one if multiple are provided
        if len(image_before.shape) > 3 and image_before.shape[0] > 1:
             print(f"Warning: SliderComparisonNode received batch of {image_before.shape[0]} images for 'before'. Using the first one.")
        
        if len(image_after.shape) > 3 and image_after.shape[0] > 1:
             print(f"Warning: SliderComparisonNode received batch of {image_after.shape[0]} images for 'after'. Using the first one.")

        # tensor2pil handles the conversion. If input is a batch, it might return a list or handle single. 
        # The utils.py tensor2pil implementation:
        # return Image.fromarray(np.clip(255. * img.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
        # It squeezes, so if batch size is 1 it works. If batch size > 1, squeeze might not do what we want if we pass the whole batch.
        # Let's slice to be safe: image[0]
        
        pil_before = tensor2pil(image_before[0] if len(image_before.shape) > 3 else image_before)
        pil_after = tensor2pil(image_after[0] if len(image_after.shape) > 3 else image_after)

        # 1. Resize/Fit logic
        # We want to match them. Let's assume image_after is the "reference" for aspect ratio/canvas if they differ,
        # or we can just resize 'before' to match 'after'.
        # The prompt says "resolution need to be matched so it is exact".
        # Let's use the logic from main.py: resize_and_center_image(image1, image2)
        
        # Make sure they are RGB
        pil_before = pil_before.convert("RGB")
        pil_after = pil_after.convert("RGB")

        # Resize before to match after's canvas
        pil_before_fitted = self.resize_and_center_image(pil_before, pil_after)
        
        # Now resize both to target height
        pil_before_final = self.resize_image_to_height(pil_before_fitted, target_height)
        pil_after_final = self.resize_image_to_height(pil_after, target_height)

        # Convert to numpy for processing
        array_before = np.array(pil_before_final)
        array_after = np.array(pil_after_final)
        
        width = array_before.shape[1]
        num_frames = int(frame_rate * video_duration)
        
        # Parse slider color
        try:
            color_values = [int(c.strip()) for c in slider_color.split(',')]
            if len(color_values) != 3:
                raise ValueError
            line_color = color_values
        except:
            print(f"Invalid slider color '{slider_color}', defaulting to red.")
            line_color = [255, 0, 0]

        def make_frame(t):
            # Linear progress from 0 to 1 over the video duration
            progress = t / video_duration
            
            # Calculate divider position (0 to width)
            # Start (progress=0): divider at 0 (Show Before)
            # End (progress=1): divider at width (Show After)
            divider_position = int(progress * width)
            
            # Ensure divider stays within bounds
            divider_position = max(0, min(width, divider_position))

            # Start with the 'Before' image
            frame = np.copy(array_before)
            
            # Reveal the 'After' image from the left as the slider moves right
            if divider_position > 0:
                frame[:, :divider_position] = array_after[:, :divider_position]

            # Draw the slider line
            if 0 <= divider_position < width:
                # Ensure we don't go out of bounds with thickness
                start = max(0, divider_position)
                end = min(width, divider_position + slider_thickness)
                frame[:, start:end] = line_color

            return frame

        # Generate video
        # We can use MoviePy's VideoClip directly with make_frame, but main.py used ImageClip list.
        # VideoClip is more memory efficient for long videos.
        
        # Note: make_frame in VideoClip expects t in seconds.
        clip = VideoClip(make_frame, duration=video_duration)
        
        # Save
        filename = f"{filename_prefix}_{os.urandom(4).hex()}.mp4"
        full_output_path = os.path.join(self.output_dir, filename)
        
        clip.write_videofile(full_output_path, fps=frame_rate, bitrate="5000k", codec="libx264", audio=False, logger=None)
        
        return (full_output_path,)
