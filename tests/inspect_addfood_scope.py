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

        print(
            "Next week button count:",
            next_week.count(),
        )

        next_week.click()

        page.wait_for_timeout(2000)

        add_food = page.locator(
            '[ng-click*="AddFood"]'
        )

        print(
            "\n=== ADDFOOD ANGULAR SCOPES ==="
        )

        print(
            "Count:",
            add_food.count(),
        )

        for i in range(add_food.count()):

            element = add_food.nth(i)

            print(
                f"\n--- ADDFOOD {i} ---"
            )

            print(
                "TEXT:",
                repr(
                    element.locator(
                        "xpath=.."
                    ).inner_text()
                ),
            )

            result = element.evaluate(
                """
                (el) => {
                    const injector = angular.element(el).injector();

                    if (!injector) {
                        return {
                            error: "No Angular injector"
                        };
                    }

                    const scope = angular.element(el).scope();

                    if (!scope) {
                        return {
                            error: "No Angular scope"
                        };
                    }

                    return {
                        dayindex: scope.dayindex,
                        mealindex: scope.mealindex,
                        mealitm: scope.mealitm
                    };
                }
                """
            )

            print(
                "SCOPE:",
                result,
            )

        print(
            "\nBrowser will remain open."
        )

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
