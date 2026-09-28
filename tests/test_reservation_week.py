from playwright.sync_api import sync_playwright

from bot.login import login
from bot.reservation import reserve_week
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
    login_success = login(page)
    print("Login:", login_success)

    if not login_success:
        print("❌ Login failed.")
        browser.close()
        raise SystemExit(1)

    print("Opening reservation page...")
    page.goto("https://student.znu.ac.ir/#!/Reservation")

    page.wait_for_timeout(2000)

    print("Going to next week...")

    next_week = page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    )

    if next_week.count() == 0:
        print("❌ Next week button not found.")
        browser.close()
        raise SystemExit(1)

    next_week.click()
    page.wait_for_timeout(1500)

    print("\n" + "=" * 50)
    print("STARTING WEEK RESERVATION")
    print("=" * 50)

    results = reserve_week(page)

    print("\n" + "=" * 50)
    print("WEEK RESERVATION RESULT")
    print("=" * 50)

    for result in results:
        print(
            f"\n{result.day}"
            f"\n  Food: {result.food}"
            f"\n  Price: {result.price}"
            f"\n  Success: {result.success}"
            f"\n  Message: {result.message}"
        )

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    successful = sum(1 for result in results if result.success)
    failed = len(results) - successful

    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    print("\nBrowser will remain open.")
    input()
