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

        print("\n=== LOGIN RESULT ===")
        print("Success:", success)
        print("Current URL:", page.url)
        print("Title:", page.title())

        if not success:
            print("Login failed.")
            browser.close()
            return

        print("\nOpening food reservation...")

        page.goto(
            "https://student.znu.ac.ir/#!/Reservation",
            wait_until="domcontentloaded",
        )

        page.wait_for_timeout(3000)

        print("\n=== RESERVATION PAGE ===")
        print("URL:", page.url)
        print("TITLE:", page.title())

        print("\n=== VISIBLE TEXT ===")
        print(page.locator("body").inner_text())

        print("\n=== LINKS ===")
        links = page.locator("a")

        for i in range(links.count()):
            link = links.nth(i)

            try:
                print(
                    f"[{i}] "
                    f"text={link.inner_text().strip()!r} "
                    f"href={link.get_attribute('href')!r}"
                )
            except Exception:
                pass

        print("\n=== BUTTONS ===")
        buttons = page.locator("button")

        for i in range(buttons.count()):
            button = buttons.nth(i)

            try:
                print(
                    f"[{i}] "
                    f"text={button.inner_text().strip()!r} "
                    f"type={button.get_attribute('type')!r}"
                )
            except Exception:
                pass

        print("\nBrowser will remain open for inspection.")
        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
