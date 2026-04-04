import yt_dlp
import os
import json

def convert_cookies_to_netscape(cookies_content):
    """Convert JSON cookies to Netscape format if needed"""
    cookies_content = cookies_content.strip()
    
    # Already Netscape format
    if cookies_content.startswith("# Netscape HTTP Cookie File"):
        return cookies_content
    
    # Try to convert from JSON
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
            
            line = f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiry}\t{name}\t{value}"
            lines.append(line)
        
        return "\n".join(lines)
    except:
        return cookies_content

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
    cookies_path = "cookies.txt"

    if cookies_content:
        # Convert to Netscape format if needed
        netscape_cookies = convert_cookies_to_netscape(cookies_content)
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(netscape_cookies)
        print("Cookies written successfully")
        print(f"Cookie format: {'Netscape' if netscape_cookies.startswith('# Netscape') else 'Other'}")
    else:
        print("WARNING: No cookies found")

    ydl_opts = {
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': cookies_path,
        'quiet': False,
        'no_warnings': False,
        'retries': 3,
        'fragment_retries': 3,
        'ignoreerrors': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        # Handle extension
        if not filename.endswith('.mp4'):
            base = os.path.splitext(filename)[0]
            filename = base + '.mp4'
        
        duration = info.get('duration', 0)
        print(f"Downloaded: {filename}")
        print(f"Duration: {duration}s")

    return filename, duration
