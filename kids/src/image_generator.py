import os
import time
import requests
from urllib.parse import quote
from config import VIDEO_WIDTH, VIDEO_HEIGHT, OUTPUT_DIR

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&enhance=true"

def generate_image_for_scene(image_prompt, scene_number, output_dir, character_context=""):
    """Generate image for a single scene using Pollinations.ai (free, no API key)"""
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"scene_{scene_number:02d}_image.jpg")

    # Build a rich, consistent prompt
    full_prompt = f"{image_prompt}, {character_context}, bright vivid colors, soft lighting, child-friendly, no text, no watermark, high quality, 4k"
    full_prompt = full_prompt[:500]  # Pollinations limit
    encoded_prompt = quote(full_prompt)

    url = POLLINATIONS_URL.format(
        prompt=encoded_prompt,
        w=VIDEO_WIDTH,
        h=VIDEO_HEIGHT
    )

    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(image_path, 'wb') as f:
                    f.write(resp.content)
                print(f"  🖼️  Scene {scene_number}: image generated")
                return image_path
            else:
                print(f"  Image attempt {attempt+1} failed (status {resp.status_code}), retrying...")
                time.sleep(3)
        except Exception as e:
            print(f"  Image error scene {scene_number} attempt {attempt+1}: {e}")
            time.sleep(3)

    # Fallback: create a solid color image with PIL
    print(f"  Using fallback color image for scene {scene_number}")
    return create_fallback_image(scene_number, image_path)

def create_fallback_image(scene_number, image_path):
    """Create a colorful fallback image if Pollinations fails"""
    from PIL import Image, ImageDraw
    colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
    ]
    color = colors[scene_number % len(colors)]
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color)
    draw = ImageDraw.Draw(img)
    # Add simple decorative circles
    for i in range(10):
        x = (i * 200) % VIDEO_WIDTH
        y = (i * 150) % VIDEO_HEIGHT
        draw.ellipse([x, y, x+100, y+100], fill="white", outline=None)
    img.save(image_path, quality=95)
    return image_path

def generate_thumbnail_image(topic_plan, script, output_dir):
    """Generate a special high-quality thumbnail image"""
    os.makedirs(output_dir, exist_ok=True)
    thumbnail_path = os.path.join(output_dir, "thumbnail.jpg")

    character = topic_plan.get("character_name", "Sunny")
    char_type = topic_plan.get("character_type", "cute cartoon character")
    topic = topic_plan.get("topic", "Kids Story")
    emotion = topic_plan.get("emotion", "excited")

    thumbnail_prompt = (
        f"youtube thumbnail, {emotion} {char_type} named {character}, "
        f"big expressive eyes wide open, mouth open in surprise and joy, "
        f"bright yellow and red background with stars, "
        f"professional cartoon style, pixar quality, vivid colors, "
        f"close up face shot, child-friendly, no text overlay"
    )
    encoded = quote(thumbnail_prompt[:500])
    url = POLLINATIONS_URL.format(prompt=encoded, w=1280, h=720)

    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 10000:
            with open(thumbnail_path, 'wb') as f:
                f.write(resp.content)
            print(f"  🖼️  Thumbnail generated")
            return thumbnail_path
    except Exception as e:
        print(f"  Thumbnail error: {e}")
    return create_fallback_image(0, thumbnail_path)

def generate_all_images(scenes, topic_plan, output_dir):
    """Generate images for all scenes"""
    print("🖼️  Generating scene images with Pollinations AI...")

    character_context = (
        f"{topic_plan.get('character_name','Sunny')} the "
        f"{topic_plan.get('character_type','friendly cartoon character')}"
    )

    image_paths = []
    for scene in scenes:
        scene_num = scene["scene_number"]
        image_prompt = scene["image_prompt"]
        path = generate_image_for_scene(image_prompt, scene_num, output_dir, character_context)
        image_paths.append({"scene_number": scene_num, "image_path": path})
        time.sleep(1)  # be polite to Pollinations

    print(f"✅ All {len(image_paths)} scene images generated")
    return image_paths
  
