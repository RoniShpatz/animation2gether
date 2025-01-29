from django.contrib import messages
from django.shortcuts import redirect
from cloudinary import uploader
import os
from PIL import Image
import tempfile
from typing import List
from .models import TempFrame

def create_and_upload_animation(frames: List[TempFrame], frame_per_s: int) -> dict:
    """
    Creates an animated GIF from frames and uploads it to Cloudinary.
    
    Args:
        frames: List of TempFrame objects
        frame_per_s: Frames per second for the animation
    
    Returns:
        dict: Cloudinary upload response containing 'secure_url' and 'public_id'
    
    Raises:
        Exception: If there's an error during creation or upload
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save frames as images
        image_files = []
        for frame in frames:
            image_path = os.path.join(temp_dir, f'frame_{frame.frame_number}.png')
            # Read the file field content
            with open(image_path, 'wb') as f:
                f.write(frame.file.read())
                # Reset file pointer for next read
                frame.file.seek(0)
            image_files.append(image_path)
        
        # Create animated GIF
        images = []
        for image_file in image_files:
            images.append(Image.open(image_file))
        
        # Save as temporary GIF
        gif_path = os.path.join(temp_dir, 'animation.gif')
        duration = 1000 // frame_per_s  # Convert FPS to duration in milliseconds
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0
        )
    
        
        return gif_path