import os
import json
import requests
import random
from datetime import datetime

BRAIN_FILE = "kids/brain.json"

def load_brain():
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def save_brain(brain):
    with open(BRAIN_FILE, "w") as f:
        json.dump(brain, f, indent=2)

def fetch_youtube_trending_kids():
    """Fetch trending kids video titles from YouTube RSS (no API key needed)"""
    try:
        # YouTube trending RSS for Education category
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
    """Fetch trending searches related to kids content"""
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

def analyze_trends_with_gemini(youtube_trends, google_trends, brain):
    """Use Gemini to analyze trends and pick best kids video topic"""
    try:
        import google.generativeai as genai
        from config import GEMINI_API_KEY, GEMINI_MODEL, FALLBACK_TOPICS

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        best_topics = brain.get("best_performing_topics", [])
        best_formats = brain.get("best_title_formats", [])

        prompt = f"""You are a YouTube kids channel strategist. Analyze these trends and recommend the BEST topic for a kids animation video today.

YOUTUBE TRENDING TITLES: {youtube_trends[:15]}
GOOGLE TRENDS: {google_trends[:15]}
OUR BEST PERFORMING TOPICS SO FAR: {best_topics[-10:]}
OUR BEST TITLE FORMATS: {best_formats}
TODAY'S DATE: {datetime.now().strftime('%B %d, %Y')}

Based on this data, recommend:
1. The single BEST topic for a kids animated video today (mix of story + learning)
2. Why it will go viral
3. The target emotion (wonder/excitement/laughter/curiosity)
4. Main character name and type (animal/robot/human child)
5. The core lesson/learning element

Respond in JSON format:
{{
  "topic": "...",
  "why_viral": "...",
  "emotion": "...",
  "character_name": "...",
  "character_type": "...",
  "lesson": "...",
  "category": "mixed"
}}

Only respond with the JSON, nothing else."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        print(f"Research complete. Topic: {result['topic']}")
        return result

    except Exception as e:
        print(f"Gemini trend analysis error: {e}")
        from config import FALLBACK_TOPICS
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

    topic_plan = analyze_trends_with_gemini(youtube_trends, google_trends, brain)

    # Save trending topics to brain
    brain["trending_topics_today"] = youtube_trends[:10]
    brain["last_updated"] = datetime.now().isoformat()
    save_brain(brain)

    return topic_plan
      
