import os
import datetime
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from asgiref.wsgi import WsgiToAsgi

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

# ===== CONFIG =====
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003515229818
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://yourapp.onrender.com/<BOT_TOKEN>

# ===== FLASK APP =====
flask_app = Flask(__name__)
flask_app_asgi = WsgiToAsgi(flask_app)  # wrap for async

# ===== TELEGRAM HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to AIglobaltradingbot ⚡️",
        reply_markup=main_menu()
    )

async def market_update(context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.datetime.utcnow()
    if not (8 <= now_utc.hour < 22):  # only post 08–22 UTC
        return
    try:
        data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        ).json()

        btc_price = data["bitcoin"]["usd"]
        btc_change = data["bitcoin"]["usd_24h_change"]
        eth_price = data["ethereum"]["usd"]
        eth_change = data["ethereum"]["usd_24h_change"]

        summary = f"🚨 BTC ${btc_price:,} ({btc_change:.2f}%) | ETH ${eth_price:,} ({eth_change:.2f}%)"
        keyboard = [[InlineKeyboardButton("📈 Trade Now", url="https://your-trading-link.com")]]
        await context.bot.send_message(CHANNEL_ID, summary, reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        print("Market update error:", e)

# ===== BUILD TELEGRAM APP =====
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# ===== SETUP JOB QUEUE & WEBHOOK =====
import asyncio
async def setup_bot():
    await application.initialize()
    application.job_queue.run_repeating(market_update, interval=30, first=10)
    await application.bot.set_webhook(WEBHOOK_URL)

asyncio.get_event_loop().create_task(setup_bot())

# ===== FLASK ROUTES =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(await request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot running 🚀", 200

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

from asgiref.wsgi import WsgiToAsgi

flask_app_asgi = WsgiToAsgi(flask_app)
