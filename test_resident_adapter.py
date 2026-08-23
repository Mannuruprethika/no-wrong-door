from adapters.resident_adapter import ResidentAdapter


def main():

    adapter = ResidentAdapter()

    print("Fetching residents...")

    residents = adapter.get_all_residents()

    print()
    print("================================")
    print("Resident Index Test")
    print("================================")

    print(f"Unique residents: {len(residents)}")

    print()
    print("First 5 residents:")

    for resident in residents[:5]:
        print(
            resident["id"],
            "-",
            resident["first_name"],
            resident["last_name"]
        )


if __name__ == "__main__":
    main()