import os
import json
import requests
from config import (
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN,
    VIDEO_CATEGORY_ID, MADE_FOR_KIDS, VIDEO_LANGUAGE, DEFAULT_PRIVACY
)

def get_access_token():
    """Get fresh YouTube access token"""
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def upload_video(video_path, seo_data, thumbnail_path=None):
    """Upload video to YouTube with full metadata"""
    print("📤 Uploading to YouTube...")

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    title = seo_data.get("title", "Kids Story Video")[:100]
    description = seo_data.get("description", "")[:5000]
    tags = seo_data.get("tags", [])[:500]
    if isinstance(tags, list):
        tags = tags[:30]  # YouTube allows max 30 tags

    # Step 1: Initialize upload
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": VIDEO_CATEGORY_ID,
            "defaultLanguage": VIDEO_LANGUAGE,
            "defaultAudioLanguage": VIDEO_LANGUAGE
        },
        "status": {
            "privacyStatus": DEFAULT_PRIVACY,
            "madeForKids": MADE_FOR_KIDS,
            "selfDeclaredMadeForKids": MADE_FOR_KIDS
        }
    }

    init_resp = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status",
        headers={**headers, "Content-Type": "application/json",
                 "X-Upload-Content-Type": "video/mp4"},
        json=metadata
    )
    init_resp.raise_for_status()
    upload_url = init_resp.headers["Location"]

    # Step 2: Upload video file
    video_size = os.path.getsize(video_path)
    print(f"  Uploading {video_size / 1024 / 1024:.1f} MB...")

    with open(video_path, "rb") as f:
        upload_resp = requests.put(
            upload_url,
            headers={**headers, "Content-Type": "video/mp4",
                     "Content-Length": str(video_size)},
            data=f
        )
    upload_resp.raise_for_status()
    video_data = upload_resp.json()
    video_id = video_data["id"]
    print(f"  ✅ Video uploaded: https://youtube.com/watch?v={video_id}")

    # Step 3: Upload thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            with open(thumbnail_path, "rb") as f:
                thumb_resp = requests.post(
                    f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}&uploadType=media",
                    headers={**headers, "Content-Type": "image/jpeg"},
                    data=f
                )
            if thumb_resp.status_code == 200:
                print("  🖼️  Thumbnail uploaded")
        except Exception as e:
            print(f"  Thumbnail upload error: {e}")

    return video_id

def log_upload(video_id, title, topic_plan):
    """Log uploaded video to memory.json"""
    from datetime import datetime
    memory_file = "kids/memory.json"
    try:
        with open(memory_file, "r") as f:
            memory = json.load(f)
    except:
        memory = {"posted_videos": [], "posted_titles": [], "total_posted": 0, "last_post_date": ""}

    memory["posted_videos"].append({
        "video_id": video_id,
        "title": title,
        "topic": topic_plan.get("topic", ""),
        "date": datetime.now().isoformat(),
        "views": 0,
        "likes": 0
    })
    memory["posted_titles"].append(title)
    memory["total_posted"] += 1
    memory["last_post_date"] = datetime.now().isoformat()

    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2)
    print(f"  📝 Logged to memory.json")
              
