import os
import random
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

# ===== ENV VARIABLES =====
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Example: -1003631149457
RENDER_DOMAIN = os.getenv("RENDER_DOMAIN")  # Example: aigobaltradingbot-15.onrender.com

# ===== FLASK APP =====
flask_app = Flask(__name__)

# ===== TELEGRAM BOT =====
application = ApplicationBuilder().token(TOKEN).build()

# ===== COINS & ALERT SETTINGS =====
PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
ALERT_THRESHOLD = 2.0  # percent change to trigger alert
last_alerts = {}  # store last alerted price per coin

# ===== HELPER FUNCTIONS =====
def generate_signal(price_change):
    """Simple AI signal logic"""
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

def fetch_price(pair):
    """Fetch latest price & 24h change from Binance"""
    resp = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}")
    data = resp.json()
    return float(data["lastPrice"]), float(data["priceChangePercent"])

# ===== COMMANDS =====
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

# ===== PROFESSIONAL SIGNALS =====
async def send_live_update(context: ContextTypes.DEFAULT_TYPE = None):
    messages = []

    for pair in PAIRS:
        try:
            price, change = fetch_price(pair)
            trend, momentum, signal, confidence = generate_signal(change)

            # Only alert if price change exceeds threshold & price is new
            if abs(change) >= ALERT_THRESHOLD and last_alerts.get(pair) != round(price, 2):
                last_alerts[pair] = round(price, 2)

                emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                messages.append(
                    f"{emoji} *{pair} Signal*\n"
                    f"💰 *Price:* ${price:,.2f}\n"
                    f"📊 *Trend:* {trend}\n"
                    f"⚡ *Momentum:* {momentum}\n"
                    f"📈 *Action:* *{signal}*\n"
                    f"🎯 *Confidence:* {confidence}%\n"
                    f"⏰ Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                )
        except Exception as e:
            print(f"Error fetching {pair}: {e}")

    if messages:
        text = "🔥 *Crypto Market Signals*\n\n" + "\n\n".join(messages) + "\n\n⚡ Powered by AIglobalTrading Engine"
        try:
            await application.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            print("Error sending alert:", e)

# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# ===== JOB QUEUE =====
# Immediate update
import asyncio
asyncio.get_event_loop().create_task(send_live_update())
# Repeating every 15 minutes
application.job_queue.run_repeating(send_live_update, interval=900, first=900)

# ===== START BOT WITH WEBHOOK =====
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=f"https://{RENDER_DOMAIN}/{TOKEN}",
    )

# ===== FLASK ROUTES =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    import asyncio
    asyncio.get_event_loop().create_task(application.process_update(update))
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot running 🚀", 200
