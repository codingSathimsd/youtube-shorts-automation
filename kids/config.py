import os

# === API KEYS ===
GROQ_API_KEY          = os.environ.get("GROQ_API_KEY", "")
YOUTUBE_CLIENT_ID     = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")

# === GROQ MODEL ===
GROQ_MODEL = "llama3-70b-8192"

# === VIDEO SETTINGS ===
VIDEO_WIDTH  = 1920
VIDEO_HEIGHT = 1080
FPS          = 24

# === 30 SCENES × ~28 seconds avg = ~14 minutes ===
TARGET_DURATION_MINUTES = 14
SCENE_COUNT             = 30

# === VOICE ===
VOICE_LANG = "en"
VOICE_SLOW = False

# === PATHS ===
OUTPUT_DIR   = "kids_output"
ASSETS_DIR   = "kids/assets"
MUSIC_DIR    = f"{ASSETS_DIR}/music"
FONTS_DIR    = f"{ASSETS_DIR}/fonts"
BRAIN_FILE   = "kids/brain.json"
MEMORY_FILE  = "kids/memory.json"

# === YOUTUBE ===
VIDEO_CATEGORY_ID = "27"
MADE_FOR_KIDS     = True
VIDEO_LANGUAGE    = "en"
DEFAULT_PRIVACY   = "public"

# === CHANNEL ===
CHANNEL_NAME = "KidsViral AI"

# === FALLBACK TOPICS ===
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
    "How Plants Drink Water",
    "The Dragon Who Was Afraid of Fire",
    "The Rabbit Who Found the Magic Garden",
]
