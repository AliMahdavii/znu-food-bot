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

        print("Login page:", page.url)

        success = login(page)

        print("\n=== LOGIN RESULT ===")
        print("Success:", success)
        print("Current URL:", page.url)
        print("Title:", page.title())

        page.wait_for_timeout(5000)

        browser.close()


if __name__ == "__main__":
    main()
