
import pandas as pd
import pingouin as pg

from scipy.stats import (
    chi2_contingency,
    f_oneway,
    kruskal,
    levene,
    mannwhitneyu,
    shapiro,
    ttest_ind,
    wilcoxon,
    ttest_rel,
    friedmanchisquare
)
from statsmodels.stats.contingency_tables import (
    cochrans_q,
    mcnemar,
)
from statsmodels.stats.oneway import anova_oneway
from scipy.stats import pearsonr, spearmanr

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
            independent_var=None,
            dependent_var=None,
            variables=None,
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

        if test_id == "friedman":
            return self.friedman_test(
                dataframe,
                variables
            )

        if test_id == "cochran_q":
            return self.cochran_q_test(
                dataframe,
                variables
            )

        if test_id == "repeated_measures_anova":
            return self.repeated_measures_anova_test(
                dataframe,
                variables
            )

        if test_id == "pearson":
            return self.pearson_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "spearman":
            return self.spearman_test(
                dataframe,
                independent_var,
                dependent_var
            )

        if test_id == "chi_square_relationship":
            return self.chi_square_relationship_test(
                dataframe,
                independent_var,
                dependent_var
            )

        raise ValueError(
            f"Nieznany identyfikator testu: {test_id}"
        )

    #Pearson
    def pearson_test(
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
                "Korelacja Pearsona wymaga co najmniej "
                "trzech kompletnych par obserwacji."
            )

        coefficient, p_value = pearsonr(
            data[first_variable],
            data[second_variable]
        )

        return {
            "test": "pearson",
            "zmienna_1": first_variable,
            "zmienna_2": second_variable,
            "liczba_par": int(len(data)),
            "wspolczynnik": float(coefficient),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

    #Spearman
    def spearman_test(
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
                "Korelacja Spearmana wymaga co najmniej "
                "trzech kompletnych par obserwacji."
            )

        coefficient, p_value = spearmanr(
            data[first_variable],
            data[second_variable]
        )

        return {
            "test": "spearman",
            "zmienna_1": first_variable,
            "zmienna_2": second_variable,
            "liczba_par": int(len(data)),
            "wspolczynnik": float(coefficient),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

    #V Cramera
    def chi_square_relationship_test(
            self,
            dataframe,
            first_variable,
            second_variable,
    ):
        contingency_table = pd.crosstab(
            dataframe[first_variable],
            dataframe[second_variable]
        )

        if contingency_table.empty:
            raise ValueError(
                "Nie udało się utworzyć tabeli kontyngencji."
            )

        chi2, p_value, dof, expected = chi2_contingency(
            contingency_table
        )

        sample_size = int(contingency_table.to_numpy().sum())

        min_dimension = min(
            contingency_table.shape[0] - 1,
            contingency_table.shape[1] - 1,
        )

        if min_dimension <= 0:
            cramers_v = 0.0
        else:
            cramers_v = (
                                chi2 / (sample_size * min_dimension)
                        ) ** 0.5

        return {
            "test": "chi_square_relationship",
            "zmienna_1": first_variable,
            "zmienna_2": second_variable,
            "chi2": float(chi2),
            "degrees_of_freedom": int(dof),
            "p_value": float(p_value),
            "cramers_v": float(cramers_v),
            "liczba_obserwacji": sample_size,
            "interpretacja": self.interpret_p_value(p_value),
        }

    #Sprawdzanie rozkładu normalnego dla wielu pomiarów
    def repeated_measures_normality_test(
            self,
            dataframe,
            variables,
    ):
        if not isinstance(variables, (list, tuple)):
            raise TypeError(
                "Pomiary muszą zostać przekazane jako lista lub krotka."
            )

        if len(variables) < 3:
            raise ValueError(
                "Analiza wymaga co najmniej trzech pomiarów."
            )

        missing_columns = [
            variable
            for variable in variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        data = dataframe[list(variables)].copy()

        for variable in variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 3:
            raise ValueError(
                "Test normalności wymaga co najmniej trzech "
                "kompletnych zestawów obserwacji."
            )

        values = data.to_numpy(dtype=float)

        grand_mean = values.mean()
        subject_means = values.mean(axis=1, keepdims=True)
        measurement_means = values.mean(axis=0, keepdims=True)

        residuals = (
                values
                - subject_means
                - measurement_means
                + grand_mean
        ).ravel()

        if len(set(residuals)) < 2:
            raise ValueError(
                "Nie można sprawdzić normalności, ponieważ "
                "wszystkie reszty mają taką samą wartość."
            )

        statistic, p_value = shapiro(residuals)

        result = {
            "test_id": "repeated_measures_normality",
            "test": "Shapiro-Wilk",
            "pomiary": list(variables),
            "liczba_pomiarow": int(len(variables)),
            "liczba_kompletnych_przypadkow": int(len(data)),
            "statystyka_W": float(statistic),
            "p_value": float(p_value),
            "is_normal": bool(p_value >= 0.05),
            "alpha": 0.05,
        }

        self.report.append(
            "Wykonano test normalności reszt dla pomiarów: "
            + ", ".join(variables)
            + "."
        )

        return result

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

    #Test Cochran
    def cochran_q_test(
            self,
            dataframe,
            variables,
    ):
        if not isinstance(variables, (list, tuple)):
            raise TypeError(
                "Lista pomiarów testu Q Cochrana musi być listą lub krotką."
            )

        if len(variables) < 3:
            raise ValueError(
                "Test Q Cochrana wymaga co najmniej trzech pomiarów."
            )

        missing_columns = [
            variable
            for variable in variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        data = dataframe[list(variables)].copy()
        data = data.dropna()

        if len(data) < 2:
            raise ValueError(
                "Test Q Cochrana wymaga co najmniej dwóch "
                "kompletnych zestawów obserwacji."
            )

        unique_values = pd.unique(data.to_numpy().ravel())

        if len(unique_values) != 2:
            raise ValueError(
                "Test Q Cochrana wymaga danych binarnych, "
                "czyli dokładnie dwóch kategorii."
            )

        category_0 = unique_values[0]
        category_1 = unique_values[1]

        binary_data = data.replace({
            category_0: 0,
            category_1: 1,
        }).astype(int)

        test_result = cochrans_q(
            binary_data.to_numpy()
        )

        statistic = float(test_result.statistic)
        p_value = float(test_result.pvalue)

        result = {
            "test": "cochran_q",
            "pomiary": list(variables),
            "liczba_pomiarow": int(len(variables)),
            "liczba_kompletnych_przypadkow": int(len(binary_data)),
            "kategoria_0": str(category_0),
            "kategoria_1": str(category_1),
            "statystyka_Q": statistic,
            "degrees_of_freedom": int(len(variables) - 1),
            "p_value": p_value,
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            "Wykonano test Q Cochrana dla pomiarów: "
            + ", ".join(variables)
            + "."
        )

        return result

    #ANOVA z powtarzanymi pomiarami
    def repeated_measures_anova_test(
            self,
            dataframe,
            variables,
    ):
        if not isinstance(variables, (list, tuple)):
            raise TypeError(
                "Pomiary muszą zostać przekazane jako lista lub krotka."
            )

        if len(variables) < 3:
            raise ValueError(
                "ANOVA z powtarzanymi pomiarami wymaga "
                "co najmniej trzech pomiarów."
            )

        missing_columns = [
            variable
            for variable in variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        data = dataframe[list(variables)].copy()

        for variable in variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 3:
            raise ValueError(
                "ANOVA z powtarzanymi pomiarami wymaga "
                "co najmniej trzech kompletnych przypadków."
            )

        sphericity_result = pg.sphericity(
            data,
            method="mauchly"
        )

        sphericity_met = bool(sphericity_result.spher)
        mauchly_w = float(sphericity_result.W)
        mauchly_chi2 = float(sphericity_result.chi2)
        mauchly_dof = int(sphericity_result.dof)
        mauchly_p = float(sphericity_result.pval)

        anova_table = pg.rm_anova(
            data=data,
            correction=True,
            detailed=False,
            effsize="ng2",
        )

        anova_row = anova_table.iloc[0]

        statistic_f = float(anova_row["F"])
        p_uncorrected = float(anova_row["p_unc"])
        df_1 = float(anova_row["ddof1"])
        df_2 = float(anova_row["ddof2"])
        epsilon = float(anova_row["eps"])
        effect_size = float(anova_row["ng2"])

        corrected_value = anova_row.get(
            "p_GG_corr",
            p_uncorrected
        )

        if pd.isna(corrected_value):
            p_corrected = p_uncorrected
        else:
            p_corrected = float(corrected_value)

        if sphericity_met:
            p_value_used = p_uncorrected
            correction_used = False
        else:
            p_value_used = p_corrected
            correction_used = True

        result = {
            "test": "repeated_measures_anova",
            "pomiary": list(variables),
            "liczba_pomiarow": int(len(variables)),
            "liczba_kompletnych_przypadkow": int(len(data)),
            "statystyka_F": statistic_f,
            "df_1": df_1,
            "df_2": df_2,
            "p_value": float(p_value_used),
            "p_uncorrected": p_uncorrected,
            "p_greenhouse_geisser": p_corrected,
            "greenhouse_geisser_epsilon": epsilon,
            "sphericity_met": sphericity_met,
            "mauchly_W": mauchly_w,
            "mauchly_chi2": mauchly_chi2,
            "mauchly_df": mauchly_dof,
            "mauchly_p_value": mauchly_p,
            "correction_used": correction_used,
            "effect_size_ng2": effect_size,
            "istotne_statystycznie": bool(
                p_value_used < 0.05
            ),
            "interpretacja": self.interpret_p_value(
                p_value_used
            ),
        }

        self.report.append(
            "Wykonano ANOVA z powtarzanymi pomiarami dla: "
            + ", ".join(variables)
            + "."
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

    #Test Friedman
    def friedman_test(
            self,
            dataframe,
            variables,
    ):
        if not isinstance(variables, (list, tuple)):
            raise TypeError(
                "Lista pomiarów testu Friedmana musi być listą lub krotką."
            )

        if len(variables) < 3:
            raise ValueError(
                "Test Friedmana wymaga co najmniej trzech pomiarów."
            )

        missing_columns = [
            variable
            for variable in variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        data = dataframe[list(variables)].copy()

        for variable in variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        # Pozostają tylko osoby posiadające wszystkie pomiary.
        data = data.dropna()

        if len(data) < 2:
            raise ValueError(
                "Test Friedmana wymaga co najmniej dwóch "
                "kompletnych zestawów obserwacji."
            )

        samples = [
            data[variable].to_numpy()
            for variable in variables
        ]

        statistic, p_value = friedmanchisquare(*samples)

        result = {
            "test": "friedman",
            "pomiary": list(variables),
            "liczba_pomiarow": int(len(variables)),
            "liczba_kompletnych_przypadkow": int(len(data)),
            "statystyka_chi2": float(statistic),
            "degrees_of_freedom": int(len(variables) - 1),
            "p_value": float(p_value),
            "istotne_statystycznie": bool(p_value < 0.05),
            "interpretacja": self.interpret_p_value(p_value),
        }

        self.report.append(
            "Wykonano test Friedmana dla pomiarów: "
            + ", ".join(variables)
            + "."
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