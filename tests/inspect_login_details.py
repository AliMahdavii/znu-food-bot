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

    print("\n=== PAGE ===")
    print("Title:", page.title())
    print("URL:", page.url)

    print("\n=== FORMS ===")

    forms = page.locator("form")

    for i in range(forms.count()):
        form = forms.nth(i)

        print(f"\nForm #{i}")
        print("  action:", form.get_attribute("action"))
        print("  method:", form.get_attribute("method"))
        print("  id:", form.get_attribute("id"))
        print("  class:", form.get_attribute("class"))

    print("\n=== CAPTCHA / BOX INPUTS ===")

    for box_id in ["box1", "box2", "box3", "box4"]:
        box = page.locator(f"#{box_id}")

        print(f"\n{box_id}")
        print("  type:", box.get_attribute("type"))
        print("  name:", box.get_attribute("name"))
        print("  value:", box.input_value())
        print("  maxlength:", box.get_attribute("maxlength"))
        print("  class:", box.get_attribute("class"))
        print("  readonly:", box.get_attribute("readonly"))
        print("  disabled:", box.is_disabled())

    print("\n=== IMAGES ===")

    images = page.locator("img")

    for i in range(images.count()):
        image = images.nth(i)

        print(f"\nImage #{i}")
        print("  src:", image.get_attribute("src"))
        print("  alt:", image.get_attribute("alt"))
        print("  id:", image.get_attribute("id"))
        print("  class:", image.get_attribute("class"))

    print("\n=== TEXT AROUND LOGIN ===")

    body_text = page.locator("body").inner_text()

    print(body_text[:5000])

    input("\nPress ENTER to close the browser...")

    browser.close()