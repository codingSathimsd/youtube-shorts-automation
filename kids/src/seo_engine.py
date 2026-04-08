import json
import requests
from config import GROQ_API_KEY, GROQ_MODEL, CHANNEL_NAME

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(prompt, max_tokens=1500):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def generate_viral_seo(topic_plan, script, video_duration_minutes):
    """Generate next-level viral SEO for the video"""
    print("🏷️  Generating viral SEO with Groq...")

    topic = topic_plan.get("topic", "")
    character = topic_plan.get("character_name", "")
    lesson = topic_plan.get("lesson", "")
    episode_title = script.get("episode_title", topic)
    emotion = topic_plan.get("emotion", "wonder")

    # Generate chapters/timestamps from scenes
    scenes = script.get("scenes", [])
    chapters = generate_chapters(scenes, video_duration_minutes)

    prompt = f"""You are a top YouTube SEO expert specializing in kids education channels with millions of subscribers.

VIDEO DETAILS:
- Topic: {topic}
- Main Character: {character}
- Core Lesson: {lesson}
- Episode Title: {episode_title}
- Target Emotion: {emotion}
- Duration: ~{video_duration_minutes:.0f} minutes
- Channel: {CHANNEL_NAME}
- Target Audience: Kids aged 3-8 and their parents

Generate VIRAL YouTube SEO metadata. The goal is MAXIMUM clicks and watch time.

TITLE RULES:
- Use power words: Amazing, Magic, Funny, Cute, Best, Learn, Story
- Include emojis (2-3 max)
- Under 70 characters
- Make parents AND kids want to click
- Include the main topic keyword naturally

DESCRIPTION RULES:
- First 2 lines are the HOOK (shows before "show more") - must be irresistible
- Include timestamps/chapters
- Include call to action (subscribe, like, comment)
- Include 5-7 paragraphs
- Naturally include keywords 8-10 times
- End with 10 relevant hashtags

TAGS RULES:
- Exactly 500 characters of tags
- Mix of: broad tags, specific tags, trending tags
- Include variations and misspellings parents might type

Respond ONLY in this JSON format:
{{
  "title": "...",
  "description": "...",
  "tags": ["tag1", "tag2", ...],
  "hashtags": "#kids #cartoon ...",
  "thumbnail_text": "3-4 words for thumbnail text overlay",
  "chapters": "{chapters}"
}}"""

    try:
        response = call_groq(prompt)
        response = response.replace("```json", "").replace("```", "").strip()
        seo = json.loads(response)
        print(f"✅ SEO generated: '{seo['title']}'")
        return seo
    except Exception as e:
        print(f"SEO generation error: {e}")
        return generate_fallback_seo(topic, episode_title, character, chapters)

def generate_chapters(scenes, total_duration_minutes):
    """Generate YouTube chapters from scenes"""
    if not scenes:
        return "0:00 Introduction"

    total_seconds = total_duration_minutes * 60
    seconds_per_scene = total_seconds / len(scenes)

    chapters = ["0:00 Introduction"]
    for i, scene in enumerate(scenes[1:], 1):
        t = int(i * seconds_per_scene) + 5  # +5 for intro
        mins = t // 60
        secs = t % 60
        title = scene.get("scene_title", f"Scene {i+1}")[:40]
        chapters.append(f"{mins}:{secs:02d} {title}")

    return "\n".join(chapters)

def generate_fallback_seo(topic, episode_title, character, chapters):
    """Fallback SEO if Groq fails"""
    title = f"🌟 {episode_title[:50]} | Kids Story"
    return {
        "title": title[:70],
        "description": (
            f"🎉 Join {character} in this amazing adventure! {topic}\n\n"
            f"Perfect for kids aged 3-8! This fun and educational video will "
            f"entertain and teach your little ones important life lessons.\n\n"
            f"📚 What your child will learn:\n"
            f"✅ Fun story with lovable characters\n"
            f"✅ Important life lessons\n"
            f"✅ Educational content\n\n"
            f"⏱️ CHAPTERS:\n{chapters}\n\n"
            f"👍 LIKE this video if your kids enjoyed it!\n"
            f"🔔 SUBSCRIBE for new videos every day!\n"
            f"💬 COMMENT your favorite part!\n\n"
            f"#kidsstories #cartoonsforkids #kidslearning #educationalvideos #kidsvideo"
        ),
        "tags": [
            "kids stories", "cartoon for kids", "kids learning", "educational videos",
            "children stories", "animated stories", "kids cartoons", "bedtime stories",
            "preschool learning", "toddler videos", topic.lower(), character.lower()
        ],
        "hashtags": "#kidsstories #cartoonsforkids #kidslearning #educationalvideos",
        "thumbnail_text": topic[:20],
        "chapters": chapters
}

