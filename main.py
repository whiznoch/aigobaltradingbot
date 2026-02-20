import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from router_callback import qa_callback_router
from config import BOT_TOKEN
from database import conn, cur
from keyboards import main_menu
from router_text import text_router

# Flask app
flask_app = Flask(__name__)

# Telegram application
application = Application.builder().token(BOT_TOKEN).build()


# -----------------------
# START COMMAND
# -----------------------
async def start(update: Update, context):
    user = update.effective_user

    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user.id, user.username),
    )
    conn.commit()

    await update.message.reply_text(
        "Welcome to AIglobaltradingbot 🚀",
        reply_markup=main_menu(),
    )


# -----------------------
# REGISTER HANDLERS
# -----------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))


# -----------------------
# INITIALIZE APP ON STARTUP
# -----------------------
loop = asyncio.get_event_loop()
loop.run_until_complete(application.initialize())
loop.run_until_complete(application.start())


# -----------------------
# WEBHOOK ROUTE
# -----------------------
@flask_app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    loop.run_until_complete(application.process_update(update))

    return "ok"
