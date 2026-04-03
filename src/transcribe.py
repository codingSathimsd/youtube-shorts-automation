import whisper
import os

def add_captions(video_path):
    """
    Transcribe audio using Whisper (runs locally, free)
    Returns transcript text for SEO use
    """
    print("Transcribing audio...")
    model = whisper.load_model("base")  # tiny/base/small - base is best balance
    result = model.transcribe(video_path)
    
    transcript = result["text"]
    print(f"Transcript preview: {transcript[:200]}...")
    
    return transcript
