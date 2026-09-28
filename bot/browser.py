from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from bot.login import login
from config.settings import EDGE_PATH, ZNU_URL


class ZNUBrowser:
    """Manage the browser session for ZNU automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self) -> Page:
        """Start the browser and open the ZNU website."""

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            executable_path=EDGE_PATH,
        )

        self.page = self.browser.new_page()

        self.page.goto(
            ZNU_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

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
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.page.wait_for_timeout(2000)

    def close(self) -> None:
        """Close the browser and Playwright."""

        if self.browser is not None:
            self.browser.close()

        if self.playwright is not None:
            self.playwright.stop()
