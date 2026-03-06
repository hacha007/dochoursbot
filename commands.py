import pandas as pd
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import conn, cursor
from shifts import *
from calculations import calculate_hours
from config import SHIFT_TYPES

import pytz

# Set your timezone (change to your location)
LOCAL_TZ = pytz.timezone('Europe/London')  # Change to your timezone

def get_local_now():
    """Get current time in local timezone"""
    return datetime.now(pytz.UTC).astimezone(LOCAL_TZ)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Work hours bot ready.")


async def clock_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show dropdown menu for shift selection instead of requiring typed argument"""
    last = get_last_shift()

    if last and last[4] is None:
        await update.message.reply_text("⚠️ You are already clocked in.")
        return

    # Create inline keyboard with shift options
    keyboard = []
    for shift_key, shift_info in SHIFT_TYPES.items():
        # Create a clean display name
        display_name = f"{shift_key} ({shift_info['start']} - {shift_info['end']})"
        # Callback data must be unique and start with "shift_" for our handler
        callback_data = f"shift_{shift_key}"
        keyboard.append([InlineKeyboardButton(display_name, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select your shift type:",
        reply_markup=reply_markup
    )


async def handle_shift_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the callback when user selects a shift from the dropdown"""
    query = update.callback_query
    await query.answer()  # Answer the callback to remove loading state

    # Extract shift type from callback data (remove "shift_" prefix)
    shift = query.data.replace("shift_", "")

    if shift not in SHIFT_TYPES:
        await query.edit_message_text("Invalid shift type selected.")
        return

    # Check again if already clocked in (safety check)
    last = get_last_shift()
    if last and last[4] is None:
        await query.edit_message_text("⚠️ You are already clocked in.")
        return

    now =  get_local_now()
    insert_shift(now.date().isoformat(), shift, now.isoformat())

    await query.edit_message_text(
        f"✅ Clocked in ({shift}) at {now.strftime('%H:%M')}"
    )


async def clock_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = get_last_shift()

    if not last or last[4] is not None:
        await update.message.reply_text("⚠️ No active shift.")
        return

    now = get_local_now()
    update_clock_out(now.isoformat())

    hours = calculate_hours(
        last[3], now.isoformat(), last[5], last[6]
    )

    await update.message.reply_text(
        f"Clocked out\nTotal hours: {round(hours,2)}"
    )


async def break_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = get_last_shift()

    if last[5] is not None and last[6] is None:
        await update.message.reply_text("⚠️ Break already started.")
        return

    now = get_local_now()
    update_break_start(now.isoformat())

    await update.message.reply_text("Break started")


async def break_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = get_last_shift()

    if last[5] is None:
        await update.message.reply_text("⚠️ Break not started.")
        return

    now = get_local_now()
    update_break_end(now.isoformat())

    await update.message.reply_text("Break ended")


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = get_local_now().date().isoformat()

    cursor.execute("""
    SELECT * FROM shifts
    WHERE date=?
    ORDER BY id DESC
    LIMIT 1
    """,(today,))

    shift = cursor.fetchone()

    if not shift:
        await update.message.reply_text("No shift today.")
        return

    if shift[4] is None:
        await update.message.reply_text("Shift still active.")
        return

    hours = calculate_hours(
        shift[3], shift[4], shift[5], shift[6]
    )

    await update.message.reply_text(
        f"Today's hours: {round(hours,2)}"
    )


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    week_ago = (get_local_now() - timedelta(days=7)).date()

    df = pd.read_sql("SELECT * FROM shifts", conn)

    if df.empty:
        await update.message.reply_text("No data yet.")
        return

    df["date"] = pd.to_datetime(df["date"]).dt.date

    df = df[df["date"] >= week_ago]

    if df.empty:
        await update.message.reply_text("No shifts this week.")
        return

    total = 0

    for _, row in df.iterrows():
        if row["clock_out"]:
            total += calculate_hours(
                row["clock_in"],
                row["clock_out"],
                row["break_start"],
                row["break_end"]
            )

    await update.message.reply_text(
        f"Hours worked this week: {round(total,2)}"
    )


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month_ago = (get_local_now()- timedelta(days=30)).date()

    df = pd.read_sql("SELECT * FROM shifts", conn)

    if df.empty:
        await update.message.reply_text("No data yet.")
        return

    df["date"] = pd.to_datetime(df["date"]).dt.date

    df = df[df["date"] >= month_ago]

    if df.empty:
        await update.message.reply_text("No shifts this month.")
        return

    total = 0

    for _, row in df.iterrows():
        if row["clock_out"]:
            total += calculate_hours(
                row["clock_in"],
                row["clock_out"],
                row["break_start"],
                row["break_end"]
            )

    await update.message.reply_text(
        f"Hours worked this month: {round(total,2)}"
    )