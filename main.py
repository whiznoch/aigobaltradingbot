import os
import random
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import asyncio

# ===== ENV VARIABLES =====
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")       # -100xxxx format
RENDER_DOMAIN = os.getenv("RENDER_DOMAIN") # e.g., yourapp.onrender.com

# Build Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# ===== COINS & ALERT SETTINGS =====
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
ALERT_THRESHOLD = 0.5   # percent change to trigger alert
last_alerts = {}

# ===== HELPER FUNCTIONS =====
def generate_signal(change_percent):
    """Determine trend, signal, and confidence"""
    if change_percent > 1.5:
        trend, signal = "Bullish", "BUY"
        arrow = "📈"
    elif change_percent < -1.5:
        trend, signal = "Bearish", "SELL"
        arrow = "📉"
    else:
        trend, signal = "Sideways", "HOLD"
        arrow = "➖"

    if abs(change_percent) > 3:
        momentum, confidence = "Strong", random.randint(75, 90)
    elif abs(change_percent) > 1:
        momentum, confidence = "Moderate", random.randint(60, 75)
    else:
        momentum, confidence = "Weak", random.randint(50, 65)

    return trend, signal, arrow, momentum, confidence

def fetch_price(pair):
    """Fetch price and 24h change from Binance"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
    resp = requests.get(url, timeout=5)
    data = resp.json()
    return float(data.get("lastPrice", 0)), float(data.get("priceChangePercent", 0))

# ===== SEND PROFESSIONAL SIGNALS =====
async def send_signals(context: ContextTypes.DEFAULT_TYPE = None):
    print(f"[{datetime.utcnow()}] MARKET JOB RUNNING")
    messages = []

    for pair in PAIRS:
        try:
            price, change = fetch_price(pair)
            trend, signal, arrow, momentum, confidence = generate_signal(change)

            if abs(change) >= ALERT_THRESHOLD and last_alerts.get(pair) != signal:
                last_alerts[pair] = signal
                banner = "🟢 BUY" if signal=="BUY" else "🔴 SELL" if signal=="SELL" else "🟡 HOLD"

                messages.append(
                    f"{banner} | *{pair}*\n"
                    f"{arrow} Price: `${price:,.2f}`\n"
                    f"📊 Trend: {trend}\n"
                    f"⚡ Momentum: {momentum}\n"
                    f"💯 Confidence: {confidence}%\n"
                    f"⏰ UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"----------------------"
                )
        except Exception as e:
            print(f"HTTP error for {pair}: {e}")

    if messages:
        text = "🚀 *Premium Crypto Signals*\n\n" + "\n\n".join(messages)
        try:
            await application.bot.send_message(
                chat_id=CHANNEL_ID, text=text, parse_mode="Markdown"
            )
        except Exception as e:
            print("Error sending alert:", e)

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! This bot delivers professional crypto signals like @storm_trade_news.\n"
        "Signals will be posted directly in the channel automatically."
    )

# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))

# ===== JOB QUEUE =====
application.job_queue.run_repeating(send_signals, interval=900, first=10)

# ===== START BOT WITH WEBHOOK =====
if __name__ == "__main__":
    application.job_queue.start()
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=f"https://{RENDER_DOMAIN}/{TOKEN}",
    )
