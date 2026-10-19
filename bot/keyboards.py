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


def auto_reservation_keyboard(enabled):
    keyboard = InlineKeyboardMarkup()

    if enabled:
        keyboard.add(
            InlineKeyboardButton(
                "❌ غیرفعال کردن",
                callback_data="auto:disable"
            )
        )
    else:
        keyboard.add(
            InlineKeyboardButton(
                "✅ فعال کردن",
                callback_data="auto:enable"
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="auto:back"
        )
    )

    return keyboard


def account_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row("🔐 ثبت یا تغییر حساب دانشگاه")
    keyboard.row("🔙 بازگشت")

    return keyboard


def meal_keyboard(selected_meal):
    keyboard = InlineKeyboardMarkup()

    meals = [
        ("صبحانه", "صبحانه"),
        ("ناهار", "ناهار"),
        ("شام", "شام"),
    ]

    for name, value in meals:
        prefix = "✅" if value == selected_meal else "🍽"

        keyboard.add(
            InlineKeyboardButton(
                f"{prefix} {name}",
                callback_data=f"meal:{value}",
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="meal:back",
        )
    )

    return keyboard


def selection_mode_keyboard(selected_mode):
    keyboard = InlineKeyboardMarkup()

    modes = [
        "اولین غذای موجود",
        "ارزان‌ترین غذا",
    ]

    for mode in modes:
        prefix = "✅" if mode == selected_mode else "🔎"

        keyboard.add(
            InlineKeyboardButton(
                f"{prefix} {mode}",
                callback_data=f"mode:{mode}",
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            "🔙 بازگشت",
            callback_data="mode:back",
        )
    )

    return keyboard
