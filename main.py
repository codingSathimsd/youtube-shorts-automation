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
    print("🚀 Starting YouTube Shorts Automation...")
    
    # Step 1: Find videos
    videos = get_latest_videos()
    print(f"Found {len(videos)} videos to process")
    
    for video in videos[:2]:  # Process max 2 videos per run (API limits)
        print(f"\n📹 Processing: {video['title']}")
        
        try:
            # Step 2: Download
            video_path, duration = download_video(video['url'])
            
            # Skip if video is too short
            if duration < 120:
                print("Skipping — video too short")
                continue
            
            # Step 3: Create clips
            clip_paths = create_clips(video_path)
            
            # Step 4: Transcribe (use first clip for speed)
            transcript = add_captions(clip_paths[0])
            
            # Step 5 + 6: SEO + Upload each clip
            for i, clip_path in enumerate(clip_paths):
                metadata = generate_seo(
                    video['title'],
                    transcript,
                    video['channel']
                )
                
                upload_short(clip_path, metadata)
                print(f"✅ Clip {i+1} done!")
        
        except Exception as e:
            print(f"❌ Error processing {video['title']}: {e}")
            continue
    
    # Cleanup temp files
    cleanup(['downloads', 'output_clips'])
    print("\n🎉 Automation complete!")

if __name__ == "__main__":
    main()
