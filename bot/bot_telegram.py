import requests
import datetime
import time
import io
import pandas as pd
import threading
from telegram import __version__ as TG_VER
from pytz import timezone
import talib
import asyncio
import matplotlib.pyplot as plt

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Define key
TOKEN = "6872218219:AAHUq7K01nySykPhXii4X_V8J1N6faHFcBM"  # main bot


def get_symbol_data(symbol):
    try:
        url = ""
        data = requests.post(url, data={"symbol": symbol}).json()
        return data
    except Exception as e:
        print(e)
        return None


async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        symbol = context.args[0].upper()
        print(symbol)
        symbol_data = get_symbol_data(symbol)
        if symbol_data is None:
            await update.message.reply_text("Không tìm thấy thông tin")
            return
    except Exception as e:
        await update.message.reply_text("Đã có lỗi xảy ra, vui lòng thử lại sau")
        print(e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text(
        "Chào bạn đến với bot tra cứu thông tin chứng khoán. Tôi có thể giúp gì cho bạn?"
    )


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("i", get_info))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
