import json
import requests
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN

def get_access_token():
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def fetch_video_stats(video_ids):
    """Fetch views, likes, comments for a list of video IDs"""
    if not video_ids:
        return {}

    try:
        token = get_access_token()
        ids_str = ",".join(video_ids[:50])
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "statistics",
                "id": ids_str,
                "access_token": token
            },
            timeout=15
        )
        resp.raise_for_status()
        stats = {}
        for item in resp.json().get("items", []):
            vid_id = item["id"]
            s = item.get("statistics", {})
            stats[vid_id] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0))
            }
        return stats
    except Exception as e:
        print(f"  Analytics fetch error: {e}")
        return {}

def analyze_performance():
    """Analyze performance of posted videos and return insights"""
    print("📊 Analyzing video performance...")

    memory_file = "kids/memory.json"
    try:
        with open(memory_file, "r") as f:
            memory = json.load(f)
    except:
        print("  No memory file found")
        return {}

    posted = memory.get("posted_videos", [])
    if not posted:
        print("  No videos to analyze yet")
        return {}

    video_ids = [v["video_id"] for v in posted if v.get("video_id")]
    stats = fetch_video_stats(video_ids)

    # Update memory with latest stats
    for video in posted:
        vid_id = video.get("video_id", "")
        if vid_id in stats:
            video["views"] = stats[vid_id]["views"]
            video["likes"] = stats[vid_id]["likes"]
            video["comments"] = stats[vid_id]["comments"]

    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2)

    # Find best performing videos
    sorted_videos = sorted(posted, key=lambda x: x.get("views", 0), reverse=True)
    best_topics = [v["topic"] for v in sorted_videos[:5] if v.get("topic")]
    avg_views = sum(v.get("views", 0) for v in posted) / max(len(posted), 1)

    insights = {
        "total_videos": len(posted),
        "avg_views": avg_views,
        "best_topics": best_topics,
        "best_video": sorted_videos[0] if sorted_videos else None,
        "total_views": sum(v.get("views", 0) for v in posted)
    }

    print(f"  📈 Total videos: {insights['total_videos']}")
    print(f"  📈 Avg views: {insights['avg_views']:.0f}")
    print(f"  📈 Total views: {insights['total_views']}")
    return insights
  
