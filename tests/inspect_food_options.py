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
    page.goto(
        ZNU_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    print("Logging in...")
    print("Login:", login(page))

    print("Opening reservation page...")
    page.goto(
        "https://student.znu.ac.ir/#!/Reservation",
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(2000)

    print("Going to next week...")

    page.locator(
        'button[ng-click="browseWeek(startdate,7)"]'
    ).click()

    page.wait_for_timeout(1500)

    days = [
        ("شنبه", 0),
        ("یکشنبه", 1),
        ("دوشنبه", 2),
        ("سه شنبه", 3),
        ("چهارشنبه", 4),
    ]

    for day_name, dayindex in days:

        print("\n" + "=" * 50)
        print(day_name)
        print("=" * 50)

        if dayindex > 0:
            page.locator(
                f'label[href="#tab_day{dayindex}"]'
            ).click()

            page.wait_for_timeout(500)

        add_button = page.locator(
            'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
        ).nth(dayindex)

        container = add_button.locator("..")

        food_select = container.locator(
            'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
        )

        options = food_select.locator("option")

        print("Option count:", options.count())

        for i in range(options.count()):
            option = options.nth(i)

            print(
                f"{i}: "
                f"text={option.inner_text().strip()!r}, "
                f"value={option.get_attribute('value')!r}"
            )

    print("\nBrowser will remain open.")
    input()
