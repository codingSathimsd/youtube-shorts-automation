import json
import requests
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL

BRAIN_FILE = "kids/brain.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def load_brain():
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def save_brain(brain):
    with open(BRAIN_FILE, "w") as f:
        json.dump(brain, f, indent=2)

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def update_brain_with_insights(insights):
    """Update brain.json based on performance insights"""
    print("🧠 Updating brain with new learnings...")
    brain = load_brain()

    # Update best performing topics
    best_topics = insights.get("best_topics", [])
    existing_best = brain.get("best_performing_topics", [])
    combined = list(set(existing_best + best_topics))[-20:]  # keep top 20
    brain["best_performing_topics"] = combined

    # Update avg views by category
    avg_views = insights.get("avg_views", 0)
    if avg_views > 0:
        brain["avg_views_by_category"]["mixed"] = avg_views

    # Use Groq to improve prompt templates based on what worked
    if best_topics and insights.get("total_videos", 0) >= 3:
        try:
            improvement_prompt = f"""You are an AI that improves YouTube kids channel strategies.

PERFORMANCE DATA:
- Total videos: {insights.get('total_videos', 0)}
- Average views: {insights.get('avg_views', 0):.0f}
- Best performing topics: {best_topics}
- Best video: {insights.get('best_video', {})}

CURRENT PROMPT TEMPLATES:
{json.dumps(brain['prompt_templates'], indent=2)}

CURRENT BEST TITLE FORMATS:
{brain['best_title_formats']}

Based on this performance data, suggest improvements to:
1. The script writing prompt (make videos more engaging)
2. The image generation prompt (make visuals more appealing)
3. Two new title formats that would get more clicks
4. One new thumbnail style that would get more clicks

Respond ONLY in JSON:
{{
  "improved_script_prompt": "...",
  "improved_image_prompt": "...",
  "new_title_formats": ["...", "..."],
  "new_thumbnail_style": "..."
}}"""

            response = call_groq(improvement_prompt)
            response = response.replace("```json", "").replace("```", "").strip()
            improvements = json.loads(response)

            # Apply improvements
            brain["prompt_templates"]["script"] = improvements.get(
                "improved_script_prompt", brain["prompt_templates"]["script"])
            brain["prompt_templates"]["image"] = improvements.get(
                "improved_image_prompt", brain["prompt_templates"]["image"])

            new_formats = improvements.get("new_title_formats", [])
            brain["best_title_formats"] = (brain["best_title_formats"] + new_formats)[-8:]

            new_thumb = improvements.get("new_thumbnail_style", "")
            if new_thumb:
                brain["best_thumbnail_styles"] = (
                    brain["best_thumbnail_styles"] + [new_thumb])[-5:]

            print("  ✅ Prompt templates improved by AI")
        except Exception as e:
            print(f"  Groq improvement error: {e}")

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
        print("  No insights available yet, skipping improvement")
    print("✅ Learning cycle complete\n")
  
