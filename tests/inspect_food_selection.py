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

        print("Going to next week...")

        next_week = page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        next_week.click()

        page.wait_for_timeout(2000)

        print("\n=== FIRST ADDFOOD CONTAINER ===")

        add_food = page.locator(
            '[ng-click*="AddFood"]'
        ).nth(0)

        # Find the nearest tab-pane containing the whole food card.
        container = add_food.locator(
            "xpath=ancestor::div[contains(@class,'tab-pane')][1]"
        )

        print(
            "Container count:",
            container.count(),
        )

        print("\n=== SELECT ELEMENTS ===")

        selects = container.locator("select")

        print(
            "Select count:",
            selects.count(),
        )

        for i in range(selects.count()):

            select = selects.nth(i)

            print(
                f"\n--- SELECT {i} ---"
            )

            print(
                "NAME:",
                select.get_attribute("name"),
            )

            print(
                "NG-MODEL:",
                select.get_attribute("ng-model"),
            )

            print(
                "NG-CHANGE:",
                select.get_attribute("ng-change"),
            )

            print(
                "NG-OPTIONS:",
                select.get_attribute("ng-options"),
            )

            print(
                "CLASS:",
                select.get_attribute("class"),
            )

            print(
                "OUTER HTML:"
            )

            print(
                select.evaluate(
                    "(el) => el.outerHTML"
                )
            )

            options = select.locator("option")

            print(
                "OPTION COUNT:",
                options.count(),
            )

            for j in range(options.count()):

                option = options.nth(j)

                print(
                    f"  OPTION {j}:",
                    repr(option.inner_text()),
                    "| value:",
                    option.get_attribute("value"),
                )

        print("\n=== INPUT ELEMENTS ===")

        inputs = container.locator("input")

        print(
            "Input count:",
            inputs.count(),
        )

        for i in range(inputs.count()):

            inp = inputs.nth(i)

            print(
                f"\n--- INPUT {i} ---"
            )

            print(
                "TYPE:",
                inp.get_attribute("type"),
            )

            print(
                "NAME:",
                inp.get_attribute("name"),
            )

            print(
                "VALUE:",
                inp.get_attribute("value"),
            )

            print(
                "NG-MODEL:",
                inp.get_attribute("ng-model"),
            )

            print(
                "NG-CHANGE:",
                inp.get_attribute("ng-change"),
            )

            print(
                "NG-CLICK:",
                inp.get_attribute("ng-click"),
            )

            print(
                "OUTER HTML:"
            )

            print(
                inp.evaluate(
                    "(el) => el.outerHTML"
                )
            )

        print("\n=== BUTTONS ===")

        buttons = container.locator("button")

        print(
            "Button count:",
            buttons.count(),
        )

        for i in range(buttons.count()):

            button = buttons.nth(i)

            print(
                f"\n--- BUTTON {i} ---"
            )

            print(
                "TEXT:",
                repr(button.inner_text()),
            )

            print(
                "NG-CLICK:",
                button.get_attribute("ng-click"),
            )

            print(
                "NG-MODEL:",
                button.get_attribute("ng-model"),
            )

            print(
                "NG-DISABLED:",
                button.get_attribute("ng-disabled"),
            )

            print(
                "OUTER HTML:"
            )

            print(
                button.evaluate(
                    "(el) => el.outerHTML"
                )
            )

        print(
            "\nBrowser will remain open."
        )

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
