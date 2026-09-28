from playwright.sync_api import sync_playwright

from bot.login import login
from bot.reservation import reserve_day
from config.settings import EDGE_PATH, ZNU_URL


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=EDGE_PATH,
    )

    page = browser.new_page()

    print("Opening ZNU...")
    page.goto(ZNU_URL)

    print("Logging in...")
    print("Login:", login(page))

    print("Opening reservation page...")
    page.goto("https://student.znu.ac.ir/#!/Reservation")

    page.wait_for_timeout(2000)

    print("Going to next week...")

    next_week = page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    )

    next_week.click()

    page.wait_for_timeout(1500)

    result = reserve_day(
        page=page,
        dayindex=0,
        day_name="شنبه",
    )

    print("\n=== RESULT ===")

    print("Day:", result.day)
    print("Food:", result.food)
    print("Price:", result.price)
    print("Success:", result.success)
    print("Message:", result.message)

    print("\nBrowser will remain open.")

    input()