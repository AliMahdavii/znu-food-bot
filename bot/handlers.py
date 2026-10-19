from telebot import TeleBot

from bot.keyboards import main_menu, settings_menu, account_menu
from bot.reservation import ReservationResult
from bot.service import reserve_next_week
from database.db import get_user, save_user
from html import escape


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
    telegram_id: int,
):
    """Run reservation using the requesting user's account."""

    try:
        user = get_user(telegram_id)
    except Exception:
        print("Failed to load university account for reservation.")

        bot.send_message(
            chat_id,
            "❌ دریافت اطلاعات حساب ناموفق بود.\n"
            "لطفاً تنظیمات حساب و رمزنگاری را بررسی کن.",
        )
        return

    if user is None:
        bot.send_message(
            chat_id,
            "❌ هنوز حساب دانشگاهت ثبت نشده است.\n"
            "ابتدا باید حساب کاربری‌ات را در ربات ثبت کنی.",
        )
        return

    # Database fields:
    # 0: telegram_id
    # 1: username
    # 2: password
    username = user[1]
    password = user[2]

    bot.send_message(
        chat_id,
        "⏳ در حال ورود به سامانه و رزرو غذا...\n"
        "لطفاً صبر کن.",
    )

    try:
        results = reserve_next_week(
            username=username,
            password=password,
            headless=True,
        )

        result_text = format_reservation_result(results)

        bot.send_message(
            chat_id,
            result_text,
            parse_mode="HTML",
        )

    except Exception:
        # Avoid exposing credentials or internal error details.
        print("Reservation failed.")

        bot.send_message(
            chat_id,
            "❌ هنگام رزرو خطایی رخ داد. "
            "لطفاً بعداً دوباره تلاش کن.",
        )


def ask_university_username(bot, message):
    """Ask the user for their university username."""

    if message.text == "🔙 بازگشت":
        bot.send_message(
            message.chat.id,
            "🏠 برگشتیم به منوی اصلی.",
            reply_markup=main_menu(),
        )
        return

    username = (message.text or "").strip()

    if not username:
        msg = bot.send_message(
            message.chat.id,
            "❌ نام کاربری معتبر نیست. دوباره وارد کن:",
        )
        bot.register_next_step_handler(
            msg,
            ask_university_username,
            bot,
        )
        return

    msg = bot.send_message(
        message.chat.id,
        "🔑 حالا رمز عبور سامانه دانشگاه را ارسال کن.\n\n"
        "پس از دریافت رمز، ربات تلاش می‌کند پیام حاوی آن را حذف کند.",
    )

    bot.register_next_step_handler(
        msg,
        save_university_credentials,
        bot,
        username,
    )


def save_university_credentials(message, bot, username):
    """Encrypt and save the user's university credentials."""

    password = message.text or ""

    if password == "🔙 بازگشت":
        bot.send_message(
            message.chat.id,
            "🏠 عملیات ثبت حساب لغو شد.",
            reply_markup=main_menu(),
        )
        return

    # Try to remove the message containing the password.
    try:
        bot.delete_message(
            message.chat.id,
            message.message_id,
        )
    except Exception:
        # Message deletion may fail due to Telegram permissions or limits.
        pass

    if not password.strip():
        msg = bot.send_message(
            message.chat.id,
            "❌ رمز عبور خالی است. لطفاً رمز را دوباره ارسال کن:",
        )
        bot.register_next_step_handler(
            msg,
            save_university_credentials,
            bot,
            username,
        )
        return

    try:
        save_user(
            telegram_id=message.from_user.id,
            username=username,
            password=password,
        )

    except Exception:
        # Never log the username, password, or exception details.
        print("Failed to save university credentials.")

        bot.send_message(
            message.chat.id,
            "❌ ذخیره اطلاعات ناموفق بود.\n"
            "تنظیمات رمزنگاری را بررسی کن و دوباره تلاش کن.",
            reply_markup=account_menu(),
        )
        return

    bot.send_message(
        message.chat.id,
        "✅ حساب دانشگاه با موفقیت ذخیره شد.\n\n"
        "🔐 رمز عبور به‌صورت رمزنگاری‌شده در دیتابیس نگهداری می‌شود.",
        reply_markup=main_menu(),
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
            telegram_id=message.from_user.id,
        )

    @bot.message_handler(
        func=lambda message: message.text == "🤖 رزرو خودکار"
    )
    def auto_reservation(message):
        print("AUTO RESERVATION BUTTON PRESSED")

        run_reservation(
            bot=bot,
            chat_id=message.chat.id,
            telegram_id=message.from_user.id,
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
        try:
            user = get_user(message.from_user.id)
        except Exception:
            print("Failed to load university account.")

            bot.send_message(
                message.chat.id,
                "❌ دریافت اطلاعات حساب ناموفق بود.\n"
                "ممکن است تنظیمات رمزنگاری نیاز به بررسی داشته باشد.",
                reply_markup=account_menu(),
            )
            return

        if user is None:
            text = (
                "👤 <b>حساب کاربری</b>\n\n"
                "هنوز حساب دانشگاهت را ثبت نکرده‌ای."
            )
        else:
            username = escape(str(user[1]))

            text = (
                "👤 <b>حساب کاربری</b>\n\n"
                f"نام کاربری دانشگاه: <code>{username}</code>\n"
                "وضعیت: ✅ ثبت‌شده\n\n"
                "برای تغییر اطلاعات، گزینه زیر را انتخاب کن."
            )

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=account_menu(),
        )

    @bot.message_handler(
        func=lambda message: (
            message.text == "🔐 ثبت یا تغییر حساب دانشگاه"
        )
    )
    def register_account(message):
        msg = bot.send_message(
            message.chat.id,
            "🎓 نام کاربری سامانه دانشگاه را ارسال کن.\n\n"
            "برای لغو، گزینه «🔙 بازگشت» را بفرست.",
        )

        bot.register_next_step_handler(
            msg,
            ask_university_username,
            bot,
        )
