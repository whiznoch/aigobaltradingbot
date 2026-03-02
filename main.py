import os
import asyncio
import random
import requests
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

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

# ===== ENV VARIABLES =====
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
        trend, signal = "Bullish", "BUY"
    elif price_change < -1.5:
        trend, signal = "Bearish", "SELL"
    else:
        trend, signal = "Sideways", "HOLD"

    if abs(price_change) > 3:
        momentum, confidence = "Strong", random.randint(75, 90)
    elif abs(price_change) > 1:
        momentum, confidence = "Moderate", random.randint(60, 75)
    else:
        momentum, confidence = "Weak", random.randint(50, 60)

    return trend, momentum, signal, confidence

# ===== COINS & ALERT SETTINGS =====
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
ALERT_THRESHOLD = 2.0   # percent change to trigger alert
last_alerts = {}        # store last alerted price per coin

# ===== FETCH PRICE =====
def fetch_price(pair):
    resp = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}")
    data = resp.json()
    return float(data["lastPrice"]), float(data["priceChangePercent"])

# ===== SEND MARKET UPDATES =====
async def send_live_update(context: ContextTypes.DEFAULT_TYPE = None):
    messages = []

    for pair in PAIRS:
        try:
            price, change = fetch_price(pair)
            trend, momentum, signal, confidence = generate_signal(change)

            # Only alert if price change exceeds threshold and price is new
            if abs(change) >= ALERT_THRESHOLD and last_alerts.get(pair) != round(price, 2):
                last_alerts[pair] = round(price, 2)
                emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                messages.append(
                    f"{emoji} *{pair}*\n"
                    f"Price: ${price:,.2f}\n"
                    f"Trend: {trend}\n"
                    f"Momentum: {momentum}\n"
                    f"Signal: *{signal}*\n"
                    f"Confidence: {confidence}%"
                )
        except Exception as e:
            print(f"Error fetching {pair}: {e}")

    if messages:
        text = "⚡ *Crypto Market Alerts*\n\n" + "\n\n".join(messages)
        try:
            await application.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            print("Error sending alert:", e)

# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# ===== JOB QUEUE =====
# Runs every 15 minutes; first run after 10 seconds
application.job_queue.run_repeating(send_live_update, interval=900, first=10)

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
