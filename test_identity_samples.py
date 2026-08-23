from adapters.resident_adapter import ResidentAdapter
from adapters.benefits_adapter import BenefitsAdapter
from services.identity_matcher import IdentityMatcher


def main():

    resident_adapter = ResidentAdapter()
    benefits_adapter = BenefitsAdapter()

    print("Fetching residents...")
    residents = resident_adapter.get_all_residents()

    print("Fetching benefits...")
    benefits = benefits_adapter.get_records()

    matcher = IdentityMatcher()

    count = 0

    print()
    print("================================")
    print("Sample Medium Matches")
    print("================================")

    for resident in residents:

        result = matcher.match(
            resident,
            benefits
        )

        if (
            result.get("status") == "matched"
            and
            result.get("confidence") == "medium"
        ):

            benefit = result.get("data")

            print()
            print("--------------------------------")
            print(
                f"Resident ID : "
                f"{resident.get('id')}"
            )

            print(
                f"Resident    : "
                f"{resident.get('first_name')} "
                f"{resident.get('last_name')}"
            )

            print(
                f"Resident DOB: "
                f"{resident.get('date_of_birth')}"
            )

            print(
                f"Resident Addr: "
                f"{resident.get('address_line')}"
            )

            print(
                f"Resident City: "
                f"{resident.get('city')}"
            )

            print()

            print(
                f"Benefits Ref : "
                f"{benefit.get('reference')}"
            )

            print(
                f"Benefits Name: "
                f"{benefit.get('name')}"
            )

            print(
                f"Benefits DOB : "
                f"{benefit.get('date_of_birth')}"
            )

            print(
                f"Benefits Addr: "
                f"{benefit.get('address')}"
            )

            print(
                f"Benefits Town: "
                f"{benefit.get('town')}"
            )

            print()

            print(
                f"Score        : "
                f"{result.get('score')}"
            )

            print(
                f"Matched      : "
                f"{', '.join(result.get('matched_fields', []))}"
            )

            count += 1

            if count >= 10:
                break

    print()
    print("--------------------------------")
    print(f"Displayed: {count}")


if __name__ == "__main__":
    main()