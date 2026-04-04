# ===== OPTIMIZED TOPIC LIST =====
TOPICS = [
    # Psychology — highest shareability
    "psychology facts that change how you think",
    "human behavior secrets",
    "mind tricks psychology",

    # Finance — highest CPM for affiliates
    "money habits of millionaires",
    "passive income ideas",
    "investing tips for beginners",

    # Tech & AI — trending 2026
    "artificial intelligence facts",
    "technology that will change the world",
    "future technology predictions",

    # Motivation — India + global
    "success mindset habits",
    "discipline motivation",
    "self improvement tips",

    # Health — evergreen
    "health facts that will shock you",
    "brain health tips",
    "sleep science facts",

    # Life Hacks — most saved
    "life hacks that actually work",
    "productivity hacks",
    "study hacks for students",
]

# ===== CLIP SETTINGS =====
CLIP_DURATION = 45
CLIPS_PER_RUN = 3
OUTPUT_DIR = "output_clips"
Update src/generate_seo.py — Better Titles & Hooks
import google.generativeai as genai
import os
import json
import time
import random

# Fallback titles per category
FALLBACK_TITLES = {
    "psychology": ["This Psychology Trick Will Shock You", "Your Brain Is Lying To You", "Why You Can't Stop Scrolling"],
    "money": ["Most People Never Learn This About Money", "Do This Before You Turn 25", "Why Rich People Think Differently"],
    "tech": ["AI Is Changing Everything In 2026", "This Tech Will Replace Your Job", "The Future Is Already Here"],
    "motivation": ["Do This Every Morning To Win The Day", "Why 99% Of People Stay Broke", "This 1 Habit Changes Everything"],
    "health": ["Your Body Is Warning You Right Now", "Stop Eating This Immediately", "What Happens When You Sleep"],
    "default": ["This Will Change How You Think", "Nobody Talks About This", "Watch This Before It's Too Late"],
}

def get_fallback_title(topic):
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["psych", "mind", "brain", "behavior"]):
        return random.choice(FALLBACK_TITLES["psychology"])
    elif any(w in topic_lower for w in ["money", "income", "invest", "rich", "financ"]):
        return random.choice(FALLBACK_TITLES["money"])
    elif any(w in topic_lower for w in ["tech", "ai", "artificial", "future"]):
        return random.choice(FALLBACK_TITLES["tech"])
    elif any(w in topic_lower for w in ["motiv", "success", "discipl", "self"]):
        return random.choice(FALLBACK_TITLES["motivation"])
    elif any(w in topic_lower for w in ["health", "sleep", "body", "food"]):
        return random.choice(FALLBACK_TITLES["health"])
    else:
        return random.choice(FALLBACK_TITLES["default"])

def generate_seo(video_title, transcript, channel_name, topic=None):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    subject = topic if topic else video_title

    models_to_try = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest',
        'gemini-2.0-flash',
        'gemini-pro',
    ]

    prompt = f"""
You are a viral YouTube Shorts SEO expert in 2026.
Create metadata for a short video about: {subject}

Rules:
- Title must start with a hook word (Never, Why, How, This, Stop, Watch)
- Title must create curiosity or urgency
- Tags must mix broad and specific keywords
- Description must have a call to action

Return ONLY valid JSON, no extra text, no markdown:
{{
    "title": "Hook-driven title under 60 chars",
    "description": "2-3 sentences with keywords. End with: Follow for daily facts!",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
    "hashtags": "#Shorts #viral #facts #trending #{subject.replace(' ', '').title()[:20]}"
}}
"""

    last_error = None
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            time.sleep(2)
            response = model.generate_content(prompt)
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            metadata = json.loads(text)
            print(f"SEO Title: {metadata['title']}")
            return metadata
        except Exception as e:
            print(f"Model {model_name} failed: {str(e)[:80]}")
            last_error = e
            time.sleep(3)
            continue

    # Smart fallback based on topic
    print("Using smart fallback metadata...")
    title = get_fallback_title(subject)
    return {
        "title": title,
        "description": f"{title}. These {subject} facts will completely change your perspective. Follow for daily facts that will blow your mind!",
        "tags": [subject, "facts", "viral", "shorts", "trending", "mindblowing", "didyouknow", "amazing"],
        "hashtags": f"#Shorts #viral #facts #trending #didyouknow"
    }
