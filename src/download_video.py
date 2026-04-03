from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Fetching video info: {url}")

    yt = YouTube(url, on_progress_callback=on_progress)

    print(f"Title: {yt.title}")
    print(f"Duration: {yt.length}s")

    duration = yt.length

    # Get best mp4 stream
    stream = (
        yt.streams
        .filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .last()
    )

    if not stream:
        stream = yt.streams.filter(file_extension="mp4").first()

    if not stream:
        raise Exception("No downloadable stream found")

    print(f"Downloading at: {stream.resolution}")
    output_path = stream.download(output_path=output_dir)
    print(f"Saved to: {output_path}")

    return output_path, duration
