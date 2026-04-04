import requests
import os

def download_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    filename = url.split("?")[0].split("/")[-1]
    if not filename.endswith(".mp4"):
        filename = f"video_{abs(hash(url))}.mp4"

    output_path = os.path.join(output_dir, filename)

    print(f"Downloading: {url[:60]}...")
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()

    total = 0
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                total += len(chunk)
                print(f"Downloaded: {total // (1024*1024)}MB", end="\r")

    print(f"\nSaved: {output_path}")
    return output_path, 999
