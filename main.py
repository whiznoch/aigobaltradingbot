import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import requests
import random

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

flask_app = Flask(__name__)

# Create one global event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Build Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
    """CoinvestGlobalBot is a leveraged decentralized trading platform built on TON, enabling users to trade crypto, forex, and commodities with up to 150x leverage — directly from their wallets.

🔐 Non-custodial execution
📈 High-performance leveraged trading
💰 Competitive yield vaults
🏆 Trading tournaments & competitions
🎯 Reward-based engagement system

Users can earn Reward Points (RP) through trading and participation, join tournaments, deposit assets into yield vaults, and scale within a unified trading ecosystem engineered for performance and growth.

Built for serious traders. Designed for scale.""",
    reply_markup=main_menu()
)

# ===== SIMPLE AI SIGNAL ENGINE =====
def generate_signal(price_change):

    if price_change > 1.5:
        trend = "Bullish"
        signal = "BUY"
    elif price_change < -1.5:
        trend = "Bearish"
        signal = "SELL"
    else:
        trend = "Sideways"
        signal = "HOLD"

    if abs(price_change) > 3:
        momentum = "Strong"
        confidence = random.randint(75, 90)
    elif abs(price_change) > 1:
        momentum = "Moderate"
        confidence = random.randint(60, 75)
    else:
        momentum = "Weak"
        confidence = random.randint(50, 60)

    return trend, momentum, signal, confidence


# ===== AI SIGNAL SUMMARY JOB =====
async def send_live_update(context: ContextTypes.DEFAULT_TYPE):
    print("AI SIGNAL JOB RUNNING...")

    try:
        btc = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        eth = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT").json()

        btc_price = float(btc["lastPrice"])
        btc_change = float(btc["priceChangePercent"])

        eth_price = float(eth["lastPrice"])
        eth_change = float(eth["priceChangePercent"])

        btc_trend, btc_momentum, btc_signal, btc_conf = generate_signal(btc_change)
        eth_trend, eth_momentum, eth_signal, eth_conf = generate_signal(eth_change)

        message = (
            "🤖 *AI Signal Summary*\n\n"
            "🟡 *BTCUSDT*\n"
            f"Price: ${btc_price:,.2f}\n"
            f"Trend Bias: {btc_trend}\n"
            f"Momentum: {btc_momentum}\n"
            f"Signal: *{btc_signal}*\n"
            f"Confidence: {btc_conf}%\n\n"
            "🔵 *ETHUSDT*\n"
            f"Price: ${eth_price:,.2f}\n"
            f"Trend Bias: {eth_trend}\n"
            f"Momentum: {eth_momentum}\n"
            f"Signal: *{eth_signal}*\n"
            f"Confidence: {eth_conf}%\n\n"
            "⚡ Powered by AIglobalTrading Engine\n"
            "⏰ Updates automatically"
        )

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode="Markdown"
        )

    except Exception as e:
        print("AI signal error:", e)


# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# Schedule AI signal (TEST MODE: every 30 seconds)
application.job_queue.run_repeating(
    send_live_update,
    interval=30,
    first=5
)

# Start Application
loop.run_until_complete(application.initialize())
loop.run_until_complete(application.start())


# ===== WEBHOOK ROUTE =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.run_until_complete(application.process_update(update))
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot running 🚀", 200
