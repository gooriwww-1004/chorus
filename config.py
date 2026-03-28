from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_TIMEOUT = 20

CATEGORY_PROVIDERS = {
    "sports":  ["gemini_A", "gemini_B"],
    "science": ["gemini_A", "gemini_C"],
    "work":    ["gemini_B", "gemini_D"],
    "daily":   ["gemini_C", "gemini_D"],
}

CATEGORY_LABELS = {
    "sports":  "🏆 스포츠·로또",
    "science": "🔬 과학·기술",
    "work":    "📚 일·공부",
    "daily":   "💬 연애·일상",
}
