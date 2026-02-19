from telegram import Update
from telegram.ext import ContextTypes
from keyboards import qa_buttons

async def qa_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "qa_how":
        text = (
            "📊 *How It Works*\n\n"
            "AIglobaltrading combines trading automation, copy trading, "
            "and AI-powered strategies.\n\n"
            "1️⃣ Deposit funds\n"
            "2️⃣ Select strategy\n"
            "3️⃣ Earn from market activity\n\n"
            "Simple. Transparent. Automated."
        )

    elif data == "qa_updates":
        text = (
            "🔔 *Updates & Signals*\n\n"
            "We provide real-time trading signals and system updates.\n"
            "Signals are powered by AI analysis and expert traders.\n\n"
            "Always verify news from official channels."
        )

    elif data == "qa_rewards":
        text = (
            "💰 *Earnings & Rewards*\n\n"
            "Users earn through:\n"
            "• Trading profits\n"
            "• Referral commissions\n"
            "• Reward distributions\n\n"
            "Earnings depend on market performance and activity level."
        )

    elif data == "qa_support":
        text = (
            "🛠 *Support*\n\n"
            "Need help?\n"
            "Use the Support button in the main menu to open a ticket.\n\n"
            "Never share your private keys or passwords."
        )

    elif data == "qa_news":
        text = (
            "📰 *Official News*\n\n"
            "Only trust announcements from:\n"
            "• The official bot\n"
            "• The official Telegram channel\n\n"
            "Avoid fake accounts and impersonators."
        )

    elif data == "qa_live":
        text = (
            "📢 *Live Updates*\n\n"
            "Live trading activity, announcements, "
            "and platform updates are shared in real-time.\n\n"
            "Stay connected."
        )

    else:
        text = "Invalid selection."

    await query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=qa_buttons()
    )
