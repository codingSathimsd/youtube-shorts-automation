import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ✅ Safe moviepy imports that work on moviepy==1.0.3
try:
    from moviepy.editor import (
        VideoClip, AudioFileClip, CompositeAudioClip,
        concatenate_videoclips, concatenate_audioclips
    )
except ImportError:
    from moviepy.video.VideoClip import VideoClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
    from moviepy.video.compositing.concatenate import concatenate_videoclips

from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, CHANNEL_NAME
from src.music_generator import generate_music_for_video


def get_font(size=80):
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


# ── Intro ─────────────────────────────────────────────────────────────────────

def create_intro_clip(episode_title, duration=5):
    def make_frame(t):
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), '#FFD700')
        draw = ImageDraw.Draw(img)
        for i in range(VIDEO_HEIGHT):
            alpha = i / VIDEO_HEIGHT
            draw.line(
                [(0, i), (VIDEO_WIDTH, i)],
                fill=(
                    int(255 * (1 - alpha * 0.3)),
                    int(215 * (1 - alpha * 0.1)),
                    int(alpha * 120)
                )
            )
        for j in range(25):
            x = (j * 97 + int(t * 60)) % VIDEO_WIDTH
            y = (j * 73 + int(t * 40)) % VIDEO_HEIGHT
            size = 10 + (j % 6) * 8
            draw.ellipse([x, y, x + size, y + size], fill='white')

        font_large = get_font(120)
        font_small = get_font(55)

        try:
            bbox = draw.textbbox((0, 0), CHANNEL_NAME, font=font_large)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(CHANNEL_NAME) * 70
        cx = (VIDEO_WIDTH - tw) // 2
        draw.text((cx + 5, VIDEO_HEIGHT // 2 - 90 + 5), CHANNEL_NAME, font=font_large, fill='#CC6600')
        draw.text((cx, VIDEO_HEIGHT // 2 - 90), CHANNEL_NAME, font=font_large, fill='white')

        short = episode_title[:50]
        try:
            bbox2 = draw.textbbox((0, 0), short, font=font_small)
            tw2 = bbox2[2] - bbox2[0]
        except:
            tw2 = len(short) * 32
        cx2 = (VIDEO_WIDTH - tw2) // 2
        draw.text((cx2, VIDEO_HEIGHT // 2 + 60), short, font=font_small, fill='#FFD700')
        return np.array(img)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── Outro ─────────────────────────────────────────────────────────────────────

def create_outro_clip(duration=8):
    def make_frame(t):
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), '#FF4444')
        draw = ImageDraw.Draw(img)
        for i in range(VIDEO_HEIGHT):
            alpha = i / VIDEO_HEIGHT
            draw.line(
                [(0, i), (VIDEO_WIDTH, i)],
                fill=(
                    int(255 - alpha * 50),
                    int(68 + alpha * 50),
                    int(68 + alpha * 100)
                )
            )

        font = get_font(85)
        font_btn = get_font(58)

        for i, line in enumerate(["Thanks for watching! 🌟", "New video EVERY day!"]):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
            except:
                tw = len(line) * 48
            x = (VIDEO_WIDTH - tw) // 2
            draw.text((x + 3, 180 + i * 140 + 3), line, font=font, fill='#AA0000')
            draw.text((x, 180 + i * 140), line, font=font, fill='white')

        pulse = 1.0 + 0.06 * np.sin(t * 3.5)
        bw = int(520 * pulse)
        bh = int(115 * pulse)
        bx = (VIDEO_WIDTH - bw) // 2
        by = VIDEO_HEIGHT // 2 + 100
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=35, fill='#CC0000')

        sub = "SUBSCRIBE 🔔"
        try:
            bbox = draw.textbbox((0, 0), sub, font=font_btn)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(sub) * 34
        draw.text(((VIDEO_WIDTH - tw) // 2, by + 28), sub, font=font_btn, fill='white')
        return np.array(img)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── Master function (this is what main.py imports) ────────────────────────────

def assemble_final_video(scene_clips, episode_title, output_dir, topic_plan={}):
    """
    Assemble all scene clips into a complete final video.
    Includes: branded intro + all scenes + subscribe outro + AI music.
    """
    print("🎞️  Assembling final video...")
    os.makedirs(output_dir, exist_ok=True)
    final_path = os.path.join(output_dir, "final_video.mp4")

    # ── Step 1: Build clip list ───────────────────────────────────────────────
    print("  📽️  Building clip sequence...")
    all_clips = []
    all_clips.append(create_intro_clip(episode_title, duration=5))
    all_clips.extend(scene_clips)
    all_clips.append(create_outro_clip(duration=8))

    print(f"  Concatenating {len(all_clips)} clips "
          f"(1 intro + {len(scene_clips)} scenes + 1 outro)...")
    final_video = concatenate_videoclips(all_clips, method="compose")
    video_duration = final_video.duration
    print(f"  ✅ Total duration: {video_duration / 60:.1f} minutes")

    # ── Step 2: Generate fresh AI background music ────────────────────────────
    print("\n  🎵 Generating fresh background music...")
    music_path = generate_music_for_video(
        topic_plan=topic_plan,
        video_duration_seconds=video_duration,
        output_dir=output_dir
    )

    # ── Step 3: Mix voice + music ─────────────────────────────────────────────
    if music_path and os.path.exists(music_path):
        try:
            print("  🎚️  Mixing voice + music...")
            music = AudioFileClip(music_path)
            if music.duration < video_duration:
                loops = int(video_duration / music.duration) + 2
                music = concatenate_audioclips([music] * loops)
            music = music.subclip(0, video_duration)
            music = music.volumex(0.10)  # soft music, voice stays clear

            if final_video.audio:
                final_audio = CompositeAudioClip([
                    final_video.audio.volumex(1.0),
                    music
                ])
                final_video = final_video.set_audio(final_audio)
                print("  ✅ Voice + music mixed")
            else:
                final_video = final_video.set_audio(music)
                print("  ✅ Music added (no voice track)")
        except Exception as e:
            print(f"  ⚠️  Music mix error (voice only): {e}")
    else:
        print("  ⚠️  Music failed — voice only")

    # ── Step 4: Render ────────────────────────────────────────────────────────
    print(f"\n  🎬 Rendering {video_duration / 60:.1f} min video...")
    final_video.write_videofile(
        final_path,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        bitrate='4000k',
        audio_bitrate='192k',
        threads=4,
        preset='fast',
        logger=None
    )

    # ── Step 5: Cleanup ───────────────────────────────────────────────────────
    if music_path and os.path.exists(music_path):
        try:
            os.remove(music_path)
        except:
            pass

    size_mb = os.path.getsize(final_path) / 1024 / 1024
    print(f"\n✅ Final video ready!")
    print(f"   Duration : {video_duration / 60:.1f} minutes")
    print(f"   Size     : {size_mb:.1f} MB")
    print(f"   Path     : {final_path}")
    return final_path, video_duration
            
