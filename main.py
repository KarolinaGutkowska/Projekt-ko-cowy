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

    mw_result = stats_engine.mann_whitney_test(
        clean_df,
        numeric_column="wynik",
        group_column="grupa"
    )

    print("\n=== TEST MANN–WHITNEY ===")
    print(mw_result)

    anova_result = stats_engine.anova_test(
        clean_df,
        numeric_column="wynik",
        group_column="grupa"
    )

    print("\n=== TEST ANOVA ===")
    print(anova_result)

    kruskal_result = stats_engine.kruskal_wallis_test(
        clean_df,
        numeric_column="wynik",
        group_column="grupa"
    )

    print("\n=== TEST KRUSKAL–WALLIS ===")
    print(kruskal_result)

    chi_result = stats_engine.chi_square_test(
        clean_df,
        column1="plec",
        column2="wynik_egzaminu"
    )

    print("\n=== TEST CHI-KWADRAT ===")
    print(chi_result)

    print("\n=== RAPORT STATYSTYCZNY ===")
    for line in stats_engine.report:
        print(line)


if __name__ == "__main__":
    main()