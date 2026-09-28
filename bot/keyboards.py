from telebot.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu():
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🍽 رزروهای من",
        "⚙️ تنظیمات"
    )

    keyboard.row(
        "👤 حساب کاربری",
        "🤖 رزرو خودکار"
    )

    return keyboard


def settings_menu():
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "📅 روزهای رزرو",
        "🍽 وعده غذایی"
    )

    keyboard.row(
        "🔎 نوع انتخاب غذا",
        "🔙 بازگشت"
    )

    return keyboard


def reservation_days_keyboard(selected_days):
    keyboard = InlineKeyboardMarkup()

    days = [
        ("شنبه", "sat"),
        ("یکشنبه", "sun"),
        ("دوشنبه", "mon"),
        ("سه‌شنبه", "tue"),
        ("چهارشنبه", "wed"),
    ]

    for day_name, day_code in days:

        if day_name in selected_days:
            text = f"✅ {day_name}"
        else:
            text = f"❌ {day_name}"

        keyboard.add(
            InlineKeyboardButton(
                text,
                callback_data=f"day:{day_code}"
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            "💾 ذخیره",
            callback_data="days:save"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="days:back"
        )
    )

    return keyboard
