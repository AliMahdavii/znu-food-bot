from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

from bot.keyboards import (
    main_menu,
    settings_menu,
    reservation_days_keyboard,
    auto_reservation_keyboard,
)
from database.db import (
    save_user,
    get_user,
    update_user_setting,
)


user_states = {}
user_data = {}
selected_days = {}


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
                "❌ ابتدا حساب کاربری خودت رو ثبت کن.",
                reply_markup=main_menu()
            )
            return

        enabled = bool(user[3])

        status = (
            "✅ فعال"
            if enabled
            else "❌ غیرفعال"
        )

        bot.send_message(
            message.chat.id,
            "🤖 <b>رزرو خودکار</b>\n\n"
            f"وضعیت فعلی: {status}\n\n"
            "در صورت فعال بودن، ربات طبق تنظیمات شما "
            "فرآیند رزرو هفتگی را انجام می‌دهد.",
            parse_mode="HTML",
            reply_markup=auto_reservation_keyboard(enabled)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "auto:enable"
    )
    def enable_auto_reservation(call):

        telegram_id = call.from_user.id

        update_user_setting(
            telegram_id,
            "auto_reservation",
            1
        )

        bot.answer_callback_query(
            call.id,
            "رزرو خودکار فعال شد ✅"
        )

        bot.edit_message_text(
            "🤖 <b>رزرو خودکار</b>\n\n"
            "وضعیت فعلی: ✅ فعال\n\n"
            "ربات طبق تنظیمات شما فرآیند رزرو هفتگی "
            "را انجام خواهد داد.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=auto_reservation_keyboard(True)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "auto:disable"
    )
    def disable_auto_reservation(call):

        telegram_id = call.from_user.id

        update_user_setting(
            telegram_id,
            "auto_reservation",
            0
        )

        bot.answer_callback_query(
            call.id,
            "رزرو خودکار غیرفعال شد ❌"
        )

        bot.edit_message_text(
            "🤖 <b>رزرو خودکار</b>\n\n"
            "وضعیت فعلی: ❌ غیرفعال\n\n"
            "رزرو خودکار برای حساب شما متوقف شده است.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=auto_reservation_keyboard(False)
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "auto:back"
    )
    def auto_reservation_back(call):

        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            "⚙️ <b>تنظیمات رزرو</b>\n\n"
            "تنظیمات موردنظر خودت رو انتخاب کن:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )

        bot.send_message(
            call.message.chat.id,
            "⚙️ تنظیمات رزرو",
            reply_markup=settings_menu()
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

    @bot.message_handler(
        func=lambda message: message.text == "📅 روزهای رزرو"
    )
    def reservation_days(message):

        telegram_id = message.from_user.id
        user = get_user(telegram_id)

        if not user:
            bot.send_message(
                message.chat.id,
                "❌ ابتدا حساب کاربری خودت رو ثبت کن.",
                reply_markup=main_menu()
            )
            return

        saved_days = user[4]

        if saved_days:
            days = [
                day.strip()
                for day in saved_days.split(",")
                if day.strip()
            ]
        else:
            days = []

        selected_days[telegram_id] = set(days)

        bot.send_message(
            message.chat.id,
            "📅 <b>روزهای رزرو</b>\n\n"
            "روزهایی که می‌خواهی ربات برایت غذا رزرو کند "
            "را انتخاب کن:",
            parse_mode="HTML",
            reply_markup=reservation_days_keyboard(
                selected_days[telegram_id]
            )
        )

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("day:")
    )
    def toggle_reservation_day(call):

        telegram_id = call.from_user.id

        if telegram_id not in selected_days:
            selected_days[telegram_id] = set()

        day_codes = {
            "sat": "شنبه",
            "sun": "یکشنبه",
            "mon": "دوشنبه",
            "tue": "سه‌شنبه",
            "wed": "چهارشنبه",
        }

        day_code = call.data.split(":", 1)[1]
        day_name = day_codes.get(day_code)

        if not day_name:
            return

        if day_name in selected_days[telegram_id]:
            selected_days[telegram_id].remove(day_name)
        else:
            selected_days[telegram_id].add(day_name)

        bot.answer_callback_query(call.id)

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=reservation_days_keyboard(
                selected_days[telegram_id]
            )
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "days:save"
    )
    def save_reservation_days(call):

        telegram_id = call.from_user.id

        days = selected_days.get(
            telegram_id,
            set()
        )

        ordered_days = [
            "شنبه",
            "یکشنبه",
            "دوشنبه",
            "سه‌شنبه",
            "چهارشنبه",
        ]

        selected = [
            day
            for day in ordered_days
            if day in days
        ]

        if not selected:

            bot.answer_callback_query(
                call.id,
                "حداقل یک روز را انتخاب کن.",
                show_alert=True
            )

            return

        value = ",".join(selected)

        update_user_setting(
            telegram_id,
            "reservation_days",
            value
        )

        selected_days.pop(
            telegram_id,
            None
        )

        bot.answer_callback_query(
            call.id,
            "تنظیمات ذخیره شد ✅"
        )

        bot.edit_message_text(
            "✅ <b>روزهای رزرو ذخیره شدند.</b>\n\n"
            f"📅 {value}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )

        bot.send_message(
            call.message.chat.id,
            "⚙️ تنظیمات رزرو",
            reply_markup=settings_menu()
        )

    @bot.callback_query_handler(
        func=lambda call: call.data == "days:back"
    )
    def reservation_days_back(call):

        selected_days.pop(
            call.from_user.id,
            None
        )

        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            "⚙️ <b>تنظیمات رزرو</b>\n\n"
            "تنظیمات موردنظر خودت رو انتخاب کن:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )

        bot.send_message(
            call.message.chat.id,
            "⚙️ تنظیمات رزرو",
            reply_markup=settings_menu()
        )
