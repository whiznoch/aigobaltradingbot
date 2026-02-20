import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from router_callback import qa_callback_router
from router_text import text_router
from keyboards import main_menu
from config import BOT_TOKEN
from database import conn, cur

flask_app = Flask(__name__)

# Telegram application
application = Application.builder().token(BOT_TOKEN).build()

# --- Handlers ---
async def start(update, context):
    user = update.effective_user
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user.id, user.username)
    )
    conn.commit()

    welcome_text = (
        "**Welcome to AIglobaltradingbot – First Leveraged DEX on TON!** ⚡️\n\n"
        "*Earn seasonal Reward Points (RP) by trading, depositing, or learning—"
        "then convert them into* $AIglobaltrading *tokens!*\n\n"
        "📈 Trade crypto, forex, and commodities with **up to x150 leverage** "
        "directly from your wallet.\n\n"
        "💰 Deposit your USDT, TON, and NOT into AIglobaltrading Vaults and earn "
        "**up to 14.81% APR** with no lock-ups.\n\n"
        "🧠 Learn DeFi and trading and earn with **AIglobaltrading Academy**.\n\n"
        "🫂 Invite your friends to AIglobaltrading Trade to get part of their trading fees "
        "and **earn extra RP**.\n\n"
        "🎮 Complete tasks & unlock achievements to grab even more rewards with fun!\n\n"
        "🏆 Join trading tournaments and win real rewards."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# Add handlers to the bot
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# --- Webhook route ---
@flask_app.route("/", methods=["POST"])
def webhook():
    """Receive updates from Telegram."""
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # Run async process_update in a new event loop
    asyncio.run(application.process_update(update))
    return "ok", 200

# Optional: simple GET route to check the server
@flask_app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
