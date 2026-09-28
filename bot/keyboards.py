from telebot.types import ReplyKeyboardMarkup


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
