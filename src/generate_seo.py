import google.generativeai as genai
import os
import json

def generate_seo(video_title, transcript_snippet, channel_name):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are a YouTube Shorts SEO expert.
Based on this content, generate viral metadata.

Original Video Title: {video_title}
Channel: {channel_name}
Transcript snippet: {transcript_snippet[:500]}

Return ONLY valid JSON in this exact format, no extra text:
{{
    "title": "catchy title under 60 chars",
    "description": "2-3 sentence description with keywords and call to action",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "hashtags": "#Shorts #viral #trending"
}}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    metadata = json.loads(text)
    print(f"SEO Title: {metadata['title']}")
    return metadata
