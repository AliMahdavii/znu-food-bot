from bot.service import reserve_next_week


print("Starting reservation service...")

results = reserve_next_week(
    headless=False,
)

print("\n" + "=" * 50)
print("SERVICE RESULT")
print("=" * 50)

for result in results:
    print(
        f"\n{result.day}"
        f"\n  Food: {result.food}"
        f"\n  Price: {result.price}"
        f"\n  Success: {result.success}"
        f"\n  Message: {result.message}"
    )

print("\n" + "=" * 50)
print("SERVICE TEST COMPLETED")
print("=" * 50)
