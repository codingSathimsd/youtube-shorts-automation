import json
import google.generativeai as genai
from datetime import datetime
from config import GEMINI_API_KEY, GEMINI_MODEL, SCENE_COUNT

def load_brain():
    with open("kids/brain.json", "r") as f:
        return json.load(f)

def write_full_script(topic_plan):
    """Generate a full professional kids episode script with Gemini"""
    print("✍️  Writing full episode script with Gemini...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    brain = load_brain()
    base_prompt = brain["prompt_templates"]["script"]
    image_style = brain["prompt_templates"]["image"]

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

The episode structure must be:
- Scene 1: Exciting intro / hook (grab attention in first 10 seconds)
- Scenes 2-4: Setup the story world and introduce characters warmly
- Scenes 5-8: The main adventure / challenge begins
- Scenes 9-13: The journey, learning moments woven naturally into story
- Scenes 14-16: Climax and resolution
- Scene 17: The lesson summarized in a fun, memorable way
- Scene 18: Outro - say goodbye, ask kids to subscribe and comment

For EACH scene, provide:
1. narration: The exact words to be spoken (kid-friendly, simple, enthusiastic, present tense)
2. image_prompt: A detailed visual description for AI image generation (always include "{image_style}")
3. scene_title: Short title for this scene
4. sound_effect: One simple sound effect description (e.g., "happy birds chirping", "magical sparkle sound")
5. text_overlay: 3-5 word big text to show on screen

Respond ONLY in this exact JSON format:
{{
  "episode_title": "...",
  "episode_description": "A 2-sentence description of this episode",
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
}}

Only respond with the JSON. No extra text."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        script = json.loads(text)
        print(f"✅ Script written: '{script['episode_title']}' with {len(script['scenes'])} scenes")
        return script
    except Exception as e:
        print(f"Script generation error: {e}")
        # Fallback minimal script
        return generate_fallback_script(topic, character_name, character_type, lesson)

def generate_fallback_script(topic, character_name, character_type, lesson):
    """Fallback if Gemini fails"""
    scenes = []
    narrations = [
        f"Hello friends! Welcome to our channel! Today we have an amazing story about {topic}! Are you ready? Let's go!",
        f"Once upon a time, there was a wonderful {character_type} named {character_name}. {character_name} lived in a beautiful magical land full of colors and adventure!",
        f"{character_name} woke up one sunny morning feeling very excited. Today was going to be a special day! The birds were singing and the flowers were smiling.",
        f"As {character_name} looked around, something magical happened! A sparkling light appeared in the sky. What could it be? {character_name} decided to find out!",
        f"The journey began! {character_name} walked through a rainbow forest where the trees were purple and the grass was golden. Everything was so beautiful!",
        f"Suddenly {character_name} met a new friend. It was a tiny little creature who looked sad. Oh no! What was wrong? {character_name} went over to help.",
        f"The little creature said it was lost and couldn't find its home. {character_name} felt so much kindness in their heart and said don't worry I will help you!",
        f"Together they searched and searched. They crossed a bubbly stream and climbed a gentle hill. Working together made everything more fun!",
        f"Along the way they discovered something amazing! Did you know that {lesson}? It's true! And it made their journey even more special!",
        f"They kept going with big smiles on their faces. The sun was warm, the wind was gentle, and every step was an adventure waiting to happen!",
        f"Oh! They found a clue! A golden arrow pointing the way home. {character_name} felt so happy they were able to help their new friend!",
        f"They followed the arrow through a meadow full of dancing butterflies. The butterflies seemed to be cheering them on! Fly fly fly!",
        f"And then! They saw it! The little creature's home was just ahead! It was a cozy little house covered in flowers and surrounded by rainbows!",
        f"The little creature jumped with joy! Thank you {character_name}! Thank you so much! This is the best day ever! {character_name} felt so warm inside.",
        f"They celebrated with a big feast of fruits and sweets. They laughed and danced and sang songs together. True friendship is the greatest treasure!",
        f"As the sun began to set, {character_name} said goodbye and headed home. The stars came out to light the way. What a wonderful adventure!",
        f"And so friends, today we learned something very important. {lesson}! Remember that whenever you help someone, you make the whole world brighter!",
        f"That's all for today friends! If you enjoyed this story, give us a big thumbs up and subscribe to our channel! See you next time! Bye bye!"
    ]
    for i, narration in enumerate(narrations[:SCENE_COUNT]):
        scenes.append({
            "scene_number": i + 1,
            "scene_title": f"Scene {i+1}",
            "narration": narration,
            "image_prompt": f"cute colorful cartoon illustration of {character_name} the {character_type}, scene {i+1}, bright colors, child-friendly, pixar style",
            "sound_effect": "gentle background music",
            "text_overlay": topic[:20]
        })
    return {
        "episode_title": f"{topic} | Kids Story",
        "episode_description": f"Join {character_name} on an amazing adventure! A fun story for kids about {lesson}.",
        "total_scenes": len(scenes),
        "scenes": scenes
}

