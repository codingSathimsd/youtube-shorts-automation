import feedparser
from config import CHANNELS

def get_latest_videos():
    videos = []
    for channel_id in CHANNELS:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:2]:
            video = {
                "title": entry.title,
                "url": entry.link,
                "video_id": entry.yt_videoid,
                "channel": entry.author,
            }
            videos.append(video)
            print(f"Found: {entry.title}")
    return videos
