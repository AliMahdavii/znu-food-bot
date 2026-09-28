from telebot import TeleBot

from bot.keyboards import main_menu
from database.db import save_user, get_user


user_states = {}
user_data = {}


def register_handlers(bot: TeleBot):

    @bot.message_handler(commands=["start"])
    def start(message):

        telegram_id = message.from_user.id

        user = get_user(telegram_id)

        if user:
            bot.send_message(
                message.chat.id,
                "👋 دوباره خوش اومدی!\n\n"
                "حساب شما قبلاً ثبت شده.",
                reply_markup=main_menu()
            )
            return

        user_states[telegram_id] = "username"

        bot.send_message(
            message.chat.id,
            "🍽 <b>ربات رزرو غذای دانشگاه</b>\n\n"
            "سلام 👋\n"
            "برای شروع، نام کاربری سامانه غذای دانشگاهت رو بفرست.\n\n"
            "🔐 <b>Username:</b>",
            parse_mode="HTML"
        )


    @bot.message_handler(
        func=lambda message:
        user_states.get(message.from_user.id) == "username"
    )
    def receive_username(message):

        telegram_id = message.from_user.id

        user_data[telegram_id] = {
            "username": message.text
        }

        user_states[telegram_id] = "password"

        bot.send_message(
            message.chat.id,
            "🔑 حالا رمز عبور سامانه رو بفرست."
        )


    @bot.message_handler(
        func=lambda message:
        user_states.get(message.from_user.id) == "password"
    )
    def receive_password(message):

        telegram_id = message.from_user.id

        username = user_data[telegram_id]["username"]
        password = message.text

        save_user(
            telegram_id,
            username,
            password
        )

        user_states.pop(telegram_id, None)
        user_data.pop(telegram_id, None)

        bot.send_message(
            message.chat.id,
            "✅ <b>حساب با موفقیت ثبت شد.</b>\n\n"
            "از این به بعد می‌تونی تنظیمات رزرو خودکار "
            "غذا رو مدیریت کنی.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )