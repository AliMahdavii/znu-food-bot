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

    print("\n=== BOX DETAILS ===")

    for box_id in ["box1", "box2", "box3", "box4"]:
        box = page.locator(f"#{box_id}")

        print(f"\n--- {box_id} ---")

        print("outerHTML:")
        print(box.evaluate("(el) => el.outerHTML"))

        print("\nparent HTML:")
        print(
            box.evaluate(
                "(el) => el.parentElement.outerHTML"
            )
        )

    print("\n=== LABELS ===")

    labels = page.locator("label")

    for i in range(labels.count()):
        label = labels.nth(i)

        print(
            f"Label #{i}:",
            repr(label.inner_text()),
            "| for:",
            label.get_attribute("for")
        )

    print("\n=== TEXT INPUTS ===")

    inputs = page.locator("input")

    for i in range(inputs.count()):
        element = inputs.nth(i)

        print(
            f"Input #{i}:",
            element.evaluate(
                "(el) => el.outerHTML"
            )
        )

    input("\nPress ENTER to close...")

    browser.close()
