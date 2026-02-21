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

from router_text import text_router
from router_callback import qa_callback_router
from keyboards import main_menu

TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)

# Create one global event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Build Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " **Welcome to AIglobaltradingbot – First Leveraged DEX on TON!** ⚡️\n\n" 
        "*Earn seasonal Reward Points (RP) by trading, depositing, or learning—" 
        "then convert them into* $AIglobaltrading *tokens!*\n\n" 
        "📈 Trade crypto, forex, and commodities with **up to x150 leverage** " 
        "directly from your wallet.\n\n" "💰 Deposit your USDT, TON, and NOT into AIglobaltrading Vaults and earn " 
        "**up to 14.81% APR** with no lock-ups.\n\n" 
        "🧠 Learn DeFi and trading and earn with **AIglobaltrading Academy**.\n\n" 
        "🫂 Invite your friends to AIglobaltrading Trade to get part of their trading fees " 
        "and **earn extra RP**.\n\n" 
        "🎮 Complete tasks & unlock achievements to grab even more rewards with fun!\n\n" 
        "🏆 Join trading tournaments and win real rewards.",
        reply_markup=main_menu()
    )

# ===== REGISTER HANDLERS =====
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
application.add_handler(CallbackQueryHandler(qa_callback_router))

# 🔥 ONLY INITIALIZE (DO NOT start())
loop.run_until_complete(application.initialize())

# ===== WEBHOOK ROUTE =====
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.run_until_complete(application.process_update(update))
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot running 🚀", 200
