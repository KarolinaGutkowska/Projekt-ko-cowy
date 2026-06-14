from HUBA.huba import HUBA


def main():
    huba = HUBA()

    clean_df = huba.run(
        "dane.xlsx",
        "dane_clean.xlsx",
        "huba_report.txt"
    )

    print(clean_df.head())

    print("\n=== RAPORT HUBA ===")
    for line in huba.report:
        print(line)


if __name__ == "__main__":
    main()