from playwright.sync_api import Page

from config.settings import ZNU_PASSWORD, ZNU_USERNAME


LOGIN_URL = "https://student.znu.ac.ir/identity/login"


def login(page: Page) -> bool:
    """Log in to the ZNU food system."""

    if not ZNU_USERNAME or not ZNU_PASSWORD:
        raise ValueError(
            "ZNU_USERNAME or ZNU_PASSWORD is not configured."
        )

    page.locator("#username").fill(ZNU_USERNAME)
    page.locator("#password").fill(ZNU_PASSWORD)

    page.get_by_role("button", name="ورود").click(
        no_wait_after=True
    )

    page.wait_for_timeout(3000)

    return page.url != LOGIN_URL
