from telebot import TeleBot

from bot.keyboards import main_menu, settings_menu
from bot.reservation import ReservationResult
from bot.service import reserve_next_week


def format_reservation_result(
    results: list[ReservationResult],
) -> str:
    """Format weekly reservation results for Telegram."""

    lines = [
        "🍽 <b>نتیجه رزرو غذا</b>",
        "",
    ]

    for result in results:
        status = "✅" if result.success else "❌"

        lines.append(
            f"{status} <b>{result.day}</b>"
        )
        lines.append(
            f"🍴 {result.food or 'غذا پیدا نشد'}"
        )
        lines.append(
            f"💬 {result.message}"
        )
        lines.append("")

    successful = sum(
        result.success
        for result in results
    )

    failed = len(results) - successful

    lines.extend(
        [
            "──────────────",
            f"✅ موفق: {successful}",
            f"❌ ناموفق: {failed}",
        ]
    )

    return "\n".join(lines)


def run_reservation(
    bot: TeleBot,
    chat_id: int,
):
    """Run the reservation service and send the result to Telegram."""

    bot.send_message(
        chat_id,
        "⏳ در حال ورود به سامانه و رزرو غذا...\n"
        "لطفاً صبر کن.",
    )

    try:
        results = reserve_next_week(
            headless=True,
        )

        print("RESERVATION SERVICE FINISHED")

        result_text = format_reservation_result(
            results
        )

        bot.send_message(
            chat_id,
            result_text,
            parse_mode="HTML",
        )

    except Exception as exc:
        print(f"Reservation error: {exc}")

        bot.send_message(
            chat_id,
            f"❌ خطا در رزرو:\n{exc}",
        )


def register_handlers(bot: TeleBot):

    @bot.message_handler(commands=["start"])
    def start(message):
        text = (
            "🍽 <b>ربات رزرو غذای دانشگاه</b>\n\n"
            "به ربات رزرو خودکار غذا خوش اومدی.\n\n"
            "برای شروع، از منوی زیر استفاده کن."
        )

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=main_menu(),
        )

    @bot.message_handler(commands=["reserve"])
    def reserve(message):
        print("RESERVE COMMAND RECEIVED")

        run_reservation(
            bot=bot,
            chat_id=message.chat.id,
        )

    @bot.message_handler(
        func=lambda message: message.text == "🤖 رزرو خودکار"
    )
    def auto_reservation(message):
        print("AUTO RESERVATION BUTTON PRESSED")

        run_reservation(
            bot=bot,
            chat_id=message.chat.id,
        )

    @bot.message_handler(
        func=lambda message: message.text == "⚙️ تنظیمات"
    )
    def settings(message):
        bot.send_message(
            message.chat.id,
            "⚙️ <b>تنظیمات</b>\n\n"
            "یکی از گزینه‌های زیر را انتخاب کن:",
            parse_mode="HTML",
            reply_markup=settings_menu(),
        )

    @bot.message_handler(
        func=lambda message: message.text == "🔙 بازگشت"
    )
    def back_to_main_menu(message):
        bot.send_message(
            message.chat.id,
            "🏠 برگشتیم به منوی اصلی.",
            reply_markup=main_menu(),
        )

    @bot.message_handler(
        func=lambda message: message.text == "🍽 رزروهای من"
    )
    def my_reservations(message):
        bot.send_message(
            message.chat.id,
            "🍽 هنوز بخش نمایش رزروها پیاده‌سازی نشده."
        )

    @bot.message_handler(
        func=lambda message: message.text == "👤 حساب کاربری"
    )
    def account(message):
        bot.send_message(
            message.chat.id,
            "👤 بخش حساب کاربری به‌زودی تکمیل می‌شود."
        )
