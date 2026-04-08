import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ✅ Correct moviepy 1.0.3 imports — no moviepy.editor needed
from moviepy.video.VideoClip import VideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS

def get_font(size=80):
    """Load kids-friendly font or fallback"""
    font_paths = [
        "kids/assets/fonts/Fredoka_One/FredokaOne-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()

def apply_ken_burns(image_path, duration, zoom_direction="in"):
    """Apply Ken Burns zoom/pan effect to make image feel alive"""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
    img_array = np.array(img)

    def make_frame(t):
        progress = t / max(duration, 0.1)
        if zoom_direction == "in":
            scale = 1.0 + 0.08 * progress
            offset_x = int((scale - 1) * VIDEO_WIDTH * 0.5 * progress)
            offset_y = int((scale - 1) * VIDEO_HEIGHT * 0.5 * progress)
        else:
            scale = 1.08 - 0.08 * progress
            offset_x = int((scale - 1) * VIDEO_WIDTH * 0.5 * (1 - progress))
            offset_y = int((scale - 1) * VIDEO_HEIGHT * 0.5 * (1 - progress))

        new_w = int(VIDEO_WIDTH * scale)
        new_h = int(VIDEO_HEIGHT * scale)
        pil_img = Image.fromarray(img_array)
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
        left = max(0, min(offset_x, new_w - VIDEO_WIDTH))
        top = max(0, min(offset_y, new_h - VIDEO_HEIGHT))
        pil_img = pil_img.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
        return np.array(pil_img)

    return make_frame

def add_text_to_frame(frame, text, scene_number):
    """Add big colorful text overlay on a frame"""
    if not text or len(text.strip()) == 0:
        return frame

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    font = get_font(90)
    text = text.upper()[:40]

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except:
        text_w = len(text) * 50
        text_h = 100

    x = (VIDEO_WIDTH - text_w) // 2
    y = VIDEO_HEIGHT - text_h - 80

    # Shadow
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            draw.text((x + dx, y + dy), text, font=font, fill="black")

    # Colored text — different color per scene
    colors = ["#FFD700", "#FF6B35", "#FF1493", "#00CED1", "#7B68EE"]
    color = colors[scene_number % len(colors)]
    draw.text((x, y), text, font=font, fill=color)

    return np.array(pil_img)

def apply_fade(clip, fade_duration=0.5):
    """✅ Safe fade using crossfadein/crossfadeout — works in moviepy 1.0.3"""
    try:
        clip = clip.crossfadein(fade_duration)
        clip = clip.crossfadeout(fade_duration)
    except:
        pass  # skip fade if it fails, don't crash
    return clip

def build_scene_clip(scene, image_path, audio_path, audio_duration):
    """Build one animated scene clip with Ken Burns + text + audio"""
    scene_num = scene["scene_number"]
    text_overlay = scene.get("text_overlay", "")
    zoom_dir = "in" if scene_num % 2 == 0 else "out"
    duration = audio_duration + 0.5

    make_frame = apply_ken_burns(image_path, duration, zoom_dir)

    if text_overlay:
        def frame_with_text(t):
            frame = make_frame(t)
            if duration * 0.2 < t < duration * 0.85:
                frame = add_text_to_frame(frame, text_overlay, scene_num)
            return frame
        video_clip = VideoClip(frame_with_text, duration=duration).set_fps(FPS)
    else:
        video_clip = VideoClip(make_frame, duration=duration).set_fps(FPS)

    # Add audio
    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.set_audio(audio_clip)

    # ✅ Safe fade in/out
    video_clip = apply_fade(video_clip, fade_duration=0.5)

    print(f"  🎬 Scene {scene_num}: built ({duration:.1f}s)")
    return video_clip

def build_all_scenes(scenes, image_data, voice_data):
    """Build all scene clips"""
    print("🎬 Building scene clips...")

    image_map = {d["scene_number"]: d["image_path"] for d in image_data}
    voice_map = {d["scene_number"]: (d["audio_path"], d["duration"]) for d in voice_data}

    clips = []
    for scene in scenes:
        scene_num = scene["scene_number"]
        image_path = image_map.get(scene_num)
        audio_path, duration = voice_map.get(scene_num, (None, 40.0))

        if not image_path or not os.path.exists(image_path):
            print(f"  ⚠️  Skipping scene {scene_num}: missing image")
            continue

        try:
            clip = build_scene_clip(scene, image_path, audio_path, duration)
            clips.append(clip)
        except Exception as e:
            print(f"  ⚠️  Scene {scene_num} error: {e}")
            continue

    print(f"✅ Built {len(clips)} scene clips")
    return clips
    
