import os
import time
from gtts import gTTS
from pydub import AudioSegment
from config import VOICE_LANG, VOICE_SLOW, OUTPUT_DIR

def generate_voice_for_scene(narration_text, scene_number, output_dir):
    """Generate voice audio for a single scene"""
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"scene_{scene_number:02d}_voice.mp3")

    try:
        tts = gTTS(text=narration_text, lang=VOICE_LANG, slow=VOICE_SLOW)
        tts.save(audio_path)
        # Get duration
        audio = AudioSegment.from_mp3(audio_path)
        duration = len(audio) / 1000.0  # seconds
        print(f"  🎙️  Scene {scene_number}: voice generated ({duration:.1f}s)")
        return audio_path, duration
    except Exception as e:
        print(f"  Voice error scene {scene_number}: {e}")
        time.sleep(2)
        try:
            tts = gTTS(text=narration_text, lang=VOICE_LANG, slow=VOICE_SLOW)
            tts.save(audio_path)
            audio = AudioSegment.from_mp3(audio_path)
            duration = len(audio) / 1000.0
            return audio_path, duration
        except Exception as e2:
            print(f"  Voice retry failed: {e2}")
            return None, 40.0  # fallback duration

def generate_all_voices(scenes, output_dir):
    """Generate voice for all scenes"""
    print("🎙️  Generating voice narrations...")
    voice_data = []

    for scene in scenes:
        scene_num = scene["scene_number"]
        narration = scene["narration"]

        # Clean text for TTS
        clean_text = narration.replace("!", " ").replace("?", " ").strip()
        clean_text = ' '.join(clean_text.split())

        audio_path, duration = generate_voice_for_scene(clean_text, scene_num, output_dir)
        voice_data.append({
            "scene_number": scene_num,
            "audio_path": audio_path,
            "duration": duration
        })
        time.sleep(0.5)  # avoid rate limiting

    total_duration = sum(v["duration"] for v in voice_data)
    print(f"✅ All voices generated. Total duration: {total_duration/60:.1f} minutes")
    return voice_data
  
