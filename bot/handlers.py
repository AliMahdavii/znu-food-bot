from telebot import TeleBot

from bot.browser import ZNUBrowser
from bot.keyboards import main_menu
from bot.reservation import ReservationResult, reserve_week


def format_reservation_result(
    results: list[ReservationResult],
) -> str:
    """Format weekly reservation results for Telegram."""

    lines = [
        "🍽 <b>نتیجه رزرو غذا</b>",
        "",
    ]

    for result in results:
        if result.success:
            status = "✅"
        else:
            status = "❌"

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

        browser = ZNUBrowser(headless=True)

        try:
            page = browser.start()

            if not browser.login():
                bot.send_message(
                    message.chat.id,
                    "❌ ورود به سامانه ناموفق بود.",
                )
                return

            browser.open_reservation_page()

            browser.go_to_next_week()

            bot.send_message(
                message.chat.id,
                "🔄 هفته بعد انتخاب شد.\n"
                "🍽 در حال بررسی و رزرو غذاها...",
            )

            results = reserve_week(page)

            result_text = format_reservation_result(results)

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

        finally:
            browser.close()
