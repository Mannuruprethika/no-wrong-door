from adapters.resident_adapter import ResidentAdapter
from adapters.benefits_adapter import BenefitsAdapter
from services.identity_matcher import IdentityMatcher


def main():

    print("Fetching Resident Index...")

    resident_adapter = ResidentAdapter()

    residents = (
        resident_adapter
        .get_all_residents()
    )

    print(
        f"Residents received: {len(residents)}"
    )

    print()
    print("Fetching Benefits Register...")

    benefits_adapter = BenefitsAdapter()

    benefits = (
        benefits_adapter
        .get_records()
    )

    print(
        f"Benefits records received: {len(benefits)}"
    )

    print()

    matcher = IdentityMatcher()

    high_confidence = []
    medium_confidence = []
    ambiguous = []
    unmatched = []

    print("Running identity matching...")

    for resident in residents:

        result = matcher.match(
            resident,
            benefits
        )

        status = result.get("status")

        if (
            status == "matched"
            and
            result.get("confidence")
            == "high"
        ):

            high_confidence.append(
                (resident, result)
            )

        elif (
            status == "matched"
            and
            result.get("confidence")
            == "medium"
        ):

            medium_confidence.append(
                (resident, result)
            )

        elif status == "ambiguous":

            ambiguous.append(
                (resident, result)
            )

        else:

            unmatched.append(
                (resident, result)
            )

    # ========================================================
    # Summary
    # ========================================================

    print()
    print("================================")
    print("Identity Matching Results")
    print("================================")

    print(
        f"Residents checked : {len(residents)}"
    )

    print(
        f"Benefits checked  : {len(benefits)}"
    )

    print(
        f"High confidence   : {len(high_confidence)}"
    )

    print(
        f"Medium confidence : {len(medium_confidence)}"
    )

    print(
        f"Ambiguous         : {len(ambiguous)}"
    )

    print(
        f"Unmatched         : {len(unmatched)}"
    )

    # ========================================================
    # Show sample matches
    # ========================================================

    print()
    print("================================")
    print("Sample High Confidence Matches")
    print("================================")

    for resident, result in high_confidence[:10]:

        benefit = result["data"]

        print()
        print(
            f"Resident : "
            f"{resident.get('first_name')} "
            f"{resident.get('last_name')}"
        )

        print(
            f"Resident ID : "
            f"{resident.get('id')}"
        )

        print(
            f"Benefits Ref : "
            f"{benefit.get('reference')}"
        )

        print(
            f"Benefits Name : "
            f"{benefit.get('name')}"
        )

        print(
            f"Score : "
            f"{result.get('score')}"
        )

        print(
            f"Fields : "
            f"{', '.join(result.get('matched_fields', []))}"
        )


if __name__ == "__main__":

    main()