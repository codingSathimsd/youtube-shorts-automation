import json
import os
import requests
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL, SCENE_COUNT

GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
BRAIN_FILE = "kids/brain.json"

DEFAULT_BRAIN = {
    "prompt_templates": {
        "script": "You are a professional kids animation scriptwriter. Write engaging episodes for children aged 3-8.",
        "image":  "cute colorful 3D cartoon illustration, child-friendly, bright colors, pixar-like quality"
    }
}

def load_brain():
    if not os.path.exists(BRAIN_FILE):
        os.makedirs(os.path.dirname(BRAIN_FILE), exist_ok=True)
        with open(BRAIN_FILE, "w") as f:
            json.dump(DEFAULT_BRAIN, f, indent=2)
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def call_groq(prompt, max_tokens=6000):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}",
               "Content-Type": "application/json"}
    payload = {"model": GROQ_MODEL,
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": max_tokens, "temperature": 0.88}
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def write_full_script(topic_plan):
    print("✍️  Writing professional 30-scene episode with Groq...")
    brain      = load_brain()
    image_style = brain.get("prompt_templates", {}).get(
        "image", DEFAULT_BRAIN["prompt_templates"]["image"])

    topic          = topic_plan["topic"]
    character_name = topic_plan.get("character_name", "Sunny")
    character_type = topic_plan.get("character_type", "friendly lion cub")
    lesson         = topic_plan.get("lesson", "kindness")
    emotion        = topic_plan.get("emotion", "wonder")

    prompt = f"""You are a PROFESSIONAL KIDS ANIMATION WRITER working for a studio like Pixar or DreamWorks.
You write for children aged 3-8. Your stories are emotionally engaging, funny, and deeply meaningful.

TODAY'S EPISODE: "{topic}"
MAIN CHARACTER: {character_name} the {character_type}
CORE LESSON: {lesson}
TARGET EMOTION: {emotion}
DATE: {datetime.now().strftime('%B %d, %Y')}

Write a COMPLETE PROFESSIONAL episode with EXACTLY {SCENE_COUNT} scenes.
Each scene narration: 55-75 words (25-30 seconds when spoken naturally).
Total video target: 12-15 minutes.

=== PROFESSIONAL STORYTELLING RULES ===
1. HOOK: Open with action or mystery in the very first sentence — never "once upon a time"
2. SHOW DON'T TELL: Use sensory details — colors, sounds, smells, textures
3. REAL DIALOGUE: Characters speak like actual kids — short, punchy, emotional
4. STAKES: The problem must feel REAL and IMPORTANT to the child audience
5. PLOT TWISTS: Include one at scene 12 and one at scene 22 — unexpected but satisfying
6. LESSON: Must emerge NATURALLY from the story — never preachy or forced
7. CLIFFHANGERS: Every 3rd scene should end with a question or surprise
8. COMEDY: Add at least 5 funny moments — kids love to laugh
9. EMOTION: Include one moment that makes the audience feel proud of the character
10. ENDING: The resolution must feel EARNED and JOYFUL

=== STORY STRUCTURE (30 scenes) ===
Scenes 1-2:   EXPLOSIVE HOOK — start in the middle of action, grab attention immediately
Scenes 3-5:   World building — introduce the world, secondary characters, daily life
Scenes 6-8:   INCITING INCIDENT — the problem appears, stakes established
Scenes 9-11:  First attempts — character tries to solve it, fails in funny/dramatic ways
Scene 12:     PLOT TWIST 1 — things get unexpectedly worse (or a shocking discovery)
Scenes 13-15: New approach — character learns something, finds a new strategy
Scenes 16-18: Progress with setbacks — getting closer but obstacles keep coming
Scenes 19-21: DARK MOMENT — seems completely hopeless, character considers giving up
Scene 22:     PLOT TWIST 2 — unexpected help, hidden ability, or magical discovery
Scenes 23-25: CLIMAX BUILDUP — everything comes together, action accelerates
Scene 26:     THE BIG MOMENT — the character succeeds in a spectacular way
Scenes 27-28: Resolution — consequences, the lesson revealed naturally through action
Scene 29:     EMOTIONAL PAYOFF — celebration, relationships strengthened, growth shown
Scene 30:     WARM GOODBYE — character speaks directly to audience, CTA to subscribe

=== OUTPUT FORMAT ===
Respond ONLY in this exact JSON format. No extra text, no markdown:
{{
  "episode_title": "Exciting title with emotion word",
  "episode_description": "Two exciting sentences that make parents want to click play",
  "total_scenes": {SCENE_COUNT},
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "Short dramatic title",
      "narration": "55-75 words of professional storytelling with sensory details and personality...",
      "image_prompt": "Detailed visual: {image_style}, describe specific action, emotion, setting",
      "sound_effect": "specific sound that adds atmosphere",
      "text_overlay": "3-5 WORD HOOK"
    }}
  ]
}}"""

    try:
        response = call_groq(prompt, max_tokens=6000)
        text = response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        script = json.loads(text)
        print(f"✅ Script: '{script['episode_title']}' — {len(script['scenes'])} scenes")
        return script
    except Exception as e:
        print(f"  Script error: {e}, using fallback")
        return generate_fallback_script(topic, character_name, character_type, lesson)

def generate_fallback_script(topic, character_name, character_type, lesson):
    narrations = [
        f"CRASH! Something fell from the sky! {character_name} the {character_type} looked up and could not believe what they were seeing! This was going to be the most amazing day ever!",
        f"It all started that very morning when {character_name} woke up to the most beautiful golden sunrise. The whole world seemed to be sparkling and full of magic possibilities today!",
        f"{character_name} lived in the most wonderful place you could ever imagine! Every flower had its own special song and every tree had stories hidden in its branches just waiting to be found!",
        f"Best friend Pip came running up with the most excited look on their face! You have to come see this right now! Something incredible has happened and we need you! Hurry hurry hurry!",
        f"Together they ran through the swishing tall grass until they found it! A mysterious glowing door standing all by itself in the middle of the meadow! Where could it possibly lead?",
        f"But before they could open it something went terribly wrong! The door began to shake and rumble! Strange sounds came from inside! Oh no! This did not look good at all!",
        f"I know what we can do! said {character_name} with sudden confidence! We just need to find the three golden keys that are hidden somewhere in our world! Easy peasy!",
        f"The first key was supposedly hidden deep inside the Whispering Woods where the trees talked to each other in the wind! They were going to need all their courage for this one!",
        f"Inside the woods it was both beautiful and a little bit scary! Glowing mushrooms lit the path! The trees really did seem to be whispering soft secrets all around them!",
        f"Then {character_name} remembered something important! Did you know that {lesson}? This is actually true in real life too! And it turned out to be exactly what they needed right now!",
        f"They found the first key inside a giant hollow tree! It was glowing warm and golden and felt perfectly right in {character_name}'s paw! One down and two more to go!",
        f"PLOT TWIST! The second key was guarded by a grumpy old creature who said nobody had ever been kind enough to deserve it! Things were getting very complicated very fast indeed!",
        f"But instead of giving up {character_name} sat down right there and started helping the grumpy creature with what they needed! Sometimes the best solution is the most unexpected one!",
        f"The creature's eyes went wide with surprise! In all my very long years nobody has ever done that before! Here is your key and thank you from the bottom of my heart!",
        f"Two keys and one more to go! The final key was at the very top of the tallest mountain! Their legs were tired and the path was steep but they absolutely could not stop now!",
        f"Halfway up the mountain {character_name} started to feel really worried! What if this does not work? What if the door leads nowhere? The doubt was getting heavier than the climb!",
        f"Pip looked at {character_name} with total confidence and said I believe in you completely! You have gotten us this far and you can absolutely get us the rest of the way there!",
        f"Those encouraging words were exactly what was needed! {character_name} took a deep breath of the cool mountain air and kept going one brave step after another until they made it!",
        f"They had all three keys now! But when they got back to the door a terrible storm suddenly appeared from nowhere! Thunder crashed and lightning flashed and the rain poured down heavily!",
        f"They huddled together under a big leaf feeling completely defeated and small! The storm raged and raged! Was this really the end of their incredible adventure before it even properly began?",
        f"Then at the worst darkest moment {character_name} looked down and noticed something extraordinary! The three golden keys were glowing in a special pattern pointing at something very specific!",
        f"AMAZING DISCOVERY! The storm WAS the door! The lightning bolts were actually a beautiful magical language! And {character_name} knew exactly what it was saying just from looking at the keys!",
        f"Heart pounding with excitement {character_name} held up all three keys together! They fit perfectly into three spots in the lightning! The whole sky exploded into the most gorgeous colors imaginable!",
        f"The door swung open revealing a world of pure golden light! Beautiful music filled the air! It was a magical place where everything that was broken could finally be made whole and perfect again!",
        f"Inside the magical world they found exactly what was needed! The solution to every problem they had faced! And they understood now why the whole journey had been absolutely necessary!",
        f"In the most spectacular moment {character_name} used everything learned on the journey — bravery and kindness and friendship and {lesson}! The whole world began to transform beautifully around them!",
        f"With a magical golden flash everything was restored even better than before! {character_name} and Pip danced with pure joy together under a sky full of brilliant rainbow-colored sparkles!",
        f"As they walked back home together the world felt completely different! Not because anything around them had changed but because they both had grown and learned so very much about themselves!",
        f"That night {character_name} looked up at all the stars and understood something important and beautiful! {lesson}! This was the real treasure they had found on their amazing adventure today!",
        f"And that is our wonderful story for today amazing friends! Did you enjoy it? Give us a huge thumbs up and subscribe for a brand new magical adventure every single day! We love you! Bye bye!",
    ]
    scenes = []
    for i, narr in enumerate(narrations[:SCENE_COUNT]):
        scenes.append({
            "scene_number": i+1,
            "scene_title":  f"Scene {i+1}",
            "narration":    narr,
            "image_prompt": f"cute colorful 3D cartoon of {character_name} the {character_type}, scene {i+1}, pixar style, bright colors",
            "sound_effect": "cheerful adventure music",
            "text_overlay": topic[:18]
        })
    return {
        "episode_title":       f"{topic} | Kids Adventure Story",
        "episode_description": f"Join {character_name} on an incredible adventure! A magical story about {lesson}.",
        "total_scenes":        len(scenes),
        "scenes":              scenes
}
