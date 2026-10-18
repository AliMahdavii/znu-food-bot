from bot.browser import ZNUBrowser
from bot.reservation import ReservationResult, reserve_week


def reserve_next_week(
    username: str,
    password: str,
    headless: bool = True,
) -> list[ReservationResult]:
    """Log in to ZNU and reserve lunch for the next week."""

    browser = ZNUBrowser(
        username=username,
        password=password,
        headless=headless,
    )

    try:
        page = browser.start()

        if not browser.login():
            raise RuntimeError("ZNU login failed.")

        browser.open_reservation_page()
        browser.go_to_next_week()

        return reserve_week(page)

    finally:
        browser.close()
