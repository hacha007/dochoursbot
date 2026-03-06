import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8736121810:AAHe94TSKDFh_Uxnn9inPBhq8_st7Fe2OGw"

conn = sqlite3.connect("workhours.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shifts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
shift_type TEXT,
clock_in TEXT,
clock_out TEXT,
break_start TEXT,
break_end TEXT
)
""")
conn.commit()


def get_last_shift():
    cursor.execute("SELECT * FROM shifts ORDER BY id DESC LIMIT 1")
    return cursor.fetchone()


def calculate_hours(clock_in, clock_out, break_start, break_end):

    start = datetime.fromisoformat(clock_in)
    end = datetime.fromisoformat(clock_out)

    total = end - start

    if break_start and break_end:
        bs = datetime.fromisoformat(break_start)
        be = datetime.fromisoformat(break_end)
        total -= (be - bs)

    return total.total_seconds() / 3600


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Work hours bot ready.")


async def clock_in(update: Update, context: ContextTypes.DEFAULT_TYPE):

    shift = "normal"
    if context.args:
        shift = context.args[0]

    now = datetime.now()

    cursor.execute(
        "INSERT INTO shifts(date,shift_type,clock_in) VALUES(?,?,?)",
        (now.date().isoformat(), shift, now.isoformat())
    )

    conn.commit()

    await update.message.reply_text(f"Clocked in ({shift}) at {now.strftime('%H:%M')}")


async def clock_out(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now()

    cursor.execute("""
    UPDATE shifts
    SET clock_out=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(now.isoformat(),))

    conn.commit()

    shift = get_last_shift()

    hours = calculate_hours(
        shift[3], now.isoformat(), shift[5], shift[6]
    )

    await update.message.reply_text(f"Clocked out\nTotal hours: {round(hours,2)}")


async def break_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now()

    cursor.execute("""
    UPDATE shifts
    SET break_start=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(now.isoformat(),))

    conn.commit()

    await update.message.reply_text("Break started")


async def break_end(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now()

    cursor.execute("""
    UPDATE shifts
    SET break_end=?
    WHERE id=(SELECT id FROM shifts ORDER BY id DESC LIMIT 1)
    """,(now.isoformat(),))

    conn.commit()

    await update.message.reply_text("Break ended")


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    today = datetime.now().date().isoformat()

    cursor.execute("""
    SELECT * FROM shifts WHERE date=?
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

    await update.message.reply_text(f"Today's hours: {round(hours,2)}")


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):

    week_ago = datetime.now() - timedelta(days=7)

    df = pd.read_sql(
        "SELECT * FROM shifts", conn
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df[df["date"] >= week_ago]

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
        f"Last 7 days total: {round(total,2)} hours"
    )


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):

    month_ago = datetime.now() - timedelta(days=30)

    df = pd.read_sql(
        "SELECT * FROM shifts", conn
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df[df["date"] >= month_ago]

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
        f"Last 30 days total: {round(total,2)} hours"
    )


async def export_week(update: Update, context: ContextTypes.DEFAULT_TYPE):

    df = pd.read_sql("SELECT * FROM shifts", conn)

    file = "week_report.csv"

    df.tail(7).to_csv(file)

    await update.message.reply_document(open(file,"rb"))


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("in", clock_in))
app.add_handler(CommandHandler("out", clock_out))
app.add_handler(CommandHandler("break", break_start))
app.add_handler(CommandHandler("back", break_end))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("week", week))
app.add_handler(CommandHandler("month", month))
app.add_handler(CommandHandler("exportweek", export_week))

app.run_polling()