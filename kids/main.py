import os
import sys
import shutil
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR
from src.researcher import research_today
from src.script_writer import write_full_script
from src.voice_generator import generate_all_voices
from src.image_generator import generate_all_images, generate_thumbnail_image
from src.scene_builder import build_all_scenes
from src.video_assembler import assemble_final_video
from src.seo_engine import generate_viral_seo
from src.uploader import upload_video, log_upload
from src.analyzer import analyze_performance
from src.learner import run_learning_cycle

def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()

def cleanup():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_secrets():
    # ✅ GROQ only — no Gemini
    required = ["GROQ_API_KEY", "YOUTUBE_CLIENT_ID",
                "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"❌ Missing secrets: {missing}")
        return False
    print("✅ All secrets present")
    return True

def morning_pipeline():
    """Morning job: Research → Script → Produce → Upload"""
    print("\n" + "="*60)
    print(f"🌅 KidsViral AI - Morning Pipeline")
    print(f"📅 {datetime.now().strftime('%B %d, %Y %H:%M UTC')}")
    print("="*60)

    load_env()
    if not check_secrets():
        sys.exit(1)

    cleanup()
    output_dir = OUTPUT_DIR

    try:
        # STEP 1: Research trends
        print("\n[1/7] 🔍 Researching trends...")
        topic_plan = research_today()
        print(f"  Topic: {topic_plan['topic']}")

        # STEP 2: Write full script
        print("\n[2/7] ✍️  Writing episode script...")
        script = write_full_script(topic_plan)
        scenes = script["scenes"]

        # STEP 3: Generate all images
        print("\n[3/7] 🖼️  Generating scene images...")
        image_data = generate_all_images(scenes, topic_plan, output_dir)
        thumbnail_path = generate_thumbnail_image(topic_plan, script, output_dir)

        # STEP 4: Generate all voices
        print("\n[4/7] 🎙️  Generating voice narrations...")
        voice_data = generate_all_voices(scenes, output_dir)

        # STEP 5: Build scene clips
        print("\n[5/7] 🎬 Building scene clips...")
        scene_clips = build_all_scenes(scenes, image_data, voice_data)

        if not scene_clips:
            raise Exception("No scene clips were built!")

        # STEP 6: Assemble final video
        # ✅ topic_plan passed so music matches video mood
        print("\n[6/7] 🎞️  Assembling final video...")
        final_path, duration_seconds = assemble_final_video(
            scene_clips, script["episode_title"], output_dir, topic_plan)

        # STEP 7: Generate SEO + Upload
        print("\n[7/7] 🏷️  Generating SEO + Uploading...")
        seo_data = generate_viral_seo(topic_plan, script, duration_seconds / 60)
        video_id = upload_video(final_path, seo_data, thumbnail_path)
        log_upload(video_id, seo_data["title"], topic_plan)

        print("\n" + "="*60)
        print(f"🎉 SUCCESS! Video published!")
        print(f"📺 https://youtube.com/watch?v={video_id}")
        print(f"🎬 Title: {seo_data['title']}")
        print(f"⏱️  Duration: {duration_seconds/60:.1f} minutes")
        print("="*60)

    except Exception as e:
        import traceback
        print(f"\n❌ Pipeline error: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        cleanup()

def evening_pipeline():
    """Evening job: Analyze → Learn → Improve"""
    print("\n" + "="*60)
    print(f"🌙 KidsViral AI - Evening Learning Pipeline")
    print(f"📅 {datetime.now().strftime('%B %d, %Y %H:%M UTC')}")
    print("="*60)

    load_env()

    try:
        insights = analyze_performance()
        run_learning_cycle(insights)
        print("\n✅ Evening pipeline complete!")
        print("🧠 Brain updated for tomorrow's better video")
        print("="*60)

    except Exception as e:
        import traceback
        print(f"\n❌ Evening pipeline error: {traceback.format_exc()}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "evening":
        evening_pipeline()
    else:
        morning_pipeline()
        
