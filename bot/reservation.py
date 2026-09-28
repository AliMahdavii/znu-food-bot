from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Page


@dataclass
class ReservationResult:
    day: str
    food: Optional[str]
    price: Optional[int]
    success: bool
    message: str


def activate_day_tab(page: Page, dayindex: int) -> None:
    """Activate the tab for the selected day."""

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
        price_text = food_name.split("[")[1].split("ریال")[0]
        return int(price_text.replace("]", "").strip())
    except (IndexError, ValueError):
        return None


def get_first_food(
    food_select,
) -> tuple[Optional[str], Optional[str], Optional[int]]:
    """Return the first available food from the food selector."""

    options = food_select.locator("option")

    # Option 0 is the empty placeholder.
    if options.count() < 2:
        return None, None, None

    food_option = options.nth(1)

    food_name = food_option.inner_text().strip()
    food_value = food_option.get_attribute("value")

    if not food_value:
        return food_name, None, None

    price = parse_food_price(food_name)

    return food_name, food_value, price


def get_reservation_result(
    page: Page,
    day: str,
    food: Optional[str],
    price: Optional[int],
) -> ReservationResult:
    """Read and convert the reservation result toast."""

    toast = page.locator(
        '.toast:has(.toast-title:text("نتیجه ارسال درخواست"))'
    ).last

    try:
        toast.wait_for(
            state="visible",
            timeout=5000,
        )
    except Exception:
        return ReservationResult(
            day=day,
            food=food,
            price=price,
            success=False,
            message="Reservation result was not detected.",
        )

    message = toast.locator(
        ".toast-message"
    ).inner_text().strip()

    message = message.lstrip(":").strip()

    toast_class = toast.get_attribute("class") or ""

    if "toast-warning" in toast_class or "toast-error" in toast_class:
        return ReservationResult(
            day=day,
            food=food,
            price=price,
            success=False,
            message=message,
        )

    return ReservationResult(
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
    """
    Reserve the first available lunch food for one day.

    dayindex:
        0 = Saturday
        1 = Sunday
        2 = Monday
        3 = Tuesday
        4 = Wednesday
    """

    mealindex = 1  # Lunch

    activate_day_tab(page, dayindex)

    add_button = page.locator(
        'button[ng-click="AddFood(dayindex,mealindex,mealitm)"]'
    ).nth(dayindex)

    container = add_button.locator("..")

    food_select = container.locator(
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedFood"]'
    )

    food_name, food_value, price = get_first_food(food_select)

    if food_name is None:
        return ReservationResult(
            day=day_name,
            food=None,
            price=None,
            success=False,
            message="No available food found.",
        )

    if food_value is None:
        return ReservationResult(
            day=day_name,
            food=food_name,
            price=price,
            success=False,
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
        'select[ng-model="selectitem[dayindex].peek[mealindex].selectedSelf"]'
    )

    print("Self:", self_select.input_value())

    # Add food to cart.
    if add_button.is_disabled():
        return ReservationResult(
            day=day_name,
            food=food_name,
            price=price,
            success=False,
            message="AddFood button is disabled.",
        )

    add_button.click()

    page.wait_for_timeout(1000)

    # Final reservation button.
    confirm_button = page.locator(
        'button[ng-click="FinallReserve(dayindex,mealindex)"]'
    ).nth(dayindex)

    if not confirm_button.is_enabled():
        return ReservationResult(
            day=day_name,
            food=food_name,
            price=price,
            success=False,
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

    days = [
        ("شنبه", 0),
        ("یکشنبه", 1),
        ("دوشنبه", 2),
        ("سه شنبه", 3),
        ("چهارشنبه", 4),
    ]

    results = []

    for day_name, dayindex in days:
        result = reserve_day(
            page=page,
            dayindex=dayindex,
            day_name=day_name,
        )

        results.append(result)

    return results
