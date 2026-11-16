"""Loads every setting from the .env file so no secret is written in the code."""

import os

from dotenv import load_dotenv

load_dotenv()


def get(name, default=""):
    return os.getenv(name, default).strip()


# AI model via OpenRouter. "openrouter/free" automatically picks one of the free models.
LLM_API_KEY = get("LLM_API_KEY")
LLM_BASE_URL = get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = get("LLM_MODEL", "openrouter/free")

# Google Sheet
GOOGLE_CREDENTIALS_FILE = get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID = get("GOOGLE_SHEET_ID")

# Email finder (optional). Without it we guess the email pattern.
HUNTER_API_KEY = get("HUNTER_API_KEY")

# Email sending (Mailtrap sandbox recommended: it catches emails, nothing is really delivered)
SMTP_HOST = get("SMTP_HOST")
SMTP_PORT = int(get("SMTP_PORT", "2525"))
SMTP_USER = get("SMTP_USER")
SMTP_PASSWORD = get("SMTP_PASSWORD")
FROM_EMAIL = get("FROM_EMAIL", "bdr@gopratle.test")
FROM_NAME = get("FROM_NAME", "GoPratle Team")
# Safety switch: if set, EVERY email goes to this address instead of the real lead.
TEST_RECIPIENT = get("TEST_RECIPIENT")

# Telegram bot (optional second trigger)
TELEGRAM_BOT_TOKEN = get("TELEGRAM_BOT_TOKEN")

# Timing
FOLLOWUP_DELAY_MINUTES = int(get("FOLLOWUP_DELAY_MINUTES", "2"))
POLL_SECONDS = int(get("POLL_SECONDS", "15"))
