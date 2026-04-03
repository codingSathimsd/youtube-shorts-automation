import os
import shutil
from src.fetch_videos import get_latest_videos
from src.download_video import download_video
from src.clip_video import create_clips
from src.transcribe import add_captions
from src.generate_seo import generate_seo
from src.upload_youtube import upload_short

def cleanup(dirs):
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)

def main():
    print("=" * 50)
    print("Starting YouTube Shorts Automation...")
    print("=" * 50)

    # Check secrets loaded
    print(f"GEMINI_API_KEY loaded: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'NO - MISSING'}")
    print(f"YOUTUBE_CLIENT_ID loaded: {'Yes' if os.environ.get('YOUTUBE_CLIENT_ID') else 'NO - MISSING'}")
    print(f"YOUTUBE_CLIENT_SECRET loaded: {'Yes' if os.environ.get('YOUTUBE_CLIENT_SECRET') else 'NO - MISSING'}")
    print(f"YOUTUBE_REFRESH_TOKEN loaded: {'Yes' if os.environ.get('YOUTUBE_REFRESH_TOKEN') else 'NO - MISSING'}")
    print("=" * 50)

    # Step 1: Fetch videos
    print("\nSTEP 1: Fetching videos from channels...")
    videos = get_latest_videos()
    print(f"Total videos found: {len(videos)}")

    if len(videos) == 0:
        print("ERROR: No videos found. Check your CHANNELS list in config.py")
        return

    for video in videos[:2]:
        print(f"\n{'=' * 50}")
        print(f"Processing: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"{'=' * 50}")

        try:
            # Step 2: Download
            print("\nSTEP 2: Downloading video...")
            video_path, duration = download_video(video['url'])
            print(f"Downloaded to: {video_path}")
            print(f"Duration: {duration} seconds")

            if not os.path.exists(video_path):
                print(f"ERROR: File not found at {video_path}")
                continue

            if duration < 120:
                print("SKIPPING: Video too short (under 2 minutes)")
                continue

            # Step 3: Clip
            print("\nSTEP 3: Creating clips...")
            clip_paths = create_clips(video_path)
            print(f"Clips created: {len(clip_paths)}")
            for p in clip_paths:
                print(f"  - {p}")

            if not clip_paths:
                print("ERROR: No clips were created")
                continue

            # Step 4: Transcribe
            print("\nSTEP 4: Transcribing audio...")
            transcript = add_captions(clip_paths[0])
            print(f"Transcript length: {len(transcript)} characters")

            # Step 5 + 6: SEO + Upload
            for i, clip_path in enumerate(clip_paths):
                print(f"\nSTEP 5: Generating SEO for clip {i+1}...")
                metadata = generate_seo(
                    video['title'],
                    transcript,
                    video['channel']
                )
                print(f"Title: {metadata['title']}")

                print(f"\nSTEP 6: Uploading clip {i+1} to YouTube...")
                video_id = upload_short(clip_path, metadata)
                print(f"SUCCESS: https://youtube.com/shorts/{video_id}")

        except Exception as e:
            import traceback
            print(f"\nERROR processing {video['title']}:")
            print(traceback.format_exc())
            continue

    cleanup(['downloads', 'output_clips'])
    print("\n" + "=" * 50)
    print("Automation complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
