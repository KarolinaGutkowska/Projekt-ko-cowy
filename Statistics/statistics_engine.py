
import pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu, f_oneway, kruskal, chi2_contingency


class StatisticsEngine:

    def __init__(self):
        self.report = []

    #Automatyczne wykrywanie typu zmiennych
    def detect_variable_types(self, df):
        variable_types = {}

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                variable_types[column] = "liczbowa"
            else:
                variable_types[column] = "kategoryczna"

        self.report.append("Wykryto typy zmiennych w zbiorze danych.")

        return variable_types

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
            "istotne_statystycznie": p_value < 0.05,
            "interpretacja": self.interpret_p_value(p_value)
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
            "istotne_statystycznie": p_value < 0.05,
            "interpretacja": self.interpret_p_value(p_value)
        }

        self.report.append(
            f"Wykonano test Mann–Whitney dla '{numeric_column}' względem '{group_column}'."
        )

        return result

    #ANOVA
    def anova_test(self, df, numeric_column, group_column):
        groups = df[group_column].dropna().unique()

        if len(groups) < 3:
            self.report.append(
                f"ANOVA wymaga co najmniej 3 grup w kolumnie '{group_column}'."
            )
            return None

        data_groups = [
            df[df[group_column] == group][numeric_column].dropna()
            for group in groups
        ]

        statistic, p_value = f_oneway(*data_groups)

        result = {
            "test": "ANOVA",
            "kolumna_liczbowa": numeric_column,
            "kolumna_grupująca": group_column,
            "liczba_grup": len(groups),
            "grupy": list(groups),
            "statystyka_F": statistic,
            "p_value": p_value,
            "istotne_statystycznie": p_value < 0.05,
            "interpretacja": self.interpret_p_value(p_value)
        }

        self.report.append(
            f"Wykonano test ANOVA dla '{numeric_column}' względem '{group_column}'."
        )

        return result

    # Test Kruskal–Wallis
    def kruskal_wallis_test(self, df, numeric_column, group_column):
        groups = df[group_column].dropna().unique()

        if len(groups) < 3:
            self.report.append(
                f"Test Kruskal–Wallis wymaga co najmniej 3 grup w kolumnie '{group_column}'."
            )
            return None

        data_groups = [
            df[df[group_column] == group][numeric_column].dropna()
            for group in groups
        ]

        statistic, p_value = kruskal(*data_groups)

        result = {
            "test": "Kruskal–Wallis",
            "kolumna_liczbowa": numeric_column,
            "kolumna_grupująca": group_column,
            "liczba_grup": len(groups),
            "grupy": list(groups),
            "statystyka_H": statistic,
            "p_value": p_value,
            "istotne_statystycznie": p_value < 0.05,
            "interpretacja": self.interpret_p_value(p_value)
        }

        self.report.append(
            f"Wykonano test Kruskal–Wallis dla '{numeric_column}' względem '{group_column}'."
        )

        return result

    #Test chi-kwadrat
    def chi_square_test(self, df, column1, column2):
        contingency_table = pd.crosstab(
            df[column1],
            df[column2]
        )

        statistic, p_value, dof, expected = chi2_contingency(
            contingency_table
        )

        result = {
            "test": "Chi-Square",
            "kolumna_1": column1,
            "kolumna_2": column2,
            "chi2": statistic,
            "p_value": p_value,
            "degrees_of_freedom": dof,
            "istotne_statystycznie": p_value < 0.05,
            "interpretacja": self.interpret_p_value(p_value)
        }

        self.report.append(
            f"Wykonano test Chi-kwadrat dla '{column1}' i '{column2}'."
        )

        return result
    #automatyczna interpretacja p-value
    def interpret_p_value(self, p_value, alpha=0.05):
        if p_value < alpha:
            return (
                f"p = {p_value:.4f}. Wynik jest istotny statystycznie "
                f"(p < {alpha}). Odrzucamy hipotezę zerową."
            )
        else:
            return (
                f"p = {p_value:.4f}. Wynik nie jest istotny statystycznie "
                f"(p >= {alpha}). Brak podstaw do odrzucenia hipotezy zerowej."
            )


    #Zapisywanie raportu statystycznego
    def save_report(self, report_file, results):
        with open(report_file, "w", encoding="utf-8") as file:

            file.write("=== RAPORT STATYSTYCZNY ===\n\n")

            file.write("STATYSTYKI OPISOWE\n")
            file.write("-------------------\n")

            if results["descriptive_statistics"] is not None:
                file.write(
                    results["descriptive_statistics"].to_string()
                )
                file.write("\n\n")

            file.write("KORELACJE PEARSONA\n")
            file.write("-------------------\n")

            if results["correlations"] is not None:
                file.write(
                    results["correlations"].to_string()
                )
                file.write("\n\n")

            file.write("RAPORT SYSTEMOWY\n")
            file.write("-------------------\n")

            for line in self.report:
                file.write(line + "\n")

    def run(self, df, report_file=None):
        variable_types = self.detect_variable_types(df)
        descriptive_stats = self.descriptive_statistics(df)
        correlation_matrix = self.correlations(df)

        results = {
            "variable_types": variable_types,
            "descriptive_statistics": descriptive_stats,
            "correlations": correlation_matrix
        }

        if report_file:
            self.save_report(report_file, results)

        return results