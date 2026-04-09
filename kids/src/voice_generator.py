import os
import time
import asyncio
from pydub import AudioSegment

# Natural Microsoft Neural voices - sounds like real humans
VOICE_OPTIONS = [
    "en-US-AriaNeural",    # warm female - best for storytelling
    "en-US-JennyNeural",   # friendly female
    "en-US-GuyNeural",     # natural male narrator
    "en-GB-SoniaNeural",   # British female - sounds magical
    "en-US-AriaNeural",    # repeat Aria for consistency
]

PRIMARY_VOICE = "en-US-AriaNeural"

async def generate_voice_async(text, output_path, voice=PRIMARY_VOICE,
                                rate="+8%", pitch="+5Hz"):
    """Generate natural human-like voice using Microsoft Edge TTS (free)"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text   = text,
            voice  = voice,
            rate   = rate,
            pitch  = pitch
        )
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"    edge-tts error: {e}")
        return False

def generate_voice_for_scene(narration_text, scene_number, output_dir,
                              voice=PRIMARY_VOICE):
    """Generate voice for a single scene"""
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"scene_{scene_number:02d}_voice.mp3")

    # Clean text for natural speech
    clean = narration_text.strip()
    clean = ' '.join(clean.split())
    # Add natural pauses with commas where needed
    clean = clean.replace("! ", "! ... ").replace("? ", "? ... ")

    for attempt in range(3):
        try:
            # Run async in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                generate_voice_async(clean, audio_path, voice)
            )
            loop.close()

            if success and os.path.exists(audio_path) \
                    and os.path.getsize(audio_path) > 1000:
                audio    = AudioSegment.from_mp3(audio_path)
                duration = len(audio) / 1000.0
                print(f"  🎙️  Scene {scene_number}: {duration:.1f}s [{voice[:20]}]")
                return audio_path, duration
            else:
                print(f"  Attempt {attempt+1} failed, retrying...")
                time.sleep(2)

        except Exception as e:
            print(f"  Voice error attempt {attempt+1}: {e}")
            time.sleep(3)

    # Final fallback to gTTS if edge-tts fails
    print(f"  ⚠️  Falling back to gTTS for scene {scene_number}")
    try:
        from gtts import gTTS
        tts = gTTS(text=narration_text, lang='en', slow=False)
        tts.save(audio_path)
        audio    = AudioSegment.from_mp3(audio_path)
        duration = len(audio) / 1000.0
        print(f"  🎙️  Scene {scene_number}: {duration:.1f}s [gTTS fallback]")
        return audio_path, duration
    except Exception as e:
        print(f"  gTTS also failed: {e}")
        return None, 35.0

def generate_all_voices(scenes, output_dir):
    """Generate natural voices for all scenes"""
    print("🎙️  Generating natural human voices with Edge TTS...")
    voice_data = []

    for i, scene in enumerate(scenes):
        scene_num = scene["scene_number"]
        narration = scene["narration"]

        # Rotate voices for variety - makes it feel like a real show
        voice = VOICE_OPTIONS[i % len(VOICE_OPTIONS)]

        # Narrator scenes use warm tone, dialogue uses expressive tone
        if any(w in narration.lower() for w in ["said","asked","shouted","whispered"]):
            rate  = "+5%"
            pitch = "+8Hz"
        else:
            rate  = "+8%"
            pitch = "+5Hz"

        audio_path, duration = generate_voice_for_scene(
            narration, scene_num, output_dir, voice)

        voice_data.append({
            "scene_number": scene_num,
            "audio_path":   audio_path,
            "duration":     duration
        })
        time.sleep(0.5)  # polite rate limiting

    total = sum(v["duration"] for v in voice_data)
    print(f"✅ All voices done. Total: {total/60:.1f} minutes")
    return voice_data
    
