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

        # ---------------------------------------------------------
        # Go to next week
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Find AddFood elements
        # ---------------------------------------------------------

        print("\n=== ADDFOOD ELEMENTS ===")

        add_food = page.locator(
            '[ng-click*="AddFood"]'
        )

        print(
            "AddFood count:",
            add_food.count(),
        )

        for i in range(add_food.count()):

            element = add_food.nth(i)

            print(
                f"\n--- ADDFOOD {i} ---"
            )

            print(
                "TAG:",
                element.evaluate(
                    "(el) => el.tagName"
                ),
            )

            print(
                "TEXT:",
                repr(
                    element.inner_text()
                ),
            )

            print(
                "CLASS:",
                element.get_attribute(
                    "class"
                ),
            )

            print(
                "NG-CLICK:",
                element.get_attribute(
                    "ng-click"
                ),
            )

            print(
                "NG-IF:",
                element.get_attribute(
                    "ng-if"
                ),
            )

            print(
                "NG-REPEAT:",
                element.get_attribute(
                    "ng-repeat"
                ),
            )

            print(
                "TITLE:",
                element.get_attribute(
                    "title"
                ),
            )

            print(
                "OUTER HTML:"
            )

            print(
                element.evaluate(
                    "(el) => el.outerHTML"
                )
            )

            # -----------------------------------------------------
            # Parent levels
            # -----------------------------------------------------

            current = element

            for level in range(1, 5):

                current = current.locator(
                    "xpath=.."
                )

                print(
                    f"\n  PARENT LEVEL {level}"
                )

                print(
                    "  TAG:",
                    current.evaluate(
                        "(el) => el.tagName"
                    ),
                )

                print(
                    "  CLASS:",
                    current.get_attribute(
                        "class"
                    ),
                )

                print(
                    "  NG-REPEAT:",
                    current.get_attribute(
                        "ng-repeat"
                    ),
                )

                print(
                    "  NG-IF:",
                    current.get_attribute(
                        "ng-if"
                    ),
                )

                print(
                    "  NG-CLICK:",
                    current.get_attribute(
                        "ng-click"
                    ),
                )

                text = current.inner_text().strip()

                print(
                    "  TEXT:",
                    repr(text[:500]),
                )

        print(
            "\nBrowser will remain open."
        )

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
