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
    page.wait_for_timeout(2000)

    # Saturday lunch
    container = page.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    ).nth(0).locator("..")

    food_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
    )

    self_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedSelf"]'
    )

    add_button = container.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    )

    print("\n=== BEFORE SELECTION ===")

    print(
        "Food:",
        food_select.input_value(),
    )

    print(
        "Self:",
        self_select.input_value(),
    )

    print(
        "AddFood disabled:",
        add_button.is_disabled(),
    )

    # Select first food
    print("\n=== SELECTING FIRST FOOD ===")

    food_option = food_select.locator("option").nth(1)

    print(
        "Food:",
        food_option.inner_text().strip(),
    )

    print(
        "Value:",
        food_option.get_attribute("value"),
    )

    food_select.select_option(
        food_option.get_attribute("value")
    )

    page.wait_for_timeout(1000)

    print("\n=== AFTER SELECTION ===")

    print(
        "Food:",
        food_select.input_value(),
    )

    print(
        "Self:",
        self_select.input_value(),
    )

    print(
        "AddFood disabled:",
        add_button.is_disabled(),
    )

    # Add food
    print("\n=== CLICKING ADD FOOD ===")

    add_button.click()

    page.wait_for_timeout(1500)

    print("\n=== AFTER ADD FOOD ===")

    print(
        "Food:",
        food_select.input_value(),
    )

    print(
        "Self:",
        self_select.input_value(),
    )

    print(
        "AddFood disabled:",
        add_button.is_disabled(),
    )

    print(
        "Current URL:",
        page.url,
    )

    print("\n=== PAGE TEXT AFTER ADD ===")

    print(
        page.locator("body").inner_text()[:5000]
    )

    print("\nBrowser will remain open.")

    input()
