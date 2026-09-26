from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )

    page = browser.new_page()

    page.goto("https://food.znu.ac.ir/", wait_until="domcontentloaded")

    print("Title:", page.title())
    print("URL:", page.url)

    page.wait_for_timeout(10000)

    browser.close()