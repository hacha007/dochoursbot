import os

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN environment variable set!")
SHIFT_TYPES = {
    "shift 07:30": {"start": "07:30", "end": "16:00"},
    "shift 09:30": {"start": "09:30", "end": "18:00"},
    "shift 11:30": {"start": "11:30", "end": "20:00"},
    "night": {"start": "20:00", "end": "08:00"},
    "24h": {"start": "20:00", "end": "20:00"}
}