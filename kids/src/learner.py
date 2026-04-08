import json
import os
import requests
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL

BRAIN_FILE = "kids/brain.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_BRAIN = {
    "best_performing_topics": [],
    "best_title_formats": [
        "🌟 {topic} for Kids | Fun Learning Video",
        "Learn {topic} with {character} | Kids Education"
    ],
    "best_thumbnail_styles": [
        "bright colorful cartoon with big expressive eyes"
    ],
    "prompt_templates": {
        "script": "You are a professional kids animation scriptwriter. Write engaging, fun, educational episodes for children aged 3-8.",
        "image": "cute colorful cartoon illustration, child-friendly, bright colors, happy characters, pixar-like quality",
        "title": "Create a viral YouTube title for kids content"
    },
    "avg_views_by_category": {"story": 0, "educational": 0, "mixed": 0},
    "video_performance": [],
    "total_videos_made": 0,
    "last_updated": ""
}

def load_brain():
    """Load brain — auto-create if missing"""
    if not os.path.exists(BRAIN_FILE):
        brain_dir = os.path.dirname(BRAIN_FILE)
        if brain_dir:
            os.makedirs(brain_dir, exist_ok=True)
        with open(BRAIN_FILE, "w") as f:
            json.dump(DEFAULT_BRAIN, f, indent=2)
        print(f"  ✅ brain.json created")
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def save_brain(brain):
    brain_dir = os.path.dirname(BRAIN_FILE)
    if brain_dir:
        os.makedirs(brain_dir, exist_ok=True)
    with open(BRAIN_FILE, "w") as f:
        json.dump(brain, f, indent=2)

def call_groq(prompt, max_tokens=1500):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def update_brain_with_insights(insights):
    """Update brain.json based on video performance"""
    print("🧠 Updating brain with new learnings...")
    brain = load_brain()

    best_topics = insights.get("best_topics", [])
    existing = brain.get("best_performing_topics", [])
    brain["best_performing_topics"] = list(set(existing + best_topics))[-20:]

    avg_views = insights.get("avg_views", 0)
    if avg_views > 0:
        brain["avg_views_by_category"]["mixed"] = avg_views

    if best_topics and insights.get("total_videos", 0) >= 3:
        try:
            prompt = f"""You are an AI improving a YouTube kids channel strategy.

PERFORMANCE DATA:
- Total videos: {insights.get('total_videos', 0)}
- Average views: {insights.get('avg_views', 0):.0f}
- Best topics: {best_topics}
- Best video: {insights.get('best_video', {})}

CURRENT PROMPTS:
{json.dumps(brain.get('prompt_templates', {}), indent=2)}

Suggest improvements. Respond ONLY in JSON, no extra text:
{{
  "improved_script_prompt": "...",
  "improved_image_prompt": "...",
  "new_title_formats": ["...", "..."],
  "new_thumbnail_style": "..."
}}"""

            response = call_groq(prompt)
            text = response.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                text = text[start:end]
            improvements = json.loads(text)

            brain["prompt_templates"]["script"] = improvements.get(
                "improved_script_prompt", brain["prompt_templates"]["script"])
            brain["prompt_templates"]["image"] = improvements.get(
                "improved_image_prompt", brain["prompt_templates"]["image"])
            new_formats = improvements.get("new_title_formats", [])
            brain["best_title_formats"] = (brain.get("best_title_formats", []) + new_formats)[-8:]
            new_thumb = improvements.get("new_thumbnail_style", "")
            if new_thumb:
                brain["best_thumbnail_styles"] = (
                    brain.get("best_thumbnail_styles", []) + [new_thumb])[-5:]
            print("  ✅ Prompts self-improved by Groq")
        except Exception as e:
            print(f"  Groq improvement error (skipping): {e}")

    brain["last_updated"] = datetime.now().isoformat()
    brain["total_videos_made"] = insights.get("total_videos", brain.get("total_videos_made", 0))
    save_brain(brain)
    print(f"✅ Brain updated. Total videos: {brain['total_videos_made']}")

def run_learning_cycle(insights):
    """Full self-learning cycle"""
    print("\n🔄 Running self-learning cycle...")
    if insights:
        update_brain_with_insights(insights)
    else:
        print("  No insights yet — skipping improvement")
    print("✅ Learning cycle complete\n")
        
