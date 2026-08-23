from adapters.benefits_adapter import BenefitsAdapter


def main():

    adapter = BenefitsAdapter()

    print("Fetching Benefits Register...")

    try:

        records = adapter.get_records()

        print()
        print("================================")
        print("Benefits Register Sample")
        print("================================")

        print(f"Total records: {len(records)}")

        print()
        print("First 10 records:")
        print()

        for record in records[:10]:

            print("--------------------------------")
            print(f"Reference   : {record.get('reference')}")
            print(f"Name        : {record.get('name')}")
            print(f"Date of Birth: {record.get('date_of_birth')}")
            print(f"Address     : {record.get('address')}")
            print(f"Town        : {record.get('town')}")
            print(f"Benefit Code: {record.get('benefit_code')}")
            print(f"Review Due  : {record.get('review_due')}")

    except Exception as error:

        print()
        print("Benefits Register failed.")
        print(error)


if __name__ == "__main__":
    main()