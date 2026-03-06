from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from config import TOKEN
import commands

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", commands.start))
app.add_handler(CommandHandler("in", commands.clock_in))  # This will now show the menu
app.add_handler(CallbackQueryHandler(commands.handle_shift_selection, pattern="^shift_"))  # Handle dropdown selection
app.add_handler(CommandHandler("out", commands.clock_out))
app.add_handler(CommandHandler("break", commands.break_start))
app.add_handler(CommandHandler("back", commands.break_end))
app.add_handler(CommandHandler("today", commands.today))
app.add_handler(CommandHandler("week", commands.week))
app.add_handler(CommandHandler("month", commands.month))

app.run_polling()