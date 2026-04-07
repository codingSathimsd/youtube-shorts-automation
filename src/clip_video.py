from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import numpy as np
import os
from config import CLIP_DURATION, OUTPUT_DIR

def find_best_segment(video, clip_duration):
    duration = video.duration
    start_boundary = duration * 0.10
    end_boundary = duration * 0.90
    usable = end_boundary - start_boundary

    if usable <= clip_duration:
        return start_boundary, min(start_boundary + clip_duration, end_boundary)

    sample_count = 8
    segment_size = usable / sample_count
    best_start = start_boundary
    best_energy = 0

    for i in range(sample_count):
        sample_start = start_boundary + (i * segment_size)
        try:
            subclip = video.subclip(sample_start, sample_start + min(3, segment_size))
            if subclip.audio:
                audio_array = subclip.audio.to_soundarray(fps=22000)
                energy = float(np.mean(np.abs(audio_array)))
                if energy > best_energy:
                    best_energy = energy
                    best_start = sample_start
        except:
            continue

    return best_start, best_start + clip_duration

def reframe_to_vertical(clip):
    target_w, target_h = 1080, 1920
    scale = target_h / clip.h
    scaled = clip.resize(scale)
    if scaled.w > target_w:
        x_center = scaled.w / 2
        scaled = scaled.crop(
            x1=x_center - target_w / 2,
            x2=x_center + target_w / 2
        )
    bg = ColorClip((target_w, target_h), color=(0, 0, 0), duration=scaled.duration)
    final = CompositeVideoClip([bg, scaled.set_position('center')])
    return final

def create_clips(video_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clip_paths = []

    with VideoFileClip(video_path) as video:
        duration = video.duration
        print(f"Duration: {duration}s")

        if duration < CLIP_DURATION:
            start, end = 0, min(duration - 1, 54)
        else:
            start, end = find_best_segment(video, CLIP_DURATION)

        print(f"Clipping {start:.0f}s to {end:.0f}s")
        subclip = video.subclip(start, end)
        vertical = reframe_to_vertical(subclip)
        output_path = f"{OUTPUT_DIR}/clip_1.mp4"
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
