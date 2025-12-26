import argparse
from PIL import Image
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips

# Setup command line arguments
parser = argparse.ArgumentParser(
    description='Create a video comparison of two images, scaling to a specified height while maintaining aspect ratio.')
parser.add_argument('image1_path', type=str, help='Path to the first image')
parser.add_argument('image2_path', type=str, help='Path to the second image')
parser.add_argument('output_video_path', type=str, help='Path where the output video will be saved')
parser.add_argument('--target_height', type=int, default=1080,
                    help='Target height of the output video in pixels (e.g., 640, 720, 1080). Aspect ratio is preserved.')

# The target_resolution variable will be derived from the target_height argument
args = parser.parse_args()

def resize_and_center_image(image1, image2, background_color=(255, 255, 255)):
    """
    Resize image1 to fit within the resolution of image2 while maintaining its aspect ratio,
    and paste it centered onto a canvas of the same resolution as image2 with a specified background color.

    Args:
    - image1 (PIL.Image): The first input image.
    - image2 (PIL.Image): The second input image, which determines the canvas size.
    - background_color (tuple): The background color for the canvas in RGB.

    Returns:
    - PIL.Image: The resulting combined image.
    """
    # Create a canvas with the resolution of image2 and the specified background color
    canvas = Image.new("RGB", image2.size, color=background_color)

    # Calculate the new size for image1, maintaining its aspect ratio
    img1_aspect = image1.width / image1.height
    img2_aspect = image2.width / image2.height

    if img1_aspect > img2_aspect:
        # Image1 is wider than image2
        new_width = image2.width
        new_height = int(new_width / img1_aspect)
    else:
        # Image1 is taller than image2
        new_height = image2.height
        new_width = int(new_height * img1_aspect)

    # Resize image1 to fit within the canvas while maintaining its aspect ratio
    image1_resized = image1.resize((new_width, new_height), Image.LANCZOS)

    # Calculate the position to paste the resized image1 on the canvas, centered
    paste_position = ((image2.width - new_width) // 2, (image2.height - new_height) // 2)

    # Paste the resized image1 onto the canvas
    canvas.paste(image1_resized, paste_position)

    return canvas


def resize_image_to_height(image, target_height):
    # Calculate new dimensions
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height
    new_height = target_height
    new_width = int(new_height * aspect_ratio)
    return image.resize((new_width, new_height))


# Load and resize images
image1 = Image.open(args.image1_path)
image2 = Image.open(args.image2_path)

image1 = resize_and_center_image(image1, image2)

image1_resized = resize_image_to_height(image1, args.target_height)
image2_resized = resize_image_to_height(image2, args.target_height)

# Convert images to numpy arrays
image1_array = np.array(image1_resized)
image2_array = np.array(image2_resized)

# Parameters for animation
frame_rate = 30
video_duration = 30  # seconds, adjust if you want slower or faster animation
num_frames = frame_rate * video_duration
width = image1_resized.width


def make_frame(t):
    cycle_duration = video_duration / 4  # Four phases: reveal 2nd, reveal 1st, reveal 2nd, reveal 1st
    cycle_progress = (t % cycle_duration) / cycle_duration
    cycle_number = int(t // cycle_duration)

    if cycle_number == 1:  # Move line from right to left to reveal the first image
        divider_position = width - int(cycle_progress * width)
        frame = np.copy(image2_array)
        frame[:, divider_position:] = image1_array[:, divider_position:]
    elif cycle_number == 2:  # Start with the first image fully visible, then reveal the second
        divider_position = int(cycle_progress * width)
        frame = np.copy(image1_array)
        frame[:, :divider_position] = image2_array[:, :divider_position]
    elif cycle_number == 3:  # Move line from right to left to reveal the first image again
        divider_position = width - int(cycle_progress * width)
        frame = np.copy(image2_array)
        frame[:, divider_position:] = image1_array[:, divider_position:]
    else:  # Initial phase and default action: reveal the second image by moving right
        divider_position = int(cycle_progress * width)
        frame = np.copy(image1_array)
        frame[:, :divider_position] = image2_array[:, :divider_position]

    # Add a vertical line at the divider position. Adjust the color and width as needed.
    line_color = [255, 0, 0]  # Red line, change the RGB values as desired
    line_width = 5  # Adjust the width of the line as needed
    if 0 <= divider_position < width:  # To ensure the line is only drawn within bounds
        frame[:, divider_position:divider_position + line_width] = line_color

    return frame


# Generate video
video_clips = [ImageClip(make_frame(t / frame_rate)).set_duration(1 / frame_rate) for t in range(num_frames)]
final_clip = concatenate_videoclips(video_clips, method="compose")
final_clip.write_videofile(args.output_video_path, fps=frame_rate, bitrate="3000k", codec="libx264")
