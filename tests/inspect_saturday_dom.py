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
        # Inspect all tables
        # ---------------------------------------------------------

        print("\n=== TABLES ===")

        tables = page.locator("table")

        print(
            "Table count:",
            tables.count(),
        )

        for i in range(tables.count()):
            table = tables.nth(i)

            print(f"\n--- TABLE {i} ---")

            print(
                "CLASS:",
                table.get_attribute("class"),
            )

            rows = table.locator("tr")

            print(
                "Rows:",
                rows.count(),
            )

            for r in range(rows.count()):
                row = rows.nth(r)

                print(f"\n  ROW {r}")

                cells = row.locator("th, td")

                print(
                    "  Cells:",
                    cells.count(),
                )

                for c in range(cells.count()):
                    cell = cells.nth(c)

                    text = cell.inner_text().strip()

                    print(
                        f"    CELL {c}:",
                        repr(text[:500]),
                    )

        # ---------------------------------------------------------
        # Find food schedule table
        # ---------------------------------------------------------

        print("\n=== FOOD SCHEDULE TABLE ===")

        food_table = page.locator(
            "table.table-bordered.table-striped.table-hover"
        ).first

        print(
            "Food table count:",
            page.locator(
                "table.table-bordered.table-striped.table-hover"
            ).count(),
        )

        print(
            "Food table class:",
            food_table.get_attribute("class"),
        )

        # ---------------------------------------------------------
        # Find lunch row
        # ---------------------------------------------------------

        print("\n=== LUNCH ROW ===")

        lunch_row = food_table.locator("tr").filter(
            has_text="ناهار"
        )

        print(
            "Lunch row count:",
            lunch_row.count(),
        )

        if lunch_row.count() == 0:
            print("❌ Lunch row not found")

        else:
            lunch = lunch_row.first

            lunch_cells = lunch.locator("td")

            print(
                "Lunch cells:",
                lunch_cells.count(),
            )

            # -----------------------------------------------------
            # Inspect all lunch cells
            # -----------------------------------------------------

            for i in range(lunch_cells.count()):
                cell = lunch_cells.nth(i)

                print(
                    f"\n--- LUNCH CELL {i} ---"
                )

                print(
                    "TEXT:",
                    repr(cell.inner_text()),
                )

                print(
                    "CLASS:",
                    cell.get_attribute("class"),
                )

                print(
                    "HTML:",
                    cell.inner_html(),
                )

            # -----------------------------------------------------
            # Saturday lunch
            # -----------------------------------------------------

            if lunch_cells.count() > 1:

                saturday_lunch = lunch_cells.nth(1)

                print(
                    "\n=== SATURDAY LUNCH ==="
                )

                print(
                    "TEXT:",
                    repr(
                        saturday_lunch.inner_text()
                    ),
                )

                print(
                    "CLASS:",
                    saturday_lunch.get_attribute(
                        "class"
                    ),
                )

                print(
                    "HTML:",
                    saturday_lunch.inner_html(),
                )

                # -------------------------------------------------
                # Inspect buttons
                # -------------------------------------------------

                print(
                    "\n=== SATURDAY LUNCH BUTTONS ==="
                )

                buttons = saturday_lunch.locator(
                    "button"
                )

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
                        repr(
                            button.inner_text()
                        ),
                    )

                    print(
                        "CLASS:",
                        button.get_attribute(
                            "class"
                        ),
                    )

                    print(
                        "NG-CLICK:",
                        button.get_attribute(
                            "ng-click"
                        ),
                    )

                    print(
                        "NG-IF:",
                        button.get_attribute(
                            "ng-if"
                        ),
                    )

                    print(
                        "NG-REPEAT:",
                        button.get_attribute(
                            "ng-repeat"
                        ),
                    )

                    print(
                        "TITLE:",
                        button.get_attribute(
                            "title"
                        ),
                    )

                    print(
                        "TYPE:",
                        button.get_attribute(
                            "type"
                        ),
                    )

                    print(
                        "HTML:",
                        button.evaluate(
                            "(el) => el.outerHTML"
                        ),
                    )

        print(
            "\nBrowser will remain open."
        )

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
