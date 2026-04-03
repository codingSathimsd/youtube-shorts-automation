import yt_dlp
import os

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # Ensure .mp4 extension
        base = os.path.splitext(filename)[0]
        filename = base + ".mp4"
        duration = info.get('duration', 0)
    return filename, duration
