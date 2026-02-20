import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)

# Create Telegram Application (async)
application = ApplicationBuilder().token(TOKEN).build()

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive 🚀")

application.add_handler(CommandHandler("start", start))


# ===== WEBHOOK ROUTE =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.process_update(update))
    loop.close()

    return "ok", 200


@flask_app.route("/")
def index():
    return "Bot running 🚀", 200
