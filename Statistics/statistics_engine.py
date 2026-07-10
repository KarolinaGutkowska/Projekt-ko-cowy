
import pandas as pd

from scipy.stats import (
    chi2_contingency,
    f_oneway,
    kruskal,
    levene,
    mannwhitneyu,
    shapiro,
    ttest_ind,
    wilcoxon,
    ttest_rel
)

from statsmodels.stats.oneway import anova_oneway

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

    def run_test(
            self,
            test_id,
            dataframe,
            independent_var,
            dependent_var
    ):
        if test_id == "chi_square":
            return self.chi_square_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "mann_whitney":
            return self.mann_whitney_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "t_independent":
            return self.t_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "welch_t":
            return self.welch_t_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "anova":
            return self.anova_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "welch_anova":
            return self.welch_anova_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "kruskal_wallis":
            return self.kruskal_wallis_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "wilcoxon":
            return self.wilcoxon_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "t_paired":
            return self.paired_t_test(
                dataframe,
                independent_var,
                dependent_var
            )
        if test_id == "mcnemar":
            return self.mcnemar_test(
                dataframe,
                independent_var,
                dependent_var
            )

        raise ValueError(
            f"Nieznany identyfikator testu: {test_id}"
        )

    def normality_test_by_groups(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna(
            subset=[
                grouping_variable,
                dependent_variable
            ]
        )

        grouped_data = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped_data) < 2:
            raise ValueError(
                "Do porównania wymagane są co najmniej dwie grupy."
            )

        groups_result = {}

        for group_name, group_df in grouped_data:
            values = group_df[dependent_variable].dropna()

            sample_size = len(values)

            if sample_size < 3:
                groups_result[str(group_name)] = {
                    "statistic": None,
                    "p_value": None,
                    "is_normal": False,
                    "sample_size": sample_size,
                    "error": (
                        "Za mało obserwacji do wykonania "
                        "testu Shapiro-Wilka."
                    ),
                }
                continue

            statistic, p_value = shapiro(values)

            groups_result[str(group_name)] = {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "is_normal": bool(p_value >= 0.05),
                "sample_size": int(sample_size),
                "error": None,
            }

        all_groups_normal = all(
            group_result["is_normal"]
            for group_result in groups_result.values()
        )

        result = {
            "test_id": "shapiro_wilk",
            "test": "Shapiro-Wilk",
            "grouping_variable": grouping_variable,
            "dependent_variable": dependent_variable,
            "number_of_groups": len(groups_result),
            "groups": groups_result,
            "all_groups_normal": bool(all_groups_normal),
            "alpha": 0.05,
        }

        self.report.append(
            f"Wykonano test Shapiro-Wilka w grupach dla "
            f"zmiennej '{dependent_variable}' względem "
            f"zmiennej grupującej '{grouping_variable}'."
        )

        return result

    #Test Mcnemar
    def mcnemar_test(
            self,
            dataframe,
            first_variable,
            second_variable,
    ):
        data = dataframe[
            [first_variable, second_variable]
        ].dropna().copy()

        if data.empty:
            raise ValueError(
                "Brak kompletnych par obserwacji."
            )

        first_values = data[first_variable].unique()
        second_values = data[second_variable].unique()

        all_values = list(
            pd.unique(
                pd.concat([
                    data[first_variable],
                    data[second_variable]
                ])
            )
        )

        if len(all_values) != 2:
            raise ValueError(
                "Test McNemara wymaga dwóch kategorii."
            )

        category_1 = all_values[0]
        category_2 = all_values[1]

        contingency_table = pd.crosstab(
            data[first_variable],
            data[second_variable]
        )

        contingency_table = contingency_table.reindex(
            index=[category_1, category_2],
            columns=[category_1, category_2],
            fill_value=0
        )

        result_test = mcnemar(
            contingency_table,
            exact=True
        )

        statistic = float(result_test.statistic)
        p_value = float(result_test.pvalue)

        result = {
            "test": "mcnemar",
            "pomiar_1": first_variable,
            "pomiar_2": second_variable,
            "kategoria_1": str(category_1),
            "kategoria_2": str(category_2),
            "liczba_par": int(len(data)),
            "tabela": contingency_table.values.tolist(),
            "statystyka": statistic,
            "p_value": p_value,
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test McNemara dla "
            f"'{first_variable}' i '{second_variable}'."
        )

        return result

    #Test normalności różnic
    def paired_differences_normality_test(
            self,
            dataframe,
            first_variable,
            second_variable,
    ):
        data = dataframe[
            [first_variable, second_variable]
        ].copy()

        data[first_variable] = pd.to_numeric(
            data[first_variable],
            errors="coerce"
        )

        data[second_variable] = pd.to_numeric(
            data[second_variable],
            errors="coerce"
        )

        data = data.dropna()

        if len(data) < 3:
            raise ValueError(
                "Test normalności różnic wymaga co najmniej "
                "trzech kompletnych par obserwacji."
            )

        differences = (
                data[first_variable] - data[second_variable]
        )

        statistic, p_value = shapiro(differences)

        result = {
            "test_id": "shapiro_paired_differences",
            "test": "Shapiro-Wilk",
            "first_variable": first_variable,
            "second_variable": second_variable,
            "sample_size": int(len(differences)),
            "statistic": float(statistic),
            "p_value": float(p_value),
            "is_normal": bool(p_value >= 0.05),
            "alpha": 0.05,
        }

        self.report.append(
            f"Wykonano test Shapiro-Wilka dla różnic między "
            f"'{first_variable}' i '{second_variable}'."
        )

        return result
    #Test t dla prób zależnych
    def paired_t_test(
            self,
            dataframe,
            first_variable,
            second_variable,
    ):
        data = dataframe[
            [first_variable, second_variable]
        ].copy()

        data[first_variable] = pd.to_numeric(
            data[first_variable],
            errors="coerce"
        )

        data[second_variable] = pd.to_numeric(
            data[second_variable],
            errors="coerce"
        )

        data = data.dropna()

        if len(data) < 2:
            raise ValueError(
                "Test t dla prób zależnych wymaga co najmniej "
                "dwóch kompletnych par obserwacji."
            )

        statistic, p_value = ttest_rel(
            data[first_variable],
            data[second_variable],
            nan_policy="omit",
        )

        result = {
            "test": "t_paired",
            "pomiar_1": first_variable,
            "pomiar_2": second_variable,
            "liczba_par": int(len(data)),
            "srednia_1": float(data[first_variable].mean()),
            "srednia_2": float(data[second_variable].mean()),
            "statystyka_t": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test t dla prób zależnych dla "
            f"'{first_variable}' i '{second_variable}'."
        )

        return result
    #Wilcoxon
    def wilcoxon_test(
            self,
            dataframe,
            first_variable,
            second_variable,
    ):
        data = dataframe[
            [first_variable, second_variable]
        ].copy()

        data[first_variable] = pd.to_numeric(
            data[first_variable],
            errors="coerce"
        )

        data[second_variable] = pd.to_numeric(
            data[second_variable],
            errors="coerce"
        )

        data = data.dropna()

        if len(data) < 2:
            raise ValueError(
                "Test Wilcoxona wymaga co najmniej dwóch "
                "kompletnych par obserwacji."
            )

        differences = (
                data[first_variable] - data[second_variable]
        )

        if (differences == 0).all():
            raise ValueError(
                "Wszystkie różnice między pomiarami wynoszą zero."
            )

        statistic, p_value = wilcoxon(
            data[first_variable],
            data[second_variable],
            alternative="two-sided",
        )

        result = {
            "test": "wilcoxon",
            "pomiar_1": first_variable,
            "pomiar_2": second_variable,
            "liczba_par": int(len(data)),
            "statystyka_W": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test Wilcoxona dla "
            f"'{first_variable}' i '{second_variable}'."
        )

        return result
    #ANOVA
    def welch_anova_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        grouped = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped) < 3:
            raise ValueError(
                "ANOVA Welcha wymaga co najmniej trzech grup."
            )

        group_names = []
        data_groups = []

        for group_name, group_df in grouped:
            values = group_df[dependent_variable].dropna()

            if len(values) < 2:
                raise ValueError(
                    f"Grupa „{group_name}” ma za mało obserwacji."
                )

            group_names.append(str(group_name))
            data_groups.append(values.to_numpy())

        welch_result = anova_oneway(
            data_groups,
            use_var="unequal",
            welch_correction=True,
        )

        statistic = float(welch_result.statistic)
        p_value = float(welch_result.pvalue)

        result = {
            "test": "welch_anova",
            "kolumna_liczbowa": dependent_variable,
            "kolumna_grupująca": grouping_variable,
            "liczba_grup": len(data_groups),
            "grupy": group_names,
            "statystyka_F": statistic,
            "p_value": p_value,
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano ANOVA Welcha dla "
            f"'{dependent_variable}' względem "
            f"'{grouping_variable}'."
        )

        return result
    #Jednorodność wariancji
    def levene_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        from scipy.stats import levene
        import pandas as pd

        data = dataframe[
            [grouping_variable, dependent_variable]
        ].dropna().copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        groups = [
            group[dependent_variable].to_numpy()
            for _, group in data.groupby(grouping_variable)
        ]

        if len(groups) < 2:
            raise ValueError(
                "Test Levene’a wymaga co najmniej dwóch grup."
            )

        statistic, p_value = levene(*groups)

        return {
            "test_id": "levene",
            "statistic": float(statistic),
            "p_value": float(p_value),
            "equal_variances": bool(p_value >= 0.05),
        }
    #Test t Welcha
    def welch_t_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        from scipy.stats import ttest_ind
        import pandas as pd

        data = dataframe[
            [grouping_variable, dependent_variable]
        ].dropna().copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )
        data = data.dropna()

        grouped = list(data.groupby(grouping_variable))

        if len(grouped) != 2:
            raise ValueError(
                "Test t Welcha wymaga dokładnie dwóch grup."
            )

        group_1_name, group_1_df = grouped[0]
        group_2_name, group_2_df = grouped[1]

        statistic, p_value = ttest_ind(
            group_1_df[dependent_variable],
            group_2_df[dependent_variable],
            equal_var=False,
            nan_policy="omit",
        )

        return {
            "grupa_1": str(group_1_name),
            "grupa_2": str(group_2_name),
            "statystyka_t": float(statistic),
            "p_value": float(p_value),
            "interpretacja": (
                "Stwierdzono istotne różnice między grupami."
                if p_value < 0.05
                else "Nie stwierdzono istotnych różnic między grupami."
            ),
        }
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
    def t_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        grouped = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped) != 2:
            raise ValueError(
                "Test t-Studenta wymaga dokładnie dwóch grup."
            )

        group_1_name, group_1_df = grouped[0]
        group_2_name, group_2_df = grouped[1]

        group_1 = group_1_df[dependent_variable]
        group_2 = group_2_df[dependent_variable]

        if len(group_1) < 2 or len(group_2) < 2:
            raise ValueError(
                "Każda grupa musi zawierać co najmniej "
                "dwie poprawne obserwacje."
            )

        statistic, p_value = ttest_ind(
            group_1,
            group_2,
            equal_var=True,
            nan_policy="omit",
        )

        result = {
            "test": "t_independent",
            "kolumna_liczbowa": dependent_variable,
            "kolumna_grupująca": grouping_variable,
            "grupa_1": str(group_1_name),
            "grupa_2": str(group_2_name),
            "statystyka_t": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test t-Studenta dla "
            f"'{dependent_variable}' względem "
            f"'{grouping_variable}'."
        )

        return result
    #Test Mann–Whitney
    def mann_whitney_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        grouped = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped) != 2:
            raise ValueError(
                "Test Manna-Whitneya wymaga dokładnie dwóch grup."
            )

        group_1_name, group_1_df = grouped[0]
        group_2_name, group_2_df = grouped[1]

        group_1 = group_1_df[dependent_variable]
        group_2 = group_2_df[dependent_variable]

        if group_1.empty or group_2.empty:
            raise ValueError(
                "Obie grupy muszą zawierać poprawne obserwacje."
            )

        statistic, p_value = mannwhitneyu(
            group_1,
            group_2,
            alternative="two-sided",
        )

        result = {
            "test": "mann_whitney",
            "kolumna_liczbowa": dependent_variable,
            "kolumna_grupująca": grouping_variable,
            "grupa_1": str(group_1_name),
            "grupa_2": str(group_2_name),
            "statystyka_U": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test Manna-Whitneya dla "
            f"'{dependent_variable}' względem "
            f"'{grouping_variable}'."
        )

        return result
    #ANOVA
    def anova_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        grouped = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped) < 3:
            raise ValueError(
                "ANOVA wymaga co najmniej trzech grup."
            )

        group_names = []
        data_groups = []

        for group_name, group_df in grouped:
            values = group_df[dependent_variable].dropna()

            if len(values) < 2:
                raise ValueError(
                    f"Grupa „{group_name}” ma za mało obserwacji."
                )

            group_names.append(str(group_name))
            data_groups.append(values.to_numpy())

        statistic, p_value = f_oneway(*data_groups)

        result = {
            "test": "anova",
            "kolumna_liczbowa": dependent_variable,
            "kolumna_grupująca": grouping_variable,
            "liczba_grup": len(data_groups),
            "grupy": group_names,
            "statystyka_F": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano ANOVA dla '{dependent_variable}' "
            f"względem '{grouping_variable}'."
        )

        return result

    # Test Kruskal–Wallis
    def kruskal_wallis_test(
            self,
            dataframe,
            grouping_variable,
            dependent_variable,
    ):
        data = dataframe[
            [grouping_variable, dependent_variable]
        ].copy()

        data[dependent_variable] = pd.to_numeric(
            data[dependent_variable],
            errors="coerce"
        )

        data = data.dropna()

        grouped = list(
            data.groupby(
                grouping_variable,
                sort=False
            )
        )

        if len(grouped) < 3:
            raise ValueError(
                "Test Kruskala-Wallisa wymaga "
                "co najmniej trzech grup."
            )

        group_names = []
        data_groups = []

        for group_name, group_df in grouped:
            values = group_df[dependent_variable].dropna()

            if values.empty:
                raise ValueError(
                    f"Grupa „{group_name}” nie zawiera "
                    "poprawnych obserwacji."
                )

            group_names.append(str(group_name))
            data_groups.append(values.to_numpy())

        statistic, p_value = kruskal(*data_groups)

        result = {
            "test": "kruskal_wallis",
            "kolumna_liczbowa": dependent_variable,
            "kolumna_grupująca": grouping_variable,
            "liczba_grup": len(data_groups),
            "grupy": group_names,
            "statystyka_H": float(statistic),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            f"Wykonano test Kruskala-Wallisa dla "
            f"'{dependent_variable}' względem "
            f"'{grouping_variable}'."
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

    def normality_test(self, df, numeric_column):
        data = pd.to_numeric(df[numeric_column], errors="coerce").dropna()

        if len(data) < 3:
            self.report.append(
                f"Za mało danych do testu normalności dla kolumny '{numeric_column}'."
            )
            return None

        statistic, p_value = shapiro(data)

        result = {
            "test": "Shapiro-Wilk",
            "kolumna": numeric_column,
            "statystyka_W": statistic,
            "p_value": p_value,
            "rozkład_normalny": p_value >= 0.05,
            "interpretacja": self.interpret_p_value_normality(p_value)
        }

        self.report.append(
            f"Wykonano test Shapiro-Wilka dla kolumny '{numeric_column}'."
        )

        return result

    def interpret_p_value_normality(self, p_value, alpha=0.05):
        if p_value >= alpha:
            return (
                f"p = {p_value:.4f}. Brak podstaw do odrzucenia hipotezy "
                f"o rozkładzie normalnym."
            )
        else:
            return (
                f"p = {p_value:.4f}. Wynik sugeruje, że rozkład różni się "
                f"od normalnego."
            )

    def descriptive_statistics_selected(self, df, columns):
        results = []

        for column in columns:
            data = pd.to_numeric(df[column], errors="coerce").dropna()
            n = len(data)

            if n == 0:
                continue

            results.append({
                "Zmienna": column,
                "N": n,
                "Średnia": round(data.mean(), 4),
                "Mediana": round(data.median(), 4),
                "Odchylenie standardowe": round(data.std(ddof=1), 4)
            })

        return pd.DataFrame(results)


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

    #statystyi dla zmiennych jakościowych
    def qualitative_statistics_selected(self, df, columns):
        results = []

        for column in columns:
            data = df[column].dropna()
            total = len(data)

            if total == 0:
                continue

            counts = data.value_counts()
            mode_value = data.mode().iloc[0] if not data.mode().empty else None

            for category, count in counts.items():
                percent = (count / total) * 100

                results.append({
                    "Zmienna": column,
                    "Kategoria": category,
                    "Liczebność": count,
                    "Udział procentowy": round(percent, 2),
                    "Dominanta": mode_value
                })

        return pd.DataFrame(results)