import requests
import random

def get_trending_topic(topics):
    return random.choice(topics)

def fetch_pexels_videos(topic, api_key):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": topic,
        "per_page": 10,
        "min_duration": 60,
        "max_duration": 600,
        "orientation": "landscape",
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    videos = []
    for video in data.get("videos", []):
        files = video.get("video_files", [])
        best_file = None
        best_width = 0

        for f in files:
            if f.get("width", 0) > best_width and f.get("file_type") == "video/mp4":
                best_width = f.get("width", 0)
                best_file = f

        if best_file:
            videos.append({
                "title": f"{topic.title()} - Amazing Facts",
                "url": best_file["link"],
                "duration": video.get("duration", 0),
                "topic": topic,
                "channel": "Pexels",
            })

    print(f"Found {len(videos)} videos for topic: {topic}")
    return videos
