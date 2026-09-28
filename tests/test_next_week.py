from playwright.sync_api import sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


RESERVATION_URL = "https://student.znu.ac.ir/#!/Reservation"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=EDGE_PATH,
        )

        page = browser.new_page()

        print("Opening ZNU...")

        page.goto(
            ZNU_URL,
            wait_until="domcontentloaded",
        )

        print("Logging in...")

        success = login(page)

        print("Login:", success)

        if not success:
            browser.close()
            return

        print("Opening reservation page...")

        page.goto(
            RESERVATION_URL,
            wait_until="domcontentloaded",
        )

        page.wait_for_timeout(3000)

        print("Current URL:", page.url)

        # =========================
        # Go to next week
        # =========================

        next_week_button = page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        print(
            "Next week button count:",
            next_week_button.count()
        )

        if next_week_button.count() == 0:
            print("❌ Next week button not found.")
            browser.close()
            return

        print("Clicking next week...")

        next_week_button.click()

        # Angular needs a moment to update the page
        page.wait_for_timeout(2000)

        print("\n=== AFTER NEXT WEEK ===")

        print("URL:", page.url)

        print("\n=== VISIBLE TEXT ===")

        print(
            page.locator("body").inner_text()
        )

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
