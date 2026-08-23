from adapters.benefits_adapter import BenefitsAdapter


def main():

    adapter = BenefitsAdapter()

    print("Fetching benefits records...")

    try:

        records = adapter.get_records()

        print()
        print("================================")
        print("Benefits Register Test")
        print("================================")

        print(f"Records received: {len(records)}")

        print()
        print("First 5 records:")

        for record in records[:5]:

            print(
                record["reference"],
                "-",
                record["name"]
            )

    except Exception as error:

        print()
        print("Benefits Register failed.")
        print(error)


if __name__ == "__main__":
    main()