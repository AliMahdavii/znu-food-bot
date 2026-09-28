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

        # =========================
        # Go to next week
        # =========================

        next_week = page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        print("Next week button count:", next_week.count())

        if next_week.count() == 0:
            print("❌ Next week button not found.")
            browser.close()
            return

        print("Going to next week...")
        next_week.click()

        page.wait_for_timeout(2000)

        # =========================
        # Find Saturday
        # =========================

        saturday = page.locator(
            "text=شنبه"
        ).first

        print("Saturday found:", saturday.count())

        if saturday.count() == 0:
            print("❌ Saturday not found.")
            browser.close()
            return

        print("Saturday:", saturday.inner_text())

        # =========================
        # Find Saturday container
        # =========================

        saturday_container = saturday.locator(
            "xpath=ancestor::*[contains(@ng-repeat, 'dayindex,dayitm')][1]"
        )

        print(
            "Saturday container:",
            saturday_container.count()
        )

        if saturday_container.count() == 0:
            print("❌ Saturday container not found.")
            browser.close()
            return

        # =========================
        # Find lunch
        # =========================

        lunch = saturday_container.locator(
            '[ng-repeat*="mealindex,mealitm"]'
        ).filter(
            has_text="ناهار"
        ).first

        print("Lunch container:", lunch.count())

        if lunch.count() == 0:
            print("❌ Saturday lunch not found.")
            browser.close()
            return

        # =========================
        # Food menu
        # =========================

        foods = lunch.locator(
            '[ng-repeat*="fooditm in mealitm.FoodMenu"]'
        )

        food_count = foods.count()

        print("\nFood count:", food_count)

        if food_count == 0:
            print("❌ No food found.")
            browser.close()
            return

        print("\n=== SATURDAY FOODS ===")

        for i in range(food_count):
            food = foods.nth(i)

            print(
                f"[{i}] {food.inner_text().strip()}"
            )

        # =========================
        # Select first food
        # =========================

        first_food = foods.first

        print(
            "\nSelecting first food:",
            first_food.inner_text().strip()
        )

        first_food.click()

        page.wait_for_timeout(500)

        # =========================
        # Add to cart
        # =========================

        add_button = lunch.locator(
            'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
        )

        print(
            "Add to cart button:",
            add_button.count()
        )

        if add_button.count() == 0:
            print("❌ Add to cart button not found.")
            browser.close()
            return

        print(
            "Button disabled:",
            add_button.is_disabled()
        )

        if add_button.is_disabled():
            print(
                "❌ Add to cart is still disabled."
            )
            browser.close()
            return

        print("\n🛒 Adding Saturday lunch to cart...")

        add_button.click()

        page.wait_for_timeout(1500)

        print("\n✅ Saturday food added to cart.")

        print("\nBrowser will remain open for inspection.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
