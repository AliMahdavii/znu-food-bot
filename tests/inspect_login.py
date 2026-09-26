from playwright.sync_api import sync_playwright


EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "https://food.znu.ac.ir/"


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=EDGE_PATH
    )

    page = browser.new_page()

    page.goto(URL, wait_until="domcontentloaded")

    print("\n=== PAGE INFO ===")
    print("Title:", page.title())
    print("URL:", page.url)

    print("\n=== INPUTS ===")

    inputs = page.locator("input")

    for i in range(inputs.count()):
        element = inputs.nth(i)

        print(f"\nInput #{i}")
        print("  type :", element.get_attribute("type"))
        print("  name :", element.get_attribute("name"))
        print("  id   :", element.get_attribute("id"))
        print("  placeholder:", element.get_attribute("placeholder"))

    print("\n=== BUTTONS ===")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        button = buttons.nth(i)

        print(f"\nButton #{i}")
        print("  text:", button.inner_text())
        print("  type:", button.get_attribute("type"))
        print("  id  :", button.get_attribute("id"))
        print("  name:", button.get_attribute("name"))

    page.screenshot(
        path="tests/login-page.png",
        full_page=True
    )

    print("\nScreenshot saved to: tests/login-page.png")

    input("\nPress ENTER to close the browser...")

    browser.close()