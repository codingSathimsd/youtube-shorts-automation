import google.generativeai as genai
import os
import json
import time

def generate_seo(video_title, transcript, channel_name, topic=None):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # Try models in order until one works
    models_to_try = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro-latest',
        'gemini-pro',
    ]
    
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

    last_error = None
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            time.sleep(2)  # avoid rate limit
            response = model.generate_content(prompt)
            text = response.text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            metadata = json.loads(text)
            print(f"SEO Title: {metadata['title']}")
            return metadata
        except Exception as e:
            print(f"Model {model_name} failed: {str(e)[:100]}")
            last_error = e
            time.sleep(3)
            continue

    # If all Gemini models fail use hardcoded fallback
    print("All Gemini models failed. Using fallback metadata.")
    return {
        "title": f"{subject.title()} That Will Blow Your Mind",
        "description": f"Amazing facts about {subject}. Watch till the end! Subscribe for daily content.",
        "tags": [subject, "facts", "viral", "shorts", "trending", "amazing", "mindblowing"],
        "hashtags": f"#Shorts #viral #trending #{subject.replace(' ', '')}"
    }
