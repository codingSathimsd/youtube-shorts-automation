import yt_dlp
import os

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    # Write cookies from environment to file
    cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
    cookies_path = "cookies.txt"

    if cookies_content:
        with open(cookies_path, "w") as f:
            f.write(cookies_content)
        print("Cookies loaded successfully")
    else:
        print("WARNING: No cookies found")

    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': cookies_path,
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = os.path.splitext(ydl.prepare_filename(info))[0]
        filename = base + ".mp4"
        duration = info.get('duration', 0)

    return filename, duration
