from services.unified_service import UnifiedResidentService


def main():

    service = UnifiedResidentService()

    print("Fetching unified data...")

    result = service.get_unified_data()

    print()
    print("================================")
    print("Unified Service Test")
    print("================================")

    resident_source = result["resident_index"]
    benefits_source = result["benefits_register"]

    print()
    print("Resident Index:")
    print(f"Status : {resident_source['status']}")
    print(f"Count  : {resident_source['count']}")

    print()
    print("Benefits Register:")
    print(f"Status : {benefits_source['status']}")
    print(f"Count  : {benefits_source['count']}")

    if "reason" in resident_source:
        print(f"Reason : {resident_source['reason']}")

    if "reason" in benefits_source:
        print(f"Reason : {benefits_source['reason']}")


if __name__ == "__main__":
    main()