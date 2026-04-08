import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    concatenate_videoclips, AudioFileClip, CompositeAudioClip,
    VideoClip, concatenate_audioclips
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, OUTPUT_DIR, CHANNEL_NAME
from src.music_generator import generate_music_for_video

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

# ── Intro clip ────────────────────────────────────────────────────────────────

def create_intro_clip(episode_title, duration=5):
    """Create a branded animated intro clip"""
    def make_intro_frame(t):
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), '#FFD700')
        draw = ImageDraw.Draw(img)

        # Animated gradient background
        for i in range(VIDEO_HEIGHT):
            alpha = i / VIDEO_HEIGHT
            r = int(255 * (1 - alpha * 0.3))
            g = int(215 * (1 - alpha * 0.1))
            b = int(alpha * 120)
            draw.line([(0, i), (VIDEO_WIDTH, i)], fill=(r, g, b))

        # Bouncing stars
        for j in range(25):
            x = (j * 97 + int(t * 60)) % VIDEO_WIDTH
            y = (j * 73 + int(t * 40)) % VIDEO_HEIGHT
            size = 10 + (j % 6) * 8
            draw.ellipse([x, y, x + size, y + size], fill='white')

        font_large = get_font(120)
        font_small = get_font(55)

        # Channel name with shadow
        channel_text = CHANNEL_NAME
        try:
            bbox = draw.textbbox((0, 0), channel_text, font=font_large)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(channel_text) * 70
        x = (VIDEO_WIDTH - tw) // 2
        draw.text((x + 5, VIDEO_HEIGHT // 2 - 90 + 5), channel_text, font=font_large, fill='#CC6600')
        draw.text((x, VIDEO_HEIGHT // 2 - 90), channel_text, font=font_large, fill='white')

        # Episode title below
        short_title = episode_title[:50]
        try:
            bbox2 = draw.textbbox((0, 0), short_title, font=font_small)
            tw2 = bbox2[2] - bbox2[0]
        except:
            tw2 = len(short_title) * 32
        x2 = (VIDEO_WIDTH - tw2) // 2
        draw.text((x2, VIDEO_HEIGHT // 2 + 60), short_title, font=font_small, fill='#FFD700')

        return np.array(img)

    intro = VideoClip(make_intro_frame, duration=duration).set_fps(FPS)
    return intro

# ── Outro clip ────────────────────────────────────────────────────────────────

def create_outro_clip(duration=8):
    """Create an animated subscribe CTA outro"""
    def make_outro_frame(t):
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), '#FF4444')
        draw = ImageDraw.Draw(img)

        # Gradient background
        for i in range(VIDEO_HEIGHT):
            alpha = i / VIDEO_HEIGHT
            r = int(255 - alpha * 50)
            g = int(68 + alpha * 50)
            b = int(68 + alpha * 100)
            draw.line([(0, i), (VIDEO_WIDTH, i)], fill=(r, g, b))

        font = get_font(85)
        font_btn = get_font(58)

        # Main text
        lines = ["Thanks for watching! 🌟", "New video EVERY day!"]
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
            except:
                tw = len(line) * 48
            x = (VIDEO_WIDTH - tw) // 2
            draw.text((x + 3, 180 + i * 140 + 3), line, font=font, fill='#AA0000')
            draw.text((x, 180 + i * 140), line, font=font, fill='white')

        # Pulsing subscribe button
        pulse = 1.0 + 0.06 * np.sin(t * 3.5)
        btn_w = int(520 * pulse)
        btn_h = int(115 * pulse)
        btn_x = (VIDEO_WIDTH - btn_w) // 2
        btn_y = VIDEO_HEIGHT // 2 + 100
        draw.rounded_rectangle(
            [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
            radius=35, fill='#CC0000'
        )
        sub_text = "✅ SUBSCRIBE 🔔"
        try:
            bbox = draw.textbbox((0, 0), sub_text, font=font_btn)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(sub_text) * 34
        draw.text(((VIDEO_WIDTH - tw) // 2, btn_y + 28), sub_text, font=font_btn, fill='white')

        return np.array(img)

    outro = VideoClip(make_outro_frame, duration=duration).set_fps(FPS)
    return outro

# ── Final assembly ────────────────────────────────────────────────────────────

def assemble_final_video(scene_clips, episode_title, output_dir, topic_plan={}):
    """
    Assemble all scene clips into a final polished video with:
    - Branded intro
    - All scenes with Ken Burns + voice narration
    - Subscribe outro
    - Fresh AI-generated background music every day
    - Voice narration clearly mixed over soft background music
    """
    print("🎞️  Assembling final video...")
    os.makedirs(output_dir, exist_ok=True)
    final_path = os.path.join(output_dir, "final_video.mp4")

    # ── Step 1: Build full clip sequence ─────────────────────────────────────
    print("  📽️  Building clip sequence...")
    all_clips = []
    intro = create_intro_clip(episode_title, duration=5)
    all_clips.append(intro)
    all_clips.extend(scene_clips)
    outro = create_outro_clip(duration=8)
    all_clips.append(outro)

    print(f"  Concatenating {len(all_clips)} clips "
          f"(1 intro + {len(scene_clips)} scenes + 1 outro)...")
    final_video = concatenate_videoclips(all_clips, method="compose")
    video_duration = final_video.duration
    print(f"  ✅ Total video duration: {video_duration / 60:.1f} minutes")

    # ── Step 2: Generate fresh AI background music ────────────────────────────
    print("\n  🎵 Generating today's fresh background music...")
    music_path = generate_music_for_video(
        topic_plan=topic_plan,
        video_duration_seconds=video_duration,
        output_dir=output_dir
    )

    # ── Step 3: Mix voice narration + background music ────────────────────────
    if music_path and os.path.exists(music_path):
        try:
            print("  🎚️  Mixing voice narration + background music...")
            music = AudioFileClip(music_path)

            # Loop music if it's shorter than the video
            if music.duration < video_duration:
                loops = int(video_duration / music.duration) + 2
                music = concatenate_audioclips([music] * loops)

            # Trim music to exact video length
            music = music.subclip(0, video_duration)

            # Music very soft so voice is always crystal clear
            music = music.volumex(0.10)

            if final_video.audio:
                # Voice at full volume + music softly underneath
                final_audio = CompositeAudioClip([
                    final_video.audio.volumex(1.0),
                    music
                ])
                final_video = final_video.set_audio(final_audio)
                print("  ✅ Voice + music mixed successfully")
            else:
                # No voice track — use music only
                final_video = final_video.set_audio(music)
                print("  ✅ Background music set (no voice track found)")

        except Exception as e:
            print(f"  ⚠️  Music mixing error — continuing voice only: {e}")
    else:
        print("  ⚠️  Music generation failed — continuing with voice only")

    # ── Step 4: Render final video file ──────────────────────────────────────
    print(f"\n  🎬 Rendering final MP4 ({video_duration / 60:.1f} min)...")
    print("  ⏳ This takes 10-20 minutes on GitHub Actions — please wait...")

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

    # ── Step 5: Clean up temp music file ─────────────────────────────────────
    if music_path and os.path.exists(music_path):
        try:
            os.remove(music_path)
            print("  🧹 Temp music file cleaned up")
        except:
            pass

    print(f"\n✅ Final video ready!")
    print(f"   Path     : {final_path}")
    print(f"   Duration : {video_duration / 60:.1f} minutes")
    print(f"   File size: {os.path.getsize(final_path) / 1024 / 1024:.1f} MB")

    return final_path, video_duration

