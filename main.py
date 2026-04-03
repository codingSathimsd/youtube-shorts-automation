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
    print("Starting YouTube Shorts Automation...")

    videos = get_latest_videos()
    print(f"Found {len(videos)} videos to process")

    for video in videos[:2]:
        print(f"\nProcessing: {video['title']}")
        try:
            # Download
            video_path, duration = download_video(video['url'])

            if duration < 120:
                print("Skipping — video too short")
                continue

            # Clip
            clip_paths = create_clips(video_path)

            # Transcribe
            transcript = add_captions(clip_paths[0])

            # SEO + Upload
            for i, clip_path in enumerate(clip_paths):
                metadata = generate_seo(
                    video['title'],
                    transcript,
                    video['channel']
                )
                upload_short(clip_path, metadata)
                print(f"Clip {i+1} uploaded successfully!")

        except Exception as e:
            print(f"Error processing {video['title']}: {e}")
            continue

    cleanup(['downloads', 'output_clips'])
    print("\nAutomation complete!")

if __name__ == "__main__":
    main()
