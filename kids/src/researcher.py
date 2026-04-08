import json
import requests
import random
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL, FALLBACK_TOPICS

BRAIN_FILE = "kids/brain.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def load_brain():
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def save_brain(brain):
    with open(BRAIN_FILE, "w") as f:
        json.dump(brain, f, indent=2)

def call_groq(prompt, max_tokens=1000):
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

def fetch_youtube_trending_kids():
    """Fetch trending kids video titles from YouTube RSS - no API key needed"""
    try:
        urls = [
            "https://www.youtube.com/feeds/videos.xml?chart=mostPopular&videoCategoryId=27&hl=en&regionCode=US",
            "https://www.youtube.com/feeds/videos.xml?chart=mostPopular&videoCategoryId=1&hl=en&regionCode=US",
        ]
        trending_titles = []
        for url in urls:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(resp.content)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    for entry in root.findall('atom:entry', ns)[:10]:
                        title_el = entry.find('atom:title', ns)
                        if title_el is not None:
                            trending_titles.append(title_el.text)
            except:
                continue
        return trending_titles
    except Exception as e:
        print(f"YouTube trending fetch error: {e}")
        return []

def fetch_google_trends_kids():
    """Fetch trending searches from Google Trends RSS - no API key needed"""
    try:
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            items = []
            for item in root.findall('.//item')[:20]:
                title = item.find('title')
                if title is not None:
                    items.append(title.text)
            return items
        return []
    except Exception as e:
        print(f"Google Trends fetch error: {e}")
        return []

def analyze_trends_with_groq(youtube_trends, google_trends, brain):
    """Use Groq to analyze trends and pick the best kids video topic"""
    try:
        best_topics = brain.get("best_performing_topics", [])
        best_formats = brain.get("best_title_formats", [])

        prompt = f"""You are a YouTube kids channel strategist. Analyze these trends and recommend the BEST topic for a kids animation video today.

YOUTUBE TRENDING TITLES: {youtube_trends[:15]}
GOOGLE TRENDS: {google_trends[:15]}
OUR BEST PERFORMING TOPICS SO FAR: {best_topics[-10:]}
OUR BEST TITLE FORMATS: {best_formats}
TODAY'S DATE: {datetime.now().strftime('%B %d, %Y')}

Recommend the single BEST topic for a kids animated video today (mix of story + learning).

Respond ONLY in this JSON format with no extra text:
{{
  "topic": "...",
  "why_viral": "...",
  "emotion": "wonder",
  "character_name": "...",
  "character_type": "...",
  "lesson": "...",
  "category": "mixed"
}}"""

        response = call_groq(prompt, max_tokens=500)
        text = response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        result = json.loads(text)
        print(f"  Research complete. Topic: {result['topic']}")
        return result

    except Exception as e:
        print(f"Groq trend analysis error: {e}")
        topic = random.choice(FALLBACK_TOPICS)
        return {
            "topic": topic,
            "why_viral": "Educational and entertaining for kids",
            "emotion": "wonder",
            "character_name": "Sunny",
            "character_type": "friendly lion cub",
            "lesson": "Kindness and sharing",
            "category": "mixed"
        }

def research_today():
    """Main research function - returns today's best topic plan"""
    print("🔍 Researching trends...")
    brain = load_brain()

    youtube_trends = fetch_youtube_trending_kids()
    print(f"  Found {len(youtube_trends)} YouTube trending titles")

    google_trends = fetch_google_trends_kids()
    print(f"  Found {len(google_trends)} Google trends")

    topic_plan = analyze_trends_with_groq(youtube_trends, google_trends, brain)

    # Save trending data to brain
    brain["trending_topics_today"] = youtube_trends[:10]
    brain["last_updated"] = datetime.now().isoformat()
    save_brain(brain)

    return topic_plan
        
