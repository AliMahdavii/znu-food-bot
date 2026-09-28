import telebot

from config.settings import TELEGRAM_BOT_TOKEN
from database.db import init_db
from bot.handlers import register_handlers


def main():

    init_db()

    bot = telebot.TeleBot(
        TELEGRAM_BOT_TOKEN
    )

    register_handlers(bot)

    print("🤖 ZNU Food Bot is running...")

    bot.infinity_polling()


if __name__ == "__main__":
    main()
