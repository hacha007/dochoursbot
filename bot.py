from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import os
from config import TOKEN
import commands

# Get Render URL from environment
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render provides this automatically
PORT = int(os.environ.get("PORT", 10000))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", commands.start))
app.add_handler(CommandHandler("in", commands.clock_in))
app.add_handler(CallbackQueryHandler(commands.handle_shift_selection, pattern="^shift_"))
app.add_handler(CommandHandler("out", commands.clock_out))
app.add_handler(CommandHandler("break", commands.break_start))
app.add_handler(CommandHandler("back", commands.break_end))
app.add_handler(CommandHandler("today", commands.today))
app.add_handler(CommandHandler("week", commands.week))
app.add_handler(CommandHandler("month", commands.month))

# Use webhook instead of polling
if RENDER_URL:
    # Production: Use webhook
    webhook_url = f"{RENDER_URL}/webhook"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )
else:
    # Local development: Use polling
    print("Running in polling mode (local development)")
    app.run_polling()