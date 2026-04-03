from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import os
import random
from config import CLIP_DURATION_MIN, CLIP_DURATION_MAX, CLIPS_PER_VIDEO

def find_best_moments(duration):
    """
    Simple viral moment detection:
    Avoids intros (first 20%) and outros (last 10%)
    Picks spread-out moments for variety
    """
    start_boundary = duration * 0.20
    end_boundary = duration * 0.90
    usable_duration = end_boundary - start_boundary
    
    clip_duration = random.randint(CLIP_DURATION_MIN, CLIP_DURATION_MAX)
    
    moments = []
    segment_size = usable_duration / CLIPS_PER_VIDEO
    
    for i in range(CLIPS_PER_VIDEO):
        segment_start = start_boundary + (i * segment_size)
        segment_end = segment_start + segment_size - clip_duration
        if segment_end > segment_start:
            start = random.uniform(segment_start, segment_end)
            moments.append((start, start + clip_duration))
    
    return moments

def reframe_to_vertical(clip):
    """Reframe horizontal video to 9:16 vertical (1080x1920)"""
    target_w, target_h = 1080, 1920
    
    # Scale to fill height
    scale = target_h / clip.h
    scaled = clip.resize(scale)
    
    # Crop to width
    if scaled.w > target_w:
        x_center = scaled.w / 2
        scaled = scaled.crop(
            x1=x_center - target_w/2,
            x2=x_center + target_w/2
        )
    
    # Add black background if needed
    bg = ColorClip((target_w, target_h), color=(0,0,0), duration=scaled.duration)
    final = CompositeVideoClip([bg, scaled.set_position('center')])
    
    return final

def create_clips(video_path, output_dir="output_clips"):
    """Create vertical short clips from long video"""
    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []
    
    with VideoFileClip(video_path) as video:
        moments = find_best_moments(video.duration)
        
        for i, (start, end) in enumerate(moments):
            print(f"Creating clip {i+1}/{len(moments)} ({start:.0f}s - {end:.0f}s)")
            
            subclip = video.subclip(start, end)
            vertical = reframe_to_vertical(subclip)
            
            output_path = f"{output_dir}/clip_{i+1}.mp4"
            vertical.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            clip_paths.append(output_path)
    
    return clip_paths
