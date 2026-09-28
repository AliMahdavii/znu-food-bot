from playwright.sync_api import sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


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
            "https://student.znu.ac.ir/#!/Reservation",
            wait_until="domcontentloaded",
        )

        page.wait_for_timeout(3000)

        print("\n=== RESERVATION HTML ===")

        body_html = page.locator("body").inner_html()

        with open(
            "reservation_page.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(body_html)

        print("Saved: reservation_page.html")

        print("\n=== ELEMENTS WITH AddFood ===")

        elements = page.locator('[ng-click*="AddFood"]')

        print("Count:", elements.count())

        for i in range(elements.count()):
            element = elements.nth(i)

            print(f"\n--- AddFood element {i} ---")
            print(element.evaluate("(el) => el.outerHTML"))

        print("\n=== ELEMENTS WITH FinallReserve ===")

        elements = page.locator('[ng-click*="FinallReserve"]')

        print("Count:", elements.count())

        for i in range(elements.count()):
            element = elements.nth(i)

            print(f"\n--- FinallReserve element {i} ---")
            print(element.evaluate("(el) => el.outerHTML"))

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()