from playwright.sync_api import sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=EDGE_PATH,
    )

    page = browser.new_page()

    page.goto(
        ZNU_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    print("Logging in...")
    print("Login:", login(page))

    page.goto("https://student.znu.ac.ir/#!/Reservation")
    page.wait_for_timeout(2000)

    page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    ).click()

    page.wait_for_timeout(1500)

    # چهارشنبه
    page.locator(
        'label[href="#tab_day4"]'
    ).click()

    page.wait_for_timeout(700)

    add_button = page.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    ).nth(4)

    container = add_button.locator("..")

    food_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
    )

    food_value = food_select.locator("option").nth(1).get_attribute("value")

    food_select.select_option(food_value)

    page.wait_for_timeout(1000)

    add_button.click()

    page.wait_for_timeout(1000)

    confirm_button = page.locator(
        'button[ng-click="FinallReserve(dayindex,mealindex)"]'
    ).nth(4)

    confirm_button.click()

    page.wait_for_timeout(2000)

    print("\n=== ELEMENTS CONTAINING RESULT TEXT ===")

    elements = page.get_by_text(
        "نتیجه ارسال درخواست",
        exact=False
    )

    print("Count:", elements.count())

    for i in range(elements.count()):
        element = elements.nth(i)

        try:
            print(f"\n--- Element {i} ---")
            print("Tag:", element.evaluate("(el) => el.tagName"))
            print("Visible:", element.is_visible())
            print("Text:", element.inner_text())
            print(
                "HTML:",
                element.evaluate("(el) => el.outerHTML")
            )

            print(
                "Parent HTML:",
                element.evaluate(
                    "(el) => el.parentElement.outerHTML"
                )
            )

        except Exception as e:
            print("Error:", e)

    print("\nBrowser will remain open.")
    input()
