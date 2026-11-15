"""Trigger #2: Telegram. Uses the plain Telegram Bot HTTP API (no extra library)."""

import re

import requests

import config

# Matches: "Connect with event leads for Zomato in Gurgaon"
COMMAND = re.compile(r"\bfor\s+(?P<company>.+)\s+in\s+(?P<city>.+?)[.!?]*$", re.IGNORECASE)

HELP_TEXT = 'Send me: "Connect with event leads for <Company> in <City>"'

_next_update_id = 0  # tells Telegram which messages we already read


def _call(method, **params):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/{method}"
    return requests.post(url, json=params, timeout=30).json()


def get_new_messages():
    """Returns a list of (chat_id, text) received since the last call."""
    global _next_update_id
    data = _call("getUpdates", offset=_next_update_id, timeout=0)
    messages = []
    for update in data.get("result", []):
        _next_update_id = update["update_id"] + 1
        message = update.get("message") or {}
        if message.get("text"):
            messages.append((message["chat"]["id"], message["text"]))
    return messages


def parse_command(text):
    """Returns (company, city) or None if the message doesn't match."""
    match = COMMAND.search(text.strip())
    if not match:
        return None
    return match.group("company").strip(), match.group("city").strip()


def reply(chat_id, text):
    _call("sendMessage", chat_id=chat_id, text=text)
