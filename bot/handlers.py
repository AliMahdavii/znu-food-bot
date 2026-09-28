from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

from bot.keyboards import main_menu, settings_menu
from database.db import (
    save_user,
    get_user,
    update_user_setting,
)


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

    # =========================
    # Main Menu
    # =========================

    @bot.message_handler(
        func=lambda message: message.text == "🍽 رزروهای من"
    )
    def my_reservations(message):

        bot.send_message(
            message.chat.id,
            "🍽 <b>رزروهای من</b>\n\n"
            "هنوز رزروی ثبت نشده است.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    @bot.message_handler(
        func=lambda message: message.text == "⚙️ تنظیمات"
    )
    def settings(message):

        bot.send_message(
            message.chat.id,
            "⚙️ <b>تنظیمات رزرو</b>\n\n"
            "تنظیمات موردنظر خودت رو انتخاب کن:",
            parse_mode="HTML",
            reply_markup=settings_menu()
        )

    @bot.message_handler(
        func=lambda message: message.text == "👤 حساب کاربری"
    )
    def account(message):

        telegram_id = message.from_user.id
        user = get_user(telegram_id)

        if not user:
            bot.send_message(
                message.chat.id,
                "❌ حسابی برای شما ثبت نشده است."
            )
            return

        (
            _,
            username,
            _,
            auto_reservation,
            reservation_days,
            meal,
            selection_mode
        ) = user

        status = "فعال ✅" if auto_reservation else "غیرفعال ❌"

        bot.send_message(
            message.chat.id,
            "👤 <b>حساب کاربری</b>\n\n"
            f"🔐 نام کاربری: <code>{username}</code>\n"
            f"🤖 رزرو خودکار: {status}\n"
            f"📅 روزها: {reservation_days}\n"
            f"🍽 وعده: {meal}\n"
            f"🔎 انتخاب: {selection_mode}",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    @bot.message_handler(
        func=lambda message: message.text == "🤖 رزرو خودکار"
    )
    def auto_reservation(message):

        telegram_id = message.from_user.id
        user = get_user(telegram_id)

        if not user:
            bot.send_message(
                message.chat.id,
                "❌ ابتدا حساب کاربری خودت رو ثبت کن."
            )
            return

        auto_reservation_status = user[3]

        if auto_reservation_status:
            text = (
                "🤖 <b>رزرو خودکار</b>\n\n"
                "وضعیت فعلی:\n"
                "✅ فعال"
            )
        else:
            text = (
                "🤖 <b>رزرو خودکار</b>\n\n"
                "وضعیت فعلی:\n"
                "❌ غیرفعال"
            )

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # =========================
    # Settings
    # =========================

    @bot.message_handler(
        func=lambda message: message.text == "🍽 وعده غذایی"
    )
    def meal_settings(message):

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        keyboard.row("🍽 ناهار")
        keyboard.row("🔙 بازگشت")

        bot.send_message(
            message.chat.id,
            "🍽 <b>وعده غذایی</b>\n\n"
            "وعده موردنظر را انتخاب کن:",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    @bot.message_handler(
        func=lambda message: message.text == "🍽 ناهار"
    )
    def set_lunch(message):

        telegram_id = message.from_user.id

        update_user_setting(
            telegram_id,
            "meal",
            "ناهار"
        )

        bot.send_message(
            message.chat.id,
            "✅ وعده غذایی روی <b>ناهار</b> تنظیم شد.",
            parse_mode="HTML",
            reply_markup=settings_menu()
        )

    @bot.message_handler(
        func=lambda message: message.text == "🔎 نوع انتخاب غذا"
    )
    def selection_settings(message):

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        keyboard.row(
            "🥇 اولین غذای موجود"
        )

        keyboard.row(
            "🔙 بازگشت"
        )

        bot.send_message(
            message.chat.id,
            "🔎 <b>نوع انتخاب غذا</b>\n\n"
            "روش انتخاب غذا را مشخص کن:",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    @bot.message_handler(
        func=lambda message: message.text == "🥇 اولین غذای موجود"
    )
    def set_first_available(message):

        telegram_id = message.from_user.id

        update_user_setting(
            telegram_id,
            "selection_mode",
            "اولین غذای موجود"
        )

        bot.send_message(
            message.chat.id,
            "✅ روش انتخاب روی "
            "<b>اولین غذای موجود</b> تنظیم شد.",
            parse_mode="HTML",
            reply_markup=settings_menu()
        )

    @bot.message_handler(
        func=lambda message: message.text == "🔙 بازگشت"
    )
    def back_to_settings(message):

        bot.send_message(
            message.chat.id,
            "⚙️ <b>تنظیمات رزرو</b>\n\n"
            "تنظیمات موردنظر خودت رو انتخاب کن:",
            parse_mode="HTML",
            reply_markup=settings_menu()
        )
