import json
import os
import requests
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL, SCENE_COUNT

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
BRAIN_FILE = "kids/brain.json"

DEFAULT_BRAIN = {
    "prompt_templates": {
        "script": "You are a professional kids animation scriptwriter for a top YouTube channel. Write an engaging, fun, educational episode for children aged 3-8.",
        "image": "cute colorful cartoon illustration, child-friendly, bright colors, happy characters, professional animation style, pixar-like quality"
    }
}

def load_brain():
    """Load brain — auto-create if missing"""
    if not os.path.exists(BRAIN_FILE):
        os.makedirs(os.path.dirname(BRAIN_FILE), exist_ok=True)
        with open(BRAIN_FILE, "w") as f:
            json.dump(DEFAULT_BRAIN, f, indent=2)
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def call_groq(prompt, max_tokens=4000):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.85
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def write_full_script(topic_plan):
    """Generate a full professional kids episode script using Groq"""
    print("✍️  Writing full episode script with Groq...")

    brain = load_brain()
    base_prompt = brain.get("prompt_templates", {}).get("script", DEFAULT_BRAIN["prompt_templates"]["script"])
    image_style = brain.get("prompt_templates", {}).get("image", DEFAULT_BRAIN["prompt_templates"]["image"])

    topic = topic_plan["topic"]
    character_name = topic_plan.get("character_name", "Sunny")
    character_type = topic_plan.get("character_type", "friendly lion cub")
    lesson = topic_plan.get("lesson", "kindness")
    emotion = topic_plan.get("emotion", "wonder")

    prompt = f"""{base_prompt}

TODAY'S EPISODE: "{topic}"
MAIN CHARACTER: {character_name} the {character_type}
CORE LESSON: {lesson}
TARGET EMOTION: {emotion}
DATE: {datetime.now().strftime('%B %d, %Y')}

Write a complete kids animation episode with EXACTLY {SCENE_COUNT} scenes.
Each scene should be ~35-45 seconds of narration when spoken aloud (about 80-100 words).

Episode structure:
- Scene 1: Exciting intro hook
- Scenes 2-4: Setup story world and characters
- Scenes 5-8: Main adventure begins
- Scenes 9-13: Journey with learning moments woven in
- Scenes 14-16: Climax and resolution
- Scene 17: Lesson summarized in a fun way
- Scene 18: Outro - goodbye + subscribe CTA

For EACH scene provide:
1. narration: Exact words to be spoken (kid-friendly, simple, enthusiastic)
2. image_prompt: Detailed visual description for AI image generation (include: {image_style})
3. scene_title: Short scene title
4. sound_effect: Simple sound effect description
5. text_overlay: 3-5 words for big on-screen text

Respond ONLY in this exact JSON format, no extra text:
{{
  "episode_title": "...",
  "episode_description": "A 2-sentence description",
  "total_scenes": {SCENE_COUNT},
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "...",
      "narration": "...",
      "image_prompt": "...",
      "sound_effect": "...",
      "text_overlay": "..."
    }}
  ]
}}"""

    try:
        response = call_groq(prompt, max_tokens=4000)
        text = response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        script = json.loads(text)
        print(f"✅ Script written: '{script['episode_title']}' with {len(script['scenes'])} scenes")
        return script
    except Exception as e:
        print(f"  Script generation error: {e}")
        return generate_fallback_script(topic, character_name, character_type, lesson)

def generate_fallback_script(topic, character_name, character_type, lesson):
    """Fallback script if Groq fails"""
    narrations = [
        f"Hello friends! Welcome to our amazing channel! Today we have a wonderful story about {topic}! Are you ready? Let's go on a magical adventure together!",
        f"Once upon a time there was a wonderful {character_type} named {character_name}. {character_name} lived in a beautiful magical land full of colors and joy and laughter!",
        f"{character_name} woke up one sunny morning feeling very excited. Today was going to be a very special day! The birds were singing and the flowers were smiling!",
        f"As {character_name} stepped outside something magical sparkled in the sky! Beautiful colors appeared everywhere! What could it mean? {character_name} decided to find out!",
        f"The adventure began! {character_name} walked through a rainbow forest where the trees were purple and the grass was golden. Everything was so beautiful and magical!",
        f"Suddenly {character_name} heard a little sound nearby. Someone needed help! {character_name} ran over as fast as possible to see what was happening!",
        f"There was a tiny little creature who looked very sad and lost. Oh no! {character_name} felt so much kindness and said I will help you find your way home!",
        f"Together they walked and searched everywhere! They crossed a bubbly blue stream and climbed a gentle green hill. Working together made everything so much more fun!",
        f"Along the way they discovered something truly amazing! Did you know that {lesson}? It is absolutely true! This made their journey even more wonderful and special!",
        f"They kept going with the biggest smiles on their faces. Every single step was a new adventure. The sun was warm and the wind was gentle and everything felt magical!",
        f"Look! They found a clue! A golden glowing arrow pointing the way forward! {character_name} felt so happy they were helping their new friend find the way home!",
        f"They followed the arrow through a beautiful meadow full of dancing butterflies. The butterflies seemed to be cheering them on! It was the most magical sight ever!",
        f"And then suddenly they saw it! The little creature's home was just ahead! It was a cozy little house covered in colorful flowers and surrounded by beautiful rainbows!",
        f"The little creature jumped with pure joy! Thank you so much {character_name}! You are the kindest friend in the whole wide world! This is the best day ever!",
        f"They celebrated together with a big feast of yummy fruits and sweet treats! They laughed and danced and sang happy songs. True friendship is the greatest treasure!",
        f"As the beautiful sun began to set {character_name} said a warm goodbye and headed home. The stars came out one by one to light the way. What a wonderful day!",
        f"And so dear friends today we all learned something very very important together. {lesson}! Always remember that when you help someone you make the whole world brighter!",
        f"That is all for today amazing friends! If you loved this story please give us a big thumbs up and subscribe for a brand new story every single day! Bye bye!"
    ]
    scenes = []
    for i, narration in enumerate(narrations[:SCENE_COUNT]):
        scenes.append({
            "scene_number": i + 1,
            "scene_title": f"Scene {i + 1}",
            "narration": narration,
            "image_prompt": f"cute colorful cartoon illustration of {character_name} the {character_type}, bright vivid colors, child-friendly, pixar style, scene {i + 1}",
            "sound_effect": "gentle cheerful background music",
            "text_overlay": topic[:20]
        })
    return {
        "episode_title": f"{topic} | Kids Story",
        "episode_description": f"Join {character_name} on an amazing adventure about {lesson}!",
        "total_scenes": len(scenes),
        "scenes": scenes
}
