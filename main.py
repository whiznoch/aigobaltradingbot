import os
import asyncio
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
import requests
import datetime

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003515229818
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

flask_app = Flask(__name__)

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to AIglobaltradingbot ⚡️", 
        reply_markup=main_menu()
    )

async def market_update(context: ContextTypes.DEFAULT_TYPE):
    now_utc = datetime.datetime.utcnow()
    if not (8 <= now_utc.hour < 22):
        print(f"Skipping market update at {now_utc.hour}:00 UTC")
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

# ===== GLOBAL APPLICATION =====
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

async def start_job_queue():
    await application.initialize()
    # Only now job_queue exists
    application.job_queue.run_repeating(market_update, interval=7200, first=10)
    await application.bot.set_webhook(WEBHOOK_URL)

# Launch the job queue in background when Flask starts
asyncio.get_event_loop().create_task(start_job_queue())

# ===== FLASK ROUTES =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.get_event_loop().create_task(application.process_update(update))
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot running 🚀", 200
