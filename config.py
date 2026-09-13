import os
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

# API Keys & Email Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", GMAIL_USER).strip()

# Email Server Settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL

# User Agent for HTTP/RSS Requests
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Target Categories & Search Queries
CATEGORIES = [
    {
        "id": "ai",
        "title": "Artificial Intelligence",
        "icon": "🤖",
        "query": (
            '("Artificial Intelligence" OR "Generative AI" OR "OpenAI" OR '
            '"Anthropic" OR "Google AI" OR "LLM" OR "Machine Learning") when:1d'
        ),
        "target_count": 5,
    },
    {
        "id": "tech",
        "title": "MNCs, Tech & Software Engineering",
        "icon": "💻",
        "query": (
            '("software engineering" OR "tech industry" OR "Big Tech" OR '
            'Google OR Microsoft OR Apple OR Amazon OR Meta OR Nvidia OR '
            'TCS OR Infosys OR "tech layoffs" OR "cloud computing") when:1d'
        ),
        "target_count": 5,
    },
    {
        "id": "politics",
        "title": "Geopolitics & Indian Politics",
        "icon": "🌍",
        "query": (
            '("Indian politics" OR "Geopolitics" OR "Parliament" OR '
            '"Government of India" OR "diplomacy" OR "bilateral relations" OR '
            '"foreign policy" OR "Elections") when:1d'
        ),
        "target_count": 5,
    },
]
