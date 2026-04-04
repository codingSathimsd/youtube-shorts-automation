import yt_dlp
import os
import json

def convert_cookies_to_netscape(cookies_content):
    cookies_content = cookies_content.strip()
    if cookies_content.startswith("# Netscape HTTP Cookie File"):
        return cookies_content
    try:
        cookies = json.loads(cookies_content)
        lines = ["# Netscape HTTP Cookie File", "# https://curl.se/docs/http-cookies.html", ""]
        for cookie in cookies:
            domain = cookie.get("domain", ".youtube.com")
            if not domain.startswith("."):
                domain = "." + domain
            include_subdomains = "TRUE"
            path = cookie.get("path", "/")
            secure = "TRUE" if cookie.get("secure", False) else "FALSE"
            expiry = str(int(cookie.get("expirationDate", 0)))
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            lines.append(f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiry}\t{name}\t{value}")
        return "\n".join(lines)
    except:
        return cookies_content

def try_download(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            base = os.path.splitext(filename)[0]
            filename = base + '.mp4'
        duration = info.get('duration', 0)
        return filename, duration

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
    cookies_path = "cookies.txt"

    if cookies_content:
        netscape_cookies = convert_cookies_to_netscape(cookies_content)
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(netscape_cookies)
        print("Cookies loaded successfully")
    else:
        print("WARNING: No cookies found")

    # Base options shared across all attempts
    base_opts = {
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': cookies_path,
        'quiet': False,
        'retries': 5,
        'fragment_retries': 5,
    }

    # List of strategies to try one by one
    strategies = [
        {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12) gzip',
            }
        },
        {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'extractor_args': {'youtube': {'player_client': ['ios']}},
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/17.33.2 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
            }
        },
        {
            **base_opts,
            'format': 'best[ext=mp4]/best',
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
        },
        {
            **base_opts,
            'format': 'worstvideo[ext=mp4]+worstaudio/worst[ext=mp4]/worst',
            'extractor_args': {'youtube': {'player_client': ['android']}},
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12) gzip',
            }
        },
        {
            **base_opts,
            'format': 'bestvideo+bestaudio/best',
            'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios']}},
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12) gzip',
            }
        },
    ]

    last_error = None
    for i, opts in enumerate(strategies):
        try:
            print(f"\nTrying strategy {i+1}/5...")
            filename, duration = try_download(url, opts)
            print(f"Strategy {i+1} succeeded!")
            print(f"File: {filename}")
            print(f"Duration: {duration}s")
            return filename, duration
        except Exception as e:
            print(f"Strategy {i+1} failed: {str(e)[:100]}")
            last_error = e
            continue

    raise Exception(f"All 5 download strategies failed. Last error: {last_error}")
