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

from config import BOT_TOKEN
from database import conn, cur
from keyboards import main_menu
from router_text import text_router
from router_callback import qa_callback_router

# Create Flask app
flask_app = Flask(__name__)

# Build Telegram application
application = Application.builder().token(BOT_TOKEN).build()


# ---------------- START COMMAND ---------------- #

async def start(update: Update, context):
    user = update.effective_user

    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user.id, user.username),
    )
    conn.commit()

    welcome_text = (
        "**Welcome to AIglobaltradingbot – First Leveraged DEX on TON!** ⚡️\n\n"
        "*Earn seasonal Reward Points (RP) by trading, depositing, or learning—"
        "then convert them into* $AIglobaltrading *tokens!*\n\n"
        "📈 Trade crypto, forex, and commodities with **up to x150 leverage** directly from your wallet.\n\n"
        "💰 Deposit your USDT, TON, and NOT into Vaults and earn **up to 14.81% APR** with no lock-ups.\n\n"
        "🧠 Learn DeFi and trading.\n\n"
        "🏆 Join trading tournaments and win rewards."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


# ---------------- ADD HANDLERS ---------------- #

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))


# ---------------- START TELEGRAM APP ON BOOT ---------------- #



# ---------------- WEBHOOK ROUTE ---------------- #

@flask_app.route("/", methods=["POST"])
async def webhook():
    if not application.running:
        await application.initialize()
        await application.start()

    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)

    return "ok"
