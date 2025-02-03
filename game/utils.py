from PIL import Image
import io
from typing import List
from django.core.files.base import ContentFile
from .models import TempFrame

def create_animation(frames: List[TempFrame], frame_per_s: int) -> ContentFile:
    """
    Creates an animated GIF from frames and returns it as an in-memory file.
    
    Args:
        frames: List of TempFrame objects
        frame_per_s: Frames per second for the animation
    
    Returns:
        ContentFile: In-memory GIF file that can be saved to a model field
    
    Raises:
        Exception: If there's an error during GIF creation
    """
    if not frames:
        raise Exception("No frames found to create animation.")
    
    images = []
    for frame in frames:
        # Open the frame
        original = Image.open(frame.file).convert("RGBA")  # Ensure transparency is handled
        
        # Create a white background
        white_bg = Image.new("RGBA", original.size, (255, 255, 255, 255))
        
        # Paste the frame onto the white background
        white_bg.paste(original, (0, 0), original)
        
        # Convert to RGB (no transparency) for GIF
        images.append(white_bg.convert("RGB"))

    # Set frame duration
    duration = int(1000 / frame_per_s)

    # Save GIF to an in-memory file
    gif_buffer = io.BytesIO()
    images[0].save(
        gif_buffer,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        optimize=True,
        duration=duration,
        loop=0
    )

    # Create a ContentFile for Django models
    gif_buffer.seek(0)  # Reset pointer to start of file
    return ContentFile(gif_buffer.getvalue(), name="animation.gif")