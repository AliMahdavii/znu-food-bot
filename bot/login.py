from playwright.sync_api import Page


LOGIN_URL = "https://student.znu.ac.ir/identity/login"


def login(page: Page, username: str, password: str) -> bool:
    """Log in to the ZNU student system."""

    if not username or not password:
        raise ValueError("Account credentials are missing.")

    page.locator("#username").fill(username)
    page.locator("#password").fill(password)

    page.get_by_role(
        "button",
        name="ورود",
        exact=True,
    ).click(no_wait_after=True)

    page.wait_for_timeout(3000)

    return page.url != LOGIN_URL
