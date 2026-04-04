import os
import shutil
from src.fetch_videos import fetch_pexels_videos, get_trending_topic
from src.download_video import download_video
from src.clip_video import create_clips
from src.generate_seo import generate_seo
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

    print(f"GEMINI_API_KEY: {'OK' if os.environ.get('GEMINI_API_KEY') else 'MISSING'}")
    print(f"PEXELS_API_KEY: {'OK' if os.environ.get('PEXELS_API_KEY') else 'MISSING'}")
    print(f"YOUTUBE_CLIENT_ID: {'OK' if os.environ.get('YOUTUBE_CLIENT_ID') else 'MISSING'}")
    print(f"YOUTUBE_CLIENT_SECRET: {'OK' if os.environ.get('YOUTUBE_CLIENT_SECRET') else 'MISSING'}")
    print(f"YOUTUBE_REFRESH_TOKEN: {'OK' if os.environ.get('YOUTUBE_REFRESH_TOKEN') else 'MISSING'}")

    cleanup()

    try:
        pexels_key = os.environ.get("PEXELS_API_KEY")
        if not pexels_key:
            raise Exception("PEXELS_API_KEY is missing")

        topic = get_trending_topic(TOPICS)
        print(f"\nToday's topic: {topic}")

        videos = fetch_pexels_videos(topic, pexels_key)
        if not videos:
            raise Exception(f"No videos found for topic: {topic}")

        processed = 0
        for video in videos[:5]:
            if processed >= 3:
                break

            print(f"\n{'=' * 50}")
            print(f"Processing: {video['title']}")
            print(f"{'=' * 50}")

            try:
                print("\nSTEP 1: Downloading...")
                video_path, duration = download_video(video['url'])

                print("\nSTEP 2: Creating clips...")
                clip_paths = create_clips(video_path)

                if os.path.exists(video_path):
                    os.remove(video_path)
                    print("Original deleted")

                if not clip_paths:
                    print("No clips created, skipping")
                    continue

                for i, clip_path in enumerate(clip_paths):
                    print(f"\nSTEP 3: SEO for clip {i+1}...")
                    metadata = generate_seo(
                        video['title'],
                        "",
                        "Pexels",
                        topic=video['topic']
                    )

                    print(f"STEP 4: Uploading clip {i+1}...")
                    upload_short(clip_path, metadata)

                    if os.path.exists(clip_path):
                        os.remove(clip_path)
                        print(f"Clip {i+1} deleted after upload")

                processed += 1

            except Exception as e:
                import traceback
                print(f"Error: {traceback.format_exc()}")
                continue

            finally:
                cleanup()

    finally:
        cleanup()
        print("\n" + "=" * 50)
        print("Automation complete!")
        print("=" * 50)

if __name__ == "__main__":
    main()
