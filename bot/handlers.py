from html import escape

from telebot import TeleBot

from bot.keyboards import (
    main_menu,
    settings_menu,
    account_menu,
    reservation_days_keyboard,
    meal_keyboard,
    selection_mode_keyboard,
)
from bot.reservation import ReservationResult
from bot.service import reserve_next_week
from database.db import (
    get_user,
    save_user,
    update_user_setting,
)


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

        lines.append(f"{status} <b>{escape(str(result.day))}</b>")
        lines.append(f"🍴 {escape(str(result.food or 'غذا پیدا نشد'))}")
        lines.append(f"💬 {escape(str(result.message))}")
        lines.append("")

    successful = sum(result.success for result in results)
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

    username = user[1]
    password = user[2]

    selection_mode = user[6] or "اولین غذای موجود"

    selected_days = [
        day.strip()
        for day in (user[4] or "").split(",")
        if day.strip()
    ]

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
            selected_days=selected_days,
            selection_mode=selection_mode,
        )

        bot.send_message(
            chat_id,
            format_reservation_result(results),
            parse_mode="HTML",
        )

    except Exception:
        print("Reservation failed.")
        bot.send_message(
            chat_id,
            "❌ هنگام رزرو خطایی رخ داد. "
            "لطفاً بعداً دوباره تلاش کن.",
        )


def ask_university_username(message, bot):
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

    try:
        bot.delete_message(
            message.chat.id,
            message.message_id,
        )
    except Exception:
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
        bot.send_message(
            message.chat.id,
            "🍽 <b>ربات رزرو غذای دانشگاه</b>\n\n"
            "به ربات رزرو خودکار غذا خوش اومدی.\n\n"
            "برای شروع، از منوی زیر استفاده کن.",
            parse_mode="HTML",
            reply_markup=main_menu(),
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
        func=lambda message: message.text == "📅 روزهای رزرو"
    )
    def reservation_days(message):
        try:
            user = get_user(message.from_user.id)

            if user is None:
                bot.send_message(
                    message.chat.id,
                    "❌ ابتدا حساب دانشگاهت را ثبت کن.",
                    reply_markup=main_menu(),
                )
                return

            selected_days = [
                day.strip()
                for day in (user[4] or "").split(",")
                if day.strip()
            ]

            bot.send_message(
                message.chat.id,
                "📅 <b>روزهای رزرو</b>\n\n"
                "روزهای موردنظرت را انتخاب کن و سپس ذخیره را بزن.",
                parse_mode="HTML",
                reply_markup=reservation_days_keyboard(selected_days),
            )

        except Exception:
            print("Failed to load reservation days.")
            bot.send_message(
                message.chat.id,
                "❌ دریافت تنظیمات ناموفق بود.",
            )

    @bot.message_handler(
        func=lambda message: message.text == "🍽 وعده غذایی"
    )
    def meal_settings(message):
        try:
            user = get_user(message.from_user.id)

            if user is None:
                bot.send_message(
                    message.chat.id,
                    "❌ ابتدا حساب دانشگاهت را ثبت کن.",
                    reply_markup=main_menu(),
                )
                return

            bot.send_message(
                message.chat.id,
                "🍽 وعده غذایی موردنظر را انتخاب کن:",
                reply_markup=meal_keyboard(user[5]),
            )

        except Exception:
            print("Failed to load meal settings.")
            bot.send_message(
                message.chat.id,
                "❌ دریافت تنظیمات ناموفق بود.",
            )

    @bot.message_handler(
        func=lambda message: message.text == "🔎 نوع انتخاب غذا"
    )
    def selection_mode_settings(message):
        try:
            user = get_user(message.from_user.id)

            if user is None:
                bot.send_message(
                    message.chat.id,
                    "❌ ابتدا حساب دانشگاهت را ثبت کن.",
                    reply_markup=main_menu(),
                )
                return

            bot.send_message(
                message.chat.id,
                "🔎 <b>نوع انتخاب غذا</b>\n\n"
                "روش انتخاب غذا را مشخص کن:",
                parse_mode="HTML",
                reply_markup=selection_mode_keyboard(user[6]),
            )

        except Exception:
            print("Failed to load food selection settings.")
            bot.send_message(
                message.chat.id,
                "❌ دریافت تنظیمات ناموفق بود.",
            )

    @bot.message_handler(commands=["reserve"])
    def reserve(message):
        run_reservation(
            bot=bot,
            chat_id=message.chat.id,
            telegram_id=message.from_user.id,
        )

    @bot.message_handler(
        func=lambda message: message.text == "🤖 رزرو خودکار"
    )
    def auto_reservation(message):
        run_reservation(
            bot=bot,
            chat_id=message.chat.id,
            telegram_id=message.from_user.id,
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
            "🍽 هنوز بخش نمایش رزروها پیاده‌سازی نشده.",
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

    @bot.callback_query_handler(
        func=lambda call: (
            call.data.startswith("day:")
            or call.data.startswith("days:")
        )
    )
    def handle_reservation_days(call):
        telegram_id = call.from_user.id

        try:
            user = get_user(telegram_id)

            if user is None:
                bot.answer_callback_query(
                    call.id,
                    "ابتدا حساب دانشگاهت را ثبت کن.",
                    show_alert=True,
                )
                return

            selected_days = [
                day.strip()
                for day in (user[4] or "").split(",")
                if day.strip()
            ]

            day_names = {
                "sat": "شنبه",
                "sun": "یکشنبه",
                "mon": "دوشنبه",
                "tue": "سه‌شنبه",
                "wed": "چهارشنبه",
            }

            if call.data.startswith("day:"):
                day_code = call.data.split(":", 1)[1]
                day_name = day_names.get(day_code)

                if day_name is None:
                    bot.answer_callback_query(
                        call.id,
                        "روز انتخاب‌شده معتبر نیست.",
                        show_alert=True,
                    )
                    return

                if day_name in selected_days:
                    selected_days.remove(day_name)
                else:
                    selected_days.append(day_name)

                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=reservation_days_keyboard(selected_days),
                )
                bot.answer_callback_query(call.id)
                return

            action = call.data.split(":", 1)[1]

            if action == "save":
                if not selected_days:
                    bot.answer_callback_query(
                        call.id,
                        "حداقل یک روز را انتخاب کن.",
                        show_alert=True,
                    )
                    return

                ordered_days = [
                    day for day in day_names.values()
                    if day in selected_days
                ]

                update_user_setting(
                    telegram_id,
                    "reservation_days",
                    ",".join(ordered_days),
                )

                bot.answer_callback_query(
                    call.id,
                    "تنظیمات ذخیره شد.",
                )
                bot.edit_message_text(
                    "✅ روزهای رزرو ذخیره شدند.\n\n"
                    + "، ".join(ordered_days),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )

            elif action == "back":
                bot.answer_callback_query(call.id)
                bot.send_message(
                    call.message.chat.id,
                    "⚙️ برگشت به تنظیمات.",
                    reply_markup=settings_menu(),
                )

            else:
                bot.answer_callback_query(
                    call.id,
                    "عملیات نامعتبر است.",
                    show_alert=True,
                )

        except Exception:
            print("Failed to update reservation days.")
            bot.answer_callback_query(
                call.id,
                "ذخیره تنظیمات ناموفق بود.",
                show_alert=True,
            )

    @bot.callback_query_handler(
        func=lambda call: (
            call.data.startswith("meal:")
            or call.data.startswith("mode:")
        )
    )
    def handle_other_settings(call):
        telegram_id = call.from_user.id
        action, _, value = call.data.partition(":")

        if value == "back":
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                "⚙️ برگشت به تنظیمات.",
                reply_markup=settings_menu(),
            )
            return

        if action == "meal":
            if value not in {"صبحانه", "ناهار", "شام"}:
                bot.answer_callback_query(
                    call.id,
                    "وعده غذایی معتبر نیست.",
                    show_alert=True,
                )
                return

            field = "meal"
            keyboard_factory = meal_keyboard

        elif action == "mode":
            if value not in {
                "اولین غذای موجود",
                "ارزان‌ترین غذا",
            }:
                bot.answer_callback_query(
                    call.id,
                    "روش انتخاب غذا معتبر نیست.",
                    show_alert=True,
                )
                return

            field = "selection_mode"
            keyboard_factory = selection_mode_keyboard

        else:
            bot.answer_callback_query(call.id)
            return

        try:
            user = get_user(telegram_id)

            if user is None:
                bot.answer_callback_query(
                    call.id,
                    "ابتدا حساب دانشگاهت را ثبت کن.",
                    show_alert=True,
                )
                return

            update_user_setting(
                telegram_id,
                field,
                value,
            )

            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard_factory(value),
            )

            bot.answer_callback_query(
                call.id,
                "تنظیمات ذخیره شد.",
            )

        except Exception:
            print("Failed to update user settings.")
            bot.answer_callback_query(
                call.id,
                "ذخیره تنظیمات ناموفق بود.",
                show_alert=True,
            )
