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
    page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    ).click()

    page.wait_for_timeout(1500)

    # چهارشنبه
    dayindex = 4

    print("\nActivating Wednesday tab...")

    page.locator(
        'label[href="#tab_day4"]'
    ).click()

    page.wait_for_timeout(700)

    add_button = page.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    ).nth(dayindex)

    container = add_button.locator("..")

    food_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
    )

    food_option = food_select.locator("option").nth(1)

    print("Food:", food_option.inner_text().strip())

    food_value = food_option.get_attribute("value")

    food_select.select_option(food_value)

    page.wait_for_timeout(1000)

    print("Adding food...")
    add_button.click()

    page.wait_for_timeout(1000)

    confirm_button = page.locator(
        'button[ng-click="FinallReserve(dayindex,mealindex)"]'
    ).nth(dayindex)

    print("Confirm button enabled:", confirm_button.is_enabled())

    print("\nBefore confirmation:")
    print(page.locator("body").inner_text())

    print("\nConfirming reservation...")

    confirm_button.click()

    # عمداً کمی بیشتر صبر می‌کنیم
    page.wait_for_timeout(3000)

    print("\n" + "=" * 60)
    print("AFTER FINAL RESERVATION")
    print("=" * 60)

    print("\n=== BODY TEXT ===")
    print(page.locator("body").inner_text())

    print("\n=== ALERTS ===")

    alerts = page.locator(
        '.alert, .modal, [role="alert"]'
    )

    print("Count:", alerts.count())

    for i in range(alerts.count()):
        try:
            element = alerts.nth(i)

            print(f"\n--- Alert {i} ---")
            print("Visible:", element.is_visible())
            print("Text:", element.inner_text())
            print(
                "HTML:",
                element.evaluate("(el) => el.outerHTML")
            )

        except Exception as e:
            print("Error:", e)

    print("\nBrowser will remain open.")
    input()
