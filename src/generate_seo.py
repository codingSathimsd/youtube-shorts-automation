import os
import json
import random
from groq import Groq

def generate_facts_and_seo(topic):
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = f"""
You are a viral YouTube Shorts content creator.
Topic: {topic}

Generate content for a 45-second YouTube Short.

Return ONLY valid JSON, no markdown, no extra text:
{{
    "facts": [
        "Fact 1 about {topic} — under 15 words, shocking or surprising",
        "Fact 2 about {topic} — under 15 words, shocking or surprising",
        "Fact 3 about {topic} — under 15 words, shocking or surprising",
        "Fact 4 about {topic} — under 15 words, shocking or surprising",
        "Fact 5 about {topic} — under 15 words, shocking or surprising"
    ],
    "hook": "Opening hook sentence under 10 words that creates curiosity",
    "title": "YouTube Shorts title under 60 chars starting with hook word",
    "description": "2-3 sentences about the topic with keywords. End with: Follow for daily facts!",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
    "hashtags": "#Shorts #facts #viral #trending #didyouknow"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"Title: {data['title']}")
        print(f"Facts generated: {len(data['facts'])}")
        return data
    except Exception as e:
        print(f"Groq failed: {e}")
        # Smart fallback
        return {
            "facts": [
                f"95% of people never learn this about {topic}",
                f"Scientists discovered something shocking about {topic}",
                f"This {topic} fact will completely change your mindset",
                f"Most people get {topic} completely wrong",
                f"The truth about {topic} nobody talks about"
            ],
            "hook": f"You won't believe this about {topic}!",
            "title": f"Mind Blowing Facts About {topic.title()[:40]}",
            "description": f"These {topic} facts will completely change how you think. Most people have no idea about this. Follow for daily facts!",
            "tags": [topic, "facts", "viral", "shorts", "trending", "mindblowing", "didyouknow", "amazing"],
            "hashtags": "#Shorts #facts #viral #trending #didyouknow"
        }
