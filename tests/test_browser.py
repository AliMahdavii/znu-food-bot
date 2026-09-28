from bot.browser import ZNUBrowser


browser = ZNUBrowser(headless=False)

try:
    print("Starting browser...")
    browser.start()

    print("Logging in...")
    print("Login:", browser.login())

    print("Opening reservation page...")
    browser.open_reservation_page()

    print("Browser flow completed successfully.")

    input("\nPress Enter to close browser...")

finally:
    browser.close()
