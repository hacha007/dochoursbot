from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import os
import logging
from config import TOKEN
import commands

# Enable logging to see what's happening
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment
PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

# Build application
app = ApplicationBuilder().token(TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", commands.start))
app.add_handler(CommandHandler("in", commands.clock_in))
app.add_handler(CallbackQueryHandler(commands.handle_shift_selection, pattern="^shift_"))
app.add_handler(CommandHandler("out", commands.clock_out))
app.add_handler(CommandHandler("break", commands.break_start))
app.add_handler(CommandHandler("back", commands.break_end))
app.add_handler(CommandHandler("today", commands.today))
app.add_handler(CommandHandler("week", commands.week))
app.add_handler(CommandHandler("month", commands.month))

if __name__ == "__main__":
    if RENDER_EXTERNAL_HOSTNAME:
        # Production: Use webhook
        webhook_url = f"https://{RENDER_EXTERNAL_HOSTNAME}/webhook"
        logger.info(f"Starting webhook on port {PORT}")
        logger.info(f"Webhook URL: {webhook_url}")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            url_path="/webhook"
        )
    else:
        # Local development: Use polling
        logger.info("Starting polling mode (local development)")
        app.run_polling()