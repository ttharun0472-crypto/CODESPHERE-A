import os
from dotenv import load_dotenv

load_dotenv()

JEV_API_KEY = os.getenv("JEV_AI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def check_ai_configuration():
    return {
        "jev_configured": bool(JEV_API_KEY),
        "gemini_configured": bool(GEMINI_API_KEY),
        "openai_configured": bool(OPENAI_API_KEY),
    }