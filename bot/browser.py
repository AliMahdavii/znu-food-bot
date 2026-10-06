from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL
import socket
import requests


class ZNUBrowser:
    """Manage the browser session for ZNU automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self) -> Page:
        """Start the browser and open the ZNU login page."""

        self.playwright = sync_playwright().start()

        launch_options = {
            "headless": self.headless,
        }

        if EDGE_PATH:
            launch_options["executable_path"] = EDGE_PATH

        self.browser = self.playwright.chromium.launch(
            **launch_options
        )

        self.page = self.browser.new_page()

        try:
            response = self.page.goto(
                ZNU_URL,
                wait_until="commit",
                timeout=60000,
            )

            print(
                "ZNU STATUS:",
                response.status if response else "NO RESPONSE"
            )

            print(
                "ZNU RESPONSE URL:",
                response.url if response else "NO RESPONSE"
            )

            print("ZNU PAGE URL:", self.page.url)

            self.page.wait_for_selector(
                "#username",
                state="visible",
                timeout=30000,
            )

            print("ZNU LOGIN FORM: READY")

        except Exception as exc:
            print("ZNU OPEN ERROR:", exc)
            print("CURRENT URL:", self.page.url)

            raise

        return self.page

    def login(self) -> bool:
        """Log in to the ZNU student system."""

        if self.page is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        return login(self.page)

    def open_reservation_page(self) -> None:
        """Open the food reservation page."""

        if self.page is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        self.page.goto(
            "https://student.znu.ac.ir/#!/Reservation",
            wait_until="commit",
            timeout=60000,
        )
        
        self.page.wait_for_timeout(3000)

    def go_to_next_week(self) -> None:
        """Navigate to the next reservation week."""

        if self.page is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        next_week = self.page.locator(
            'button[ng-click="browseWeek(startdate,7)"]'
        )

        if next_week.count() == 0:
            raise RuntimeError(
                "Next week button was not found."
            )

        next_week.click()
        self.page.wait_for_timeout(1500)

    def close(self) -> None:
        """Close the browser and Playwright."""

        if self.browser is not None:
            self.browser.close()

        if self.playwright is not None:
            self.playwright.stop()
