from playwright.sync_api import sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=EDGE_PATH,
    )

    page = browser.new_page()

    print("Opening ZNU...")
    page.goto(ZNU_URL)

    print("Logging in...")
    print("Login:", login(page))

    print("Opening reservation page...")
    page.goto("https://student.znu.ac.ir/#!/Reservation")

    page.wait_for_timeout(2000)

    print("Going to next week...")

    next_week = page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    )

    next_week.click()
    page.wait_for_timeout(1500)

    # Saturday lunch
    add_button = page.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    ).nth(0)

    container = add_button.locator("..")

    food_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
    )

    # Select first food
    food_option = food_select.locator("option").nth(1)

    print("\n=== SELECTING FOOD ===")

    print(
        "Food:",
        food_option.inner_text().strip(),
    )

    food_select.select_option(
        food_option.get_attribute("value")
    )

    page.wait_for_timeout(1000)

    print(
        "AddFood disabled:",
        add_button.is_disabled(),
    )

    # Add to cart
    print("\n=== ADDING TO CART ===")

    add_button.click()

    page.wait_for_timeout(1500)

    print("\n=== CART ===")

    print(
        "Cart text:",
        page.get_by_text("سبد", exact=False).all_inner_texts()
    )

    # Find final confirmation button
    print("\n=== CONFIRM BUTTON SEARCH ===")

    confirm_buttons = page.get_by_text(
        "تایید نهایی سبد خرید",
        exact=True,
    )

    print(
        "Count:",
        confirm_buttons.count(),
    )

    if confirm_buttons.count() == 0:
        print("❌ Confirm button not found.")
    else:
        confirm_button = confirm_buttons.first

        print("Text:", confirm_button.inner_text())
        print("Tag:", confirm_button.evaluate("(el) => el.tagName"))
        print("HTML:")
        print(
            confirm_button.evaluate(
                "(el) => el.outerHTML"
            )
        )

        print("\n=== PARENT HTML ===")

        print(
            confirm_button.locator("..").evaluate(
                "(el) => el.outerHTML"
            )
        )

        print("\n=== ATTRIBUTES ===")

        attributes = confirm_button.evaluate(
            """
            (el) => {
                const result = {};
                for (const attr of el.attributes) {
                    result[attr.name] = attr.value;
                }
                return result;
            }
            """
        )

        for name, value in attributes.items():
            print(f"{name}: {value}")

        print("\n=== BUTTON STATE ===")

        print(
            "Visible:",
            confirm_button.is_visible(),
        )

        print(
            "Enabled:",
            confirm_button.is_enabled(),
        )

    print("\nBrowser will remain open.")

    input()
