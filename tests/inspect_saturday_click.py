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

        print("Next week button count:", next_week.count())

        next_week.click()

        page.wait_for_timeout(2000)

        saturday_candidates = page.get_by_text(
            "شنبه",
            exact=False,
        )

        print("\n=== SATURDAY CANDIDATES ===")
        print("Count:", saturday_candidates.count())

        saturday = None

        for i in range(saturday_candidates.count()):
            candidate = saturday_candidates.nth(i)

            try:
                if candidate.is_visible():
                    saturday = candidate
                    print("Visible Saturday index:", i)
                    break
            except Exception:
                continue

        if saturday is None:
            print("❌ No visible Saturday found.")
            browser.close()
            return

        print("\n=== SATURDAY ELEMENT ===")

        print("Count:", page.get_by_text(
            "شنبه",
            exact=False,
        ).count())

        print("TAG:", saturday.evaluate("(el) => el.tagName"))
        print("TEXT:", repr(saturday.inner_text()))
        print("ID:", saturday.get_attribute("id"))
        print("CLASS:", saturday.get_attribute("class"))
        print("NG-CLICK:", saturday.get_attribute("ng-click"))
        print("NG-IF:", saturday.get_attribute("ng-if"))
        print("NG-REPEAT:", saturday.get_attribute("ng-repeat"))
        print("HREF:", saturday.get_attribute("href"))
        print("ONCLICK:", saturday.get_attribute("onclick"))

        parent = saturday.locator("xpath=..")

        print("\n=== SATURDAY PARENT ===")

        print("TAG:", parent.evaluate("(el) => el.tagName"))
        print("TEXT:", repr(parent.inner_text()))
        print("ID:", parent.get_attribute("id"))
        print("CLASS:", parent.get_attribute("class"))
        print("NG-CLICK:", parent.get_attribute("ng-click"))
        print("NG-IF:", parent.get_attribute("ng-if"))
        print("NG-REPEAT:", parent.get_attribute("ng-repeat"))

        print("\n=== CLICKING SATURDAY ===")

        saturday.click()

        page.wait_for_timeout(2000)

        print("Saturday clicked.")

        print("\n=== AFTER CLICK ===")

        print("URL:", page.url)

        print("\n=== BODY TEXT ===")

        body_text = page.locator("body").inner_text()

        print(body_text)

        html = page.content()

        with open(
            "tests/saturday_after_click.html",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(html)

        print("\nHTML saved to:")
        print("tests/saturday_after_click.html")

        print("\nBrowser will remain open.")

        page.wait_for_timeout(15000)

        browser.close()


if __name__ == "__main__":
    main()
