
from telegram import ReplyKeyboardMarkup

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["🌱 Earn", "📊 Trade"],
            ["📈 Portfolio", "❓ Q&A"],
            ["📰 Official News", "🙋‍ Support"],
        ],
        resize_keyboard=True
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def earn_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Start Earning", url="https://coinvestglobalfx.com/Clientarea/login")],
        [InlineKeyboardButton("📘 Learn More", url="https://t.me/+qO6R0I2fErtlNDAx")],
    ])

def trade_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Start Trading", url="https://coinvestglobalfx.com/Clientarea/login")],
    ])
def Support_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Open a ticket", url="https://t.me/+c66hHjj1qI81MWQx")],
    ])
def Portfolio_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("View Portfolio", url="https://coinvestglobalfx.com/Clientarea/login")],
    ])
def Official_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👉 Join the official community:", url="https://t.me/+c66hHjj1qI81MWQx")],
    ])
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def qa_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 How It Works", callback_data="qa_how"),
            InlineKeyboardButton("🔔 Updates & Signals", callback_data="qa_updates"),
        ],
        [
            InlineKeyboardButton("💰 Earnings & Rewards", callback_data="qa_rewards"),
            InlineKeyboardButton("🛠 Support", callback_data="qa_support"),
        ],
        [
            InlineKeyboardButton("📰 Official News", callback_data="qa_news"),
            InlineKeyboardButton("📢 Live Updates", callback_data="qa_live"),
        ],
    ])
