import feedparser
import os
from config import CHANNELS

def get_latest_videos():
    """Fetch latest videos from configured channels via RSS"""
    videos = []
    
    for channel_id in CHANNELS:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:2]:  # Get 2 latest per channel
            video = {
                "title": entry.title,
                "url": entry.link,
                "video_id": entry.yt_videoid,
                "channel": entry.author,
                "duration": None  # Will be filled during download
            }
            videos.append(video)
            print(f"Found: {entry.title}")
    
    return videos
