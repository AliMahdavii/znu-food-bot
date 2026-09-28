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

    print("\n=== ELEMENTS CONTAINING DAY NAMES ===")

    days = [
        "شنبه",
        "یکشنبه",
        "دوشنبه",
        "سه شنبه",
        "چهارشنبه",
    ]

    for day in days:
        print(f"\n--- {day} ---")

        elements = page.get_by_text(
            day,
            exact=False,
        )

        print("Count:", elements.count())

        for i in range(min(elements.count(), 5)):
            element = elements.nth(i)

            try:
                print(
                    f"\nElement {i}:"
                )

                print(
                    "Tag:",
                    element.evaluate("(el) => el.tagName"),
                )

                print(
                    "Text:",
                    element.inner_text().strip(),
                )

                print(
                    "HTML:",
                    element.evaluate(
                        "(el) => el.outerHTML"
                    )
                )

            except Exception as e:
                print("Error:", e)

    print("\nBrowser will remain open.")

    input()
