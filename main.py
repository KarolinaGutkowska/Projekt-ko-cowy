from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine


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

    # ANALIZA STATYSTYCZNA
    stats_engine = StatisticsEngine()

    results = stats_engine.run(clean_df)

    print("\n=== STATYSTYKI OPISOWE ===")
    print(results["descriptive_statistics"])

    print("\n=== KORELACJE PEARSONA ===")
    print(results["correlations"])

    print("\n=== RAPORT STATYSTYCZNY ===")
    for line in stats_engine.report:
        print(line)


if __name__ == "__main__":
    main()