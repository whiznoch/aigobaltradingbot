from keyboards import earn_buttons, trade_buttons, Support_buttons, qa_buttons, Portfolio_buttons, Official_buttons

async def text_router(update, context):
    text = update.message.text

    if text == "🌱 Earn":
        await update.message.reply_text(
            "🌱 *Earn with AIglobaltrading*\n\n"
            "Earn Reward Points by trading, depositing, and learning. Provide your crypto and enjoy 14.96% of the protocol revenue 💎",
            parse_mode="Markdown",
            reply_markup=earn_buttons()
        )

    elif text == "📊 Trade":
        await update.message.reply_text(
            "📊 *Start Trading with AIglobaltrading*\n\n"
            "Trade crypto, forex, and commodities with leverage. Click below to get started 📈",
            parse_mode="Markdown",
            reply_markup=trade_buttons()
        )

    elif text == "📈 Portfolio":
        await update.message.reply_text(
            "📈 *Manage portfolio*\n\n"
            "Manage and review your trading portfolio 📈",
            parse_mode="Markdown",
            reply_markup=Portfolio_buttons()
        )

    elif text == "❓ Q&A":
        await update.message.reply_text(
            "❓ *AIglobaltrading Q&A*\n\n"
            "Choose a topic below:",
            parse_mode="Markdown",
            reply_markup=qa_buttons()
        )

    elif text == "📰 Official News":
        await update.message.reply_text(
            "📰 *AIGlobal Trading — Official News*\n\n"
            "This channel delivers verified announcements, feature releases, system updates, and important platform notices.",
            parse_mode="Markdown",
            reply_markup=Official_buttons()
        )

    elif text == "🙋‍ Support":
        await update.message.reply_text(
            "🙋 *AIglobaltrading Support bot*\n\n"
            "Need help? Open a ticket below 🤝",
            parse_mode="Markdown",
            reply_markup=Support_buttons()
        )

    else:
        await update.message.reply_text(
            "Please use the menu buttons below 👇"
        )
