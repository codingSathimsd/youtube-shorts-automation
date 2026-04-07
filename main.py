import os
import shutil
from src.fetch_videos import fetch_pexels_videos, get_trending_topic
from src.download_video import download_video
from src.clip_video import create_clips
from src.add_text_overlay import add_text_overlay
from src.generate_seo import generate_facts_and_seo
from src.upload_youtube import upload_short
from config import TOPICS, OUTPUT_DIR

TEMP_DIRS = ['downloads', OUTPUT_DIR]

def cleanup():
    for d in TEMP_DIRS:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Cleaned: {d}")

def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()

def main():
    load_env()

    print("=" * 50)
    print("Starting YouTube Shorts Automation...")
    print("=" * 50)

    print(f"GROQ_API_KEY: {'OK' if os.environ.get('GROQ_API_KEY') else 'MISSING'}")
    print(f"PEXELS_API_KEY: {'OK' if os.environ.get('PEXELS_API_KEY') else 'MISSING'}")
    print(f"YOUTUBE_CLIENT_ID: {'OK' if os.environ.get('YOUTUBE_CLIENT_ID') else 'MISSING'}")
    print(f"YOUTUBE_REFRESH_TOKEN: {'OK' if os.environ.get('YOUTUBE_REFRESH_TOKEN') else 'MISSING'}")

    cleanup()

    try:
        pexels_key = os.environ.get("PEXELS_API_KEY")
        groq_key = os.environ.get("GROQ_API_KEY")

        if not pexels_key:
            raise Exception("PEXELS_API_KEY missing")
        if not groq_key:
            raise Exception("GROQ_API_KEY missing")

        # Pick topic
        topic = get_trending_topic(TOPICS)
        print(f"\nTopic: {topic}")

        # Generate facts + SEO with Groq
        print("\nSTEP 1: Generating facts with Groq...")
        content = generate_facts_and_seo(topic)

        # Fetch Pexels video
        print("\nSTEP 2: Fetching Pexels video...")
        videos = fetch_pexels_videos(topic, pexels_key)
        if not videos:
            raise Exception(f"No videos for: {topic}")

        for video in videos[:5]:
            try:
                # Download
                print("\nSTEP 3: Downloading...")
                video_path, duration = download_video(video['url'])

                # Clip to vertical
                print("\nSTEP 4: Clipping to vertical...")
                clip_paths = create_clips(video_path)

                if os.path.exists(video_path):
                    os.remove(video_path)

                if not clip_paths:
                    continue

                # Add text overlay
                print("\nSTEP 5: Adding text overlays...")
                clip_path = clip_paths[0]
                final_path = f"{OUTPUT_DIR}/final_clip.mp4"
                add_text_overlay(clip_path, content, final_path)

                if os.path.exists(clip_path):
                    os.remove(clip_path)

                # Build metadata
                metadata = {
                    "title": content["title"],
                    "description": content["description"],
                    "tags": content["tags"],
                    "hashtags": content["hashtags"]
                }

                # Upload
                print("\nSTEP 6: Uploading to YouTube...")
                upload_short(final_path, metadata)

                if os.path.exists(final_path):
                    os.remove(final_path)

                print("\nSUCCESS!")
                break

            except Exception as e:
                import traceback
                print(f"Error: {traceback.format_exc()}")
                continue

    finally:
        cleanup()
        print("\n" + "=" * 50)
        print("Automation complete!")
        print("=" * 50)

if __name__ == "__main__":
    main()
