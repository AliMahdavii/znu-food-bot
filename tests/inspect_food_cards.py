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

        print("\n=== BUTTON DETAILS ===")

        buttons = page.locator("button")

        for i in range(buttons.count()):
            button = buttons.nth(i)

            try:
                print(f"\n--- BUTTON {i} ---")
                print("TEXT:", repr(button.inner_text()))
                print("TYPE:", button.get_attribute("type"))
                print("CLASS:", button.get_attribute("class"))
                print("ID:", button.get_attribute("id"))

                print("HTML:")
                print(button.evaluate("(el) => el.outerHTML"))

            except Exception as e:
                print("ERROR:", e)

        print("\n=== INPUTS ===")

        inputs = page.locator("input")

        for i in range(inputs.count()):
            element = inputs.nth(i)

            try:
                print(f"\n--- INPUT {i} ---")
                print("TYPE:", element.get_attribute("type"))
                print("NAME:", element.get_attribute("name"))
                print("VALUE:", element.get_attribute("value"))
                print("CLASS:", element.get_attribute("class"))
                print("ID:", element.get_attribute("id"))

            except Exception as e:
                print("ERROR:", e)

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
