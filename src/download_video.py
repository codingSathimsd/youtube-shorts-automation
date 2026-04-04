from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
import os
from config import CLIP_DURATION, CLIPS_PER_RUN, OUTPUT_DIR

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

    bg = ColorClip(
        (target_w, target_h),
        color=(0, 0, 0),
        duration=scaled.duration
    )
    final = CompositeVideoClip([bg, scaled.set_position('center')])
    return final

def create_clips(video_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clip_paths = []

    with VideoFileClip(video_path) as video:
        duration = video.duration
        print(f"Video duration: {duration}s")

        if duration < CLIP_DURATION:
            moments = [(0, min(duration - 1, 59))]
        else:
            clips_to_make = min(CLIPS_PER_RUN, int(duration // CLIP_DURATION))
            usable = duration * 0.9
            segment = usable / clips_to_make
            moments = []
            for i in range(clips_to_make):
                start = (i * segment) + (duration * 0.05)
                end = min(start + CLIP_DURATION, duration - 1)
                if end > start:
                    moments.append((start, end))

        for i, (start, end) in enumerate(moments):
            print(f"Creating clip {i+1}/{len(moments)}")
            subclip = video.subclip(start, end)
            vertical = reframe_to_vertical(subclip)
            output_path = f"{OUTPUT_DIR}/clip_{i+1}.mp4"
            vertical.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            clip_paths.append(output_path)
            print(f"Clip {i+1} saved")

    return clip_paths
