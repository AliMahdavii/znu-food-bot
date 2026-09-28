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

        # Saturday / lunch
        dayindex = 0
        mealindex = 1

        add_food = page.locator(
            '[ng-click*="AddFood"]'
        ).nth(dayindex)

        container = add_food.locator(
            "xpath=ancestor::div[contains(@class,'tab-pane')][1]"
        )

        food_select = container.locator(
            'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
        )

        self_select = container.locator(
            'select[ng-model="selectitem[dayindex].peek[mealindex].selectedSelf"]'
        )

        add_button = container.locator(
            'button[ng-click*="AddFood"]'
        )

        print("\n=== INITIAL STATE ===")

        print(
            "Food select:",
            food_select.input_value(),
        )

        print(
            "Self select:",
            self_select.input_value(),
        )

        print(
            "AddFood disabled:",
            add_button.is_disabled(),
        )

        # Get first real food option.
        food_option = food_select.locator(
            "option"
        ).nth(1)

        food_value = food_option.get_attribute(
            "value"
        )

        food_text = food_option.inner_text().strip()

        print("\n=== SELECTING FOOD ===")

        print(
            "Food:",
            food_text,
        )

        print(
            "Value:",
            food_value,
        )

        food_select.select_option(
            food_value
        )

        # Angular needs a moment to execute GetFillSelf.
        page.wait_for_timeout(1000)

        print("\n=== AFTER FOOD SELECTION ===")

        print(
            "Food select:",
            food_select.input_value(),
        )

        print(
            "Self select:",
            self_select.input_value(),
        )

        print(
            "Self option count:",
            self_select.locator("option").count(),
        )

        for i in range(
            self_select.locator("option").count()
        ):
            option = self_select.locator(
                "option"
            ).nth(i)

            print(
                f"Self option {i}:",
                repr(option.inner_text().strip()),
                "| value:",
                option.get_attribute("value"),
            )

        print("\n=== SELF AUTO-SELECTION ===")

        print(
            "Self:",
            self_select.locator("option").first.inner_text().strip(),
        )

        print(
            "Self value:",
            self_select.input_value(),
        )

        print(
            "AddFood disabled:",
            add_button.is_disabled(),
        )

        print("\n=== FINAL STATE ===")

        print(
            "Food select:",
            food_select.input_value(),
        )

        print(
            "Self select:",
            self_select.input_value(),
        )

        print(
            "AddFood disabled:",
            add_button.is_disabled(),
        )

        print(
            "\nBrowser will remain open."
        )

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
