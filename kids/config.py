import os

# === API KEYS (from GitHub Secrets) ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")

# === GEMINI MODEL ===
GEMINI_MODEL = "gemini-2.0-flash"

# === GROQ MODEL ===
GROQ_MODEL = "llama3-8b-8192"

# === VIDEO SETTINGS ===
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24
TARGET_DURATION_MINUTES = 12  # target ~12 min video
SCENE_COUNT = 18              # 18 scenes x ~40sec each = ~12 min

# === VOICE SETTINGS ===
VOICE_LANG = "en"
VOICE_SLOW = False

# === PATHS ===
OUTPUT_DIR = "kids_output"
ASSETS_DIR = "kids/assets"
MUSIC_DIR = f"{ASSETS_DIR}/music"
FONTS_DIR = f"{ASSETS_DIR}/fonts"
BRAIN_FILE = "kids/brain.json"
MEMORY_FILE = "kids/memory.json"

# === YOUTUBE SETTINGS ===
VIDEO_CATEGORY_ID = "27"       # Education
MADE_FOR_KIDS = True
VIDEO_LANGUAGE = "en"
DEFAULT_PRIVACY = "public"

# === CHANNEL IDENTITY ===
CHANNEL_NAME = "KidsViral AI"
CHANNEL_INTRO_TEXT = "Welcome to KidsViral AI!"
CHARACTER_NAME = "Sunny"       # main character name for consistency

# === TOPIC SEEDS (fallback if trending research fails) ===
FALLBACK_TOPICS = [
    "The Lion Who Learned to Share",
    "How Rainbows Are Made",
    "The Little Robot Who Made Friends",
    "Why Do Stars Twinkle?",
    "The Brave Little Turtle",
    "How Butterflies Grow",
    "The Magic of Numbers 1 to 10",
    "Why Do We Sleep?",
    "The Friendly Cloud's Journey",
    "How Plants Drink Water"
]

