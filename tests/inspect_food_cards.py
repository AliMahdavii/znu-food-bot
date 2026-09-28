from pathlib import Path

from playwright.sync_api import sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


RESERVATION_URL = "https://student.znu.ac.ir/#!/Reservation"
OUTPUT_FILE = Path("food_inspection.txt")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=EDGE_PATH,
        )

        page = browser.new_page()

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

        # =========================
        # Next week
        # =========================

        next_week = page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        if next_week.count() == 0:
            print("❌ Next week button not found.")
            browser.close()
            return

        print("Going to next week...")

        next_week.click()

        page.wait_for_timeout(2000)

        # =========================
        # Inspect
        # =========================

        output = []

        output.append("=== FOOD ELEMENTS ===\n")

        elements = page.locator(
            "[ng-click], "
            "[ng-model], "
            "[ng-if], "
            "[ng-repeat], "
            "button, "
            "input, "
            "select"
        )

        keywords = [
            "چلو",
            "لوبیا",
            "کباب",
            "غذا",
            "AddFood",
            "افزودن",
            "ناهار",
        ]

        for i in range(elements.count()):
            element = elements.nth(i)

            try:
                text = element.inner_text().strip()
            except Exception:
                text = ""

            ng_click = element.get_attribute("ng-click")
            ng_model = element.get_attribute("ng-model")
            ng_repeat = element.get_attribute("ng-repeat")
            ng_if = element.get_attribute("ng-if")

            combined = " ".join(
                filter(
                    None,
                    [
                        text,
                        ng_click,
                        ng_model,
                        ng_repeat,
                        ng_if,
                    ],
                )
            )

            if any(
                keyword in combined
                for keyword in keywords
            ):
                output.append(
                    f"""
[{i}]
  text      = {text!r}
  ng-click  = {ng_click!r}
  ng-model  = {ng_model!r}
  ng-repeat = {ng_repeat!r}
  ng-if     = {ng_if!r}
"""
                )

        output.append("\n=== FOOD BUTTONS ===\n")

        buttons = page.locator("button")

        for i in range(buttons.count()):
            button = buttons.nth(i)

            try:
                output.append(
                    f"[{i}] "
                    f"text={button.inner_text().strip()!r} "
                    f"ng-click={button.get_attribute('ng-click')!r} "
                    f"disabled={button.is_disabled()}\n"
                )
            except Exception:
                pass

        OUTPUT_FILE.write_text(
            "".join(output),
            encoding="utf-8",
        )

        print(f"\n✅ Inspection saved to: {OUTPUT_FILE}")

        print("Browser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
