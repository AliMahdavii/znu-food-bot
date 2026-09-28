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