from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Locator, Page


LUNCH_MEAL_INDEX = 1

ADD_FOOD_SELECTOR = (
    'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
)

FOOD_SELECT_SELECTOR = (
    'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
)

SELF_SELECT_SELECTOR = (
    'select[ng-model="selectitem[dayindex].peek[mealindex].selectedSelf"]'
)

CONFIRM_BUTTON_SELECTOR = (
    'button[ng-click="FinallReserve(dayindex,mealindex)"]'
)

RESULT_TOAST_SELECTOR = (
    '.toast:has(.toast-title:text("نتیجه ارسال درخواست"))'
)

DAYS = [
    ("شنبه", 0),
    ("یکشنبه", 1),
    ("دوشنبه", 2),
    ("سه شنبه", 3),
    ("چهارشنبه", 4),
]


@dataclass
class ReservationResult:
    day: str
    food: Optional[str]
    price: Optional[int]
    success: bool
    message: str


def create_result(
    day: str,
    food: Optional[str],
    price: Optional[int],
    message: str,
    success: bool = False,
) -> ReservationResult:
    """Create a reservation result."""

    return ReservationResult(
        day=day,
        food=food,
        price=price,
        success=success,
        message=message,
    )


def activate_day_tab(page: Page, dayindex: int) -> None:
    """Activate the reservation tab for a specific day."""

    if dayindex == 0:
        return

    tab = page.locator(
        f'label[href="#tab_day{dayindex}"]'
    )

    if tab.count() == 0:
        raise RuntimeError(
            f"Day tab not found for dayindex={dayindex}"
        )

    tab.click()
    page.wait_for_timeout(500)


def parse_food_price(food_name: str) -> Optional[int]:
    """Extract the price from a food option text."""

    try:
        price_text = food_name.split("[", 1)[1].split("ریال", 1)[0]
        return int(price_text.replace("]", "").strip())
    except (IndexError, ValueError):
        return None


def get_first_food(
    food_select: Locator,
) -> tuple[Optional[str], Optional[str], Optional[int]]:
    """Return the first available food from the food selector."""

    options = food_select.locator("option")

    # The first option is the empty placeholder.
    if options.count() < 2:
        return None, None, None

    food_option = options.nth(1)

    food_name = food_option.inner_text().strip()
    food_value = food_option.get_attribute("value")

    if not food_value:
        return food_name, None, parse_food_price(food_name)

    return (
        food_name,
        food_value,
        parse_food_price(food_name),
    )


def get_day_container(
    page: Page,
    dayindex: int,
) -> tuple[Locator, Locator]:
    """Return the add-food button and its parent container."""

    add_button = page.locator(
        ADD_FOOD_SELECTOR
    ).nth(dayindex)

    container = add_button.locator("..")

    return add_button, container


def get_reservation_result(
    page: Page,
    day: str,
    food: Optional[str],
    price: Optional[int],
) -> ReservationResult:
    """Read the reservation result from the website toast."""

    toast = page.locator(
        RESULT_TOAST_SELECTOR
    ).last

    try:
        toast.wait_for(
            state="visible",
            timeout=5000,
        )
    except Exception:
        return create_result(
            day=day,
            food=food,
            price=price,
            message="Reservation result was not detected.",
        )

    message = toast.locator(
        ".toast-message"
    ).inner_text().strip()

    message = message.lstrip(":").strip()

    toast_class = toast.get_attribute("class") or ""

    if "toast-warning" in toast_class or "toast-error" in toast_class:
        return create_result(
            day=day,
            food=food,
            price=price,
            message=message,
        )

    return create_result(
        day=day,
        food=food,
        price=price,
        success=True,
        message=message or "Reservation completed successfully.",
    )


def reserve_day(
    page: Page,
    dayindex: int,
    day_name: str,
) -> ReservationResult:
    """Reserve the first available lunch food for one day.

    ```
    dayindex:
        0 = Saturday
        1 = Sunday
        2 = Monday
        3 = Tuesday
        4 = Wednesday
    """

    activate_day_tab(page, dayindex)

    add_button, container = get_day_container(
        page,
        dayindex,
    )

    food_select = container.locator(
        FOOD_SELECT_SELECTOR
    )

    food_name, food_value, price = get_first_food(
        food_select
    )

    if food_name is None:
        return create_result(
            day=day_name,
            food=None,
            price=None,
            message="No available food found.",
        )

    if food_value is None:
        return create_result(
            day=day_name,
            food=food_name,
            price=price,
            message="Food value was not found.",
        )

    print(f"\n=== {day_name} ===")
    print(f"Food: {food_name}")
    print(f"Value: {food_value}")

    # Select the first available food.
    food_select.select_option(food_value)

    page.wait_for_timeout(1000)

    # The website automatically selects the self.
    self_select = container.locator(
        SELF_SELECT_SELECTOR
    )

    print("Self:", self_select.input_value())

    # Add food to cart.
    if add_button.is_disabled():
        return create_result(
            day=day_name,
            food=food_name,
            price=price,
            message="AddFood button is disabled.",
        )

    add_button.click()

    page.wait_for_timeout(1000)

    # Find the final reservation button.
    confirm_button = page.locator(
        CONFIRM_BUTTON_SELECTOR
    ).nth(dayindex)

    if not confirm_button.is_enabled():
        return create_result(
            day=day_name,
            food=food_name,
            price=price,
            message="Final reservation button is disabled.",
        )

    print("Confirming reservation...")

    confirm_button.click()

    page.wait_for_timeout(1500)

    return get_reservation_result(
        page=page,
        day=day_name,
        food=food_name,
        price=price,
    )


def reserve_week(page: Page) -> list[ReservationResult]:
    """Reserve lunch from Saturday through Wednesday."""

    results = []

    for day_name, dayindex in DAYS:
        result = reserve_day(
            page=page,
            dayindex=dayindex,
            day_name=day_name,
        )

        results.append(result)

    return results
