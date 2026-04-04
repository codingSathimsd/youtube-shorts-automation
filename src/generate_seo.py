import google.generativeai as genai
import os
import json

def generate_seo(video_title, transcript, channel_name, topic=None):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    subject = topic if topic else video_title

    prompt = f"""
You are a viral YouTube Shorts SEO expert.
Create metadata for a short video about: {subject}

Return ONLY valid JSON, no extra text, no markdown:
{{
    "title": "Hook-driven title under 60 chars with power word",
    "description": "2-3 sentences with keywords. End with subscribe CTA.",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"],
    "hashtags": "#Shorts #viral #trending #{subject.replace(' ', '')}"
}}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    metadata = json.loads(text)
    print(f"SEO Title: {metadata['title']}")
    return metadata
