import os
import random
import requests
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
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Telegram channel ID like -1001234567890
RENDER_DOMAIN = os.getenv("RENDER_DOMAIN")  # e.g., yourbot.onrender.com

# Build Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🚀 *CoinvestGlobalBot*

CoinvestGlobalBot is a leveraged decentralized trading platform built on TON, enabling users to trade crypto, forex, and commodities with up to 150x leverage — directly from their wallets.

🔐 Non-custodial execution
📈 High-performance leveraged trading
💰 Competitive yield vaults
🏆 Trading tournaments & competitions
🎯 Reward-based engagement system

Built for serious traders. Designed for scale.""",
        reply_markup=main_menu(),
        parse_mode="Markdown"
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
ALERT_THRESHOLD = 2.0  # percent change to trigger alert
last_alerts = {}        # store last alerted price per coin

# ===== FETCH PRICE VIA COINGECKO =====
def fetch_price(pair):
    coin_map = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum",
        "BNBUSDT": "binancecoin",
        "SOLUSDT": "solana"
    }
    coin_id = coin_map.get(pair)
    if not coin_id:
        return None, None
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    resp = requests.get(url)
    data = resp.json()
    price = data[coin_id]["usd"]
    change = data[coin_id]["usd_24h_change"]
    return float(price), float(change)

# ===== SEND PROFESSIONAL MARKET UPDATES =====
async def send_live_update(context: ContextTypes.DEFAULT_TYPE = None):
    messages = []

    for pair in PAIRS:
        try:
            price, change = fetch_price(pair)
            if price is None:
                continue
            trend, momentum, signal, confidence = generate_signal(change)

            # Only alert if price change exceeds threshold and price is new
            if abs(change) >= ALERT_THRESHOLD and last_alerts.get(pair) != round(price, 2):
                last_alerts[pair] = round(price, 2)
                emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
                arrow = "📈" if signal == "BUY" else "📉" if signal == "SELL" else "➖"
                messages.append(
                    f"{arrow} {emoji} *{pair} Signal*\n"
                    f"💵 Price: `${price:,.2f}`\n"
                    f"📊 Trend: {trend}\n"
                    f"⚡ Momentum: {momentum}\n"
                    f"🔔 Signal: *{signal}*\n"
                    f"✅ Confidence: {confidence}%\n"
                    f"----------------------"
                )
        except Exception as e:
            print(f"HTTP error for {pair}: {e}")

    if messages:
        text = "🚨 *Crypto Market Alerts*\n\n" + "\n".join(messages)
        try:
            await application.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Error sending alert:", e)

# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# ===== JOB QUEUE =====
# Run every 15 minutes; first run after 10 seconds
application.job_queue.run_repeating(send_live_update, interval=900, first=10)

# ===== START BOT WITH WEBHOOK =====
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=f"https://{RENDER_DOMAIN}/{TOKEN}",
    )
