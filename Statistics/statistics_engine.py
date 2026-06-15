
import pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu, f_oneway, kruskal, chi2_contingency


class StatisticsEngine:

    def __init__(self):
        self.report = []

    #Statystyki opisowe
    def descriptive_statistics(self, df):
        numeric_df = df.select_dtypes(include="number")

        if numeric_df.empty:
            self.report.append("Brak kolumn liczbowych do analizy opisowej.")
            return None

        stats = numeric_df.describe().T

        self.report.append("Wygenerowano statystyki opisowe dla kolumn liczbowych.")

        return stats

    #Korelacje
    def correlations(self, df):
        numeric_df = df.select_dtypes(include="number")

        if numeric_df.shape[1] < 2:
            self.report.append("Za mało kolumn liczbowych do obliczenia korelacji.")
            return None

        correlation_matrix = numeric_df.corr(method="pearson")

        self.report.append("Obliczono macierz korelacji Pearsona.")

        return correlation_matrix

    #T-test
    def t_test(self, df, numeric_column, group_column):
        groups = df[group_column].dropna().unique()

        if len(groups) != 2:
            self.report.append(
                f"Test t wymaga dokładnie 2 grup w kolumnie '{group_column}'."
            )
            return None

        group1 = df[df[group_column] == groups[0]][numeric_column].dropna()
        group2 = df[df[group_column] == groups[1]][numeric_column].dropna()

        statistic, p_value = ttest_ind(group1, group2, equal_var=False)

        result = {
            "kolumna_liczbowa": numeric_column,
            "kolumna_grupująca": group_column,
            "grupa_1": groups[0],
            "grupa_2": groups[1],
            "statystyka_t": statistic,
            "p_value": p_value,
            "istotne_statystycznie": p_value < 0.05
        }

        self.report.append(
            f"Wykonano test t-Studenta dla '{numeric_column}' względem '{group_column}'."
        )

        return result

    #Test Mann–Whitney
    def mann_whitney_test(self, df, numeric_column, group_column):
        groups = df[group_column].dropna().unique()

        if len(groups) != 2:
            self.report.append(
                f"Test Mann–Whitney wymaga dokładnie 2 grup w kolumnie '{group_column}'."
            )
            return None

        group1 = df[df[group_column] == groups[0]][numeric_column].dropna()
        group2 = df[df[group_column] == groups[1]][numeric_column].dropna()

        statistic, p_value = mannwhitneyu(group1, group2, alternative="two-sided")

        result = {
            "test": "Mann–Whitney",
            "kolumna_liczbowa": numeric_column,
            "kolumna_grupująca": group_column,
            "grupa_1": groups[0],
            "grupa_2": groups[1],
            "statystyka_U": statistic,
            "p_value": p_value,
            "istotne_statystycznie": p_value < 0.05
        }

        self.report.append(
            f"Wykonano test Mann–Whitney dla '{numeric_column}' względem '{group_column}'."
        )

        return result

    def run(self, df):
        descriptive_stats = self.descriptive_statistics(df)
        correlation_matrix = self.correlations(df)

        return {
            "descriptive_statistics": descriptive_stats,
            "correlations": correlation_matrix
        }