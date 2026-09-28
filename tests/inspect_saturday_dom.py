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

        # Go to next week
        next_week = page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        next_week.click()

        page.wait_for_timeout(2000)

        # Find Saturday
        saturday = page.get_by_text(
            "شنبه",
            exact=False,
        ).first

        print("\n=== SATURDAY ===")
        print("Text:", repr(saturday.inner_text()))

        # Get parents
        current = saturday

        for level in range(1, 8):

            current = current.locator("xpath=..")

            print(f"\n=== PARENT LEVEL {level} ===")

            try:
                print("TAG:", current.evaluate("(el) => el.tagName"))
                print("CLASS:", current.get_attribute("class"))
                print(
                    "NG-REPEAT:",
                    current.get_attribute("ng-repeat")
                )
                print(
                    "NG-IF:",
                    current.get_attribute("ng-if")
                )
                print(
                    "NG-CLICK:",
                    current.get_attribute("ng-click")
                )

                text = current.inner_text().strip()

                print(
                    "TEXT:",
                    repr(text[:500])
                )

            except Exception as e:
                print("ERROR:", e)

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
