from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import os
from config import FACTS_PER_VIDEO, SECONDS_PER_FACT, FONT_SIZE, TEXT_COLOR, BOX_COLOR

def wrap_text(text, max_chars=30):
    """Wrap text into multiple lines"""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += (" " if current else "") + word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def create_text_image(text, video_width, video_height, is_hook=False):
    """Create a text overlay image"""
    img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Font size
    font_size = FONT_SIZE + 10 if is_hook else FONT_SIZE

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Wrap text
    lines = wrap_text(text, max_chars=25)

    # Calculate text block size
    line_height = font_size + 10
    total_height = line_height * len(lines) + 40
    max_width = max([draw.textlength(line, font=font) for line in lines]) + 60

    # Position in lower third
    box_x = (video_width - max_width) // 2
    box_y = video_height - total_height - 150

    # Draw semi-transparent background box
    box_img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box_img)
    box_draw.rectangle(
        [box_x - 10, box_y - 10, box_x + max_width + 10, box_y + total_height + 10],
        fill=BOX_COLOR
    )
    img = Image.alpha_composite(img, box_img)
    draw = ImageDraw.Draw(img)

    # Draw each line
    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        x = (video_width - line_width) // 2
        y = box_y + 20 + i * line_height

        # Shadow effect
        draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 255))
        # Main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))

    return np.array(img)

def add_text_overlay(video_path, content, output_path):
    """Add text overlays to video"""
    print("Adding text overlays...")

    with VideoFileClip(video_path) as video:
        w, h = video.size
        duration = video.duration

        clips = []

        # Hook text — first 4 seconds
        hook_text = content.get("hook", "You won't believe this!")
        hook_img = create_text_image(hook_text, w, h, is_hook=True)
        hook_clip = ImageClip(hook_img, ismask=False).set_duration(SECONDS_PER_FACT)

        # Facts — each shown for SECONDS_PER_FACT seconds
        fact_clips = []
        facts = content.get("facts", [])[:FACTS_PER_VIDEO]

        for fact in facts:
            fact_img = create_text_image(fact, w, h)
            fact_clip = ImageClip(fact_img, ismask=False).set_duration(SECONDS_PER_FACT)
            fact_clips.append(fact_clip)

        # Build video with text overlays timed correctly
        text_clips = [hook_clip] + fact_clips
        start_time = 0

        overlay_clips = [video]
        for text_clip in text_clips:
            overlay = text_clip.set_start(start_time).set_opacity(1)
            overlay_clips.append(overlay)
            start_time += SECONDS_PER_FACT
            if start_time >= duration:
                break

        final = CompositeVideoClip(overlay_clips)
        final = final.subclip(0, min(duration, 55))

        final.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

    print(f"Text overlay added: {output_path}")
    return output_path
