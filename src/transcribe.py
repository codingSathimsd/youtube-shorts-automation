import whisper

def add_captions(video_path):
    print("Transcribing audio...")
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    transcript = result["text"]
    print(f"Transcript preview: {transcript[:200]}...")
    return transcript
