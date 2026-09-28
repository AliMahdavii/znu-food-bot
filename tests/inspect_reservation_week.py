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

        print("\n=== TEXT / WEEK RELATED ELEMENTS ===")

        elements = page.locator(
            "button, a, input, select, option, "
            "[ng-click], [ng-model], [ng-change]"
        )

        keywords = [
            "هفته",
            "بعد",
            "قبلی",
            "انتخاب",
            "تاریخ",
            "شنبه",
            "یکشنبه",
            "دوشنبه",
            "سه‌شنبه",
            "چهارشنبه",
            "پنجشنبه",
            "جمعه",
        ]

        for i in range(elements.count()):
            element = elements.nth(i)

            try:
                text = element.inner_text().strip()
            except Exception:
                text = ""

            try:
                ng_click = element.get_attribute("ng-click")
            except Exception:
                ng_click = None

            try:
                ng_model = element.get_attribute("ng-model")
            except Exception:
                ng_model = None

            try:
                ng_change = element.get_attribute("ng-change")
            except Exception:
                ng_change = None

            combined = " ".join(
                filter(
                    None,
                    [
                        text,
                        ng_click,
                        ng_model,
                        ng_change,
                    ],
                )
            )

            if any(keyword in combined for keyword in keywords):
                print(
                    f"\n[{i}]"
                    f"\n  text      = {text!r}"
                    f"\n  ng-click  = {ng_click!r}"
                    f"\n  ng-model  = {ng_model!r}"
                    f"\n  ng-change = {ng_change!r}"
                )

        print("\n=== ALL BUTTONS ===")

        buttons = page.locator("button")

        for i in range(buttons.count()):
            button = buttons.nth(i)

            try:
                print(
                    f"[{i}] "
                    f"text={button.inner_text().strip()!r} "
                    f"ng-click={button.get_attribute('ng-click')!r} "
                    f"title={button.get_attribute('title')!r}"
                )
            except Exception:
                pass

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
