from telebot import TeleBot

from bot.keyboards import main_menu
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
        bot.send_message(
            message.chat.id,
            "⏳ در حال ورود به سامانه و رزرو غذا...\n"
            "لطفاً صبر کن.",
        )

        try:
            results = reserve_next_week(
                headless=True,
            )

            result_text = format_reservation_result(
                results
            )

            bot.send_message(
                message.chat.id,
                result_text,
                parse_mode="HTML",
            )

        except Exception as exc:
            print(f"Reservation error: {exc}")

            bot.send_message(
                message.chat.id,
                "❌ هنگام رزرو غذا یک خطای غیرمنتظره رخ داد.",
            )
