import os
from moviepy.video.VideoClip import VideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from src.animator import generate_frame, pick_character, FPS

def build_scene_clip(scene, audio_path, audio_duration, topic):
    scene_num  = scene["scene_number"] - 1
    text_over  = scene.get("text_overlay", "")
    duration   = audio_duration + 0.5

    def make_frame(t):
        return generate_frame(
            t=t,
            scene_number=scene_num,
            topic=topic,
            text_overlay=text_over
        )

    clip = VideoClip(make_frame, duration=duration).set_fps(FPS)

    if audio_path and os.path.exists(audio_path):
        clip = clip.set_audio(AudioFileClip(audio_path))

    try:
        clip = clip.crossfadein(0.4).crossfadeout(0.4)
    except:
        pass

    char_name, _ = pick_character(topic)
    print(f"  🎬 Scene {scene_num+1}: {char_name} | {duration:.1f}s")
    return clip

def build_all_scenes(scenes, image_data, voice_data, topic=""):
    print("🎬 Building animated scenes...")
    voice_map = {d["scene_number"]: (d["audio_path"], d["duration"])
                 for d in voice_data}
    clips = []
    for scene in scenes:
        sn = scene["scene_number"]
        audio_path, duration = voice_map.get(sn, (None, 40.0))
        try:
            clip = build_scene_clip(scene, audio_path, duration, topic)
            clips.append(clip)
        except Exception as e:
            print(f"  ⚠️ Scene {sn} error: {e}")
    print(f"✅ Built {len(clips)} animated scenes")
    return clips
    
