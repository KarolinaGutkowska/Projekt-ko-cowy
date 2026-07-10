
import pandas as pd
import pingouin as pg
import statsmodels.api as sm
import numpy as np

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

        if test_id == "linear_regression":
            return self.linear_regression_test(
                dataframe=dataframe,
                dependent_variable=dependent_var,
                independent_variables=variables,
            )
        if test_id == "logistic_regression":
            return self.logistic_regression_test(
                dataframe=dataframe,
                dependent_variable=dependent_var,
                independent_variables=variables,
            )
        if test_id == "mediation":
            if not variables or len(variables) != 1:
                raise ValueError(
                    "Dla analizy mediacji należy przekazać "
                    "dokładnie jeden mediator."
                )

            return self.mediation_test(
                dataframe=dataframe,
                independent_variable=independent_var,
                mediator_variable=variables[0],
                dependent_variable=dependent_var,
            )
        if test_id == "moderation":
            if not variables or len(variables) != 1:
                raise ValueError(
                    "Dla analizy moderacji należy przekazać "
                    "dokładnie jeden moderator."
                )

            return self.moderation_test(
                dataframe=dataframe,
                independent_variable=independent_var,
                moderator_variable=variables[0],
                dependent_variable=dependent_var,
            )

        raise ValueError(
            f"Nieznany identyfikator testu: {test_id}"
        )
    #Moderacje
    def moderation_test(
            self,
            dataframe,
            independent_variable,
            moderator_variable,
            dependent_variable,
    ):
        variables = [
            independent_variable,
            moderator_variable,
            dependent_variable,
        ]

        if len(set(variables)) != 3:
            raise ValueError(
                "Zmienna X, moderator W i zmienna Y "
                "muszą być różnymi kolumnami."
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

        data = dataframe[variables].copy()

        for variable in variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 10:
            raise ValueError(
                "Analiza moderacji wymaga co najmniej "
                "10 kompletnych obserwacji."
            )

        for variable in variables:
            if data[variable].nunique() < 2:
                raise ValueError(
                    f"Zmienna „{variable}” nie zawiera "
                    "wystarczającej zmienności."
                )

        x_mean = float(data[independent_variable].mean())
        w_mean = float(data[moderator_variable].mean())

        x_centered_name = f"{independent_variable}_centered"
        w_centered_name = f"{moderator_variable}_centered"
        interaction_name = "X_x_W"

        data[x_centered_name] = (
                data[independent_variable] - x_mean
        )

        data[w_centered_name] = (
                data[moderator_variable] - w_mean
        )

        data[interaction_name] = (
                data[x_centered_name]
                * data[w_centered_name]
        )

        predictors = [
            x_centered_name,
            w_centered_name,
            interaction_name,
        ]

        x_matrix = sm.add_constant(
            data[predictors],
            has_constant="add"
        )

        y = data[dependent_variable]

        model = sm.OLS(
            y,
            x_matrix
        ).fit()

        confidence_intervals = model.conf_int()

        coefficients = []

        display_names = {
            "const": "Wyraz wolny",
            x_centered_name: independent_variable,
            w_centered_name: moderator_variable,
            interaction_name: (
                f"{independent_variable} × {moderator_variable}"
            ),
        }

        for variable_name in model.params.index:
            confidence_interval = confidence_intervals.loc[
                variable_name
            ]

            coefficients.append({
                "zmienna": display_names.get(
                    variable_name,
                    str(variable_name)
                ),
                "nazwa_techniczna": str(variable_name),
                "wspolczynnik": float(
                    model.params[variable_name]
                ),
                "blad_standardowy": float(
                    model.bse[variable_name]
                ),
                "statystyka_t": float(
                    model.tvalues[variable_name]
                ),
                "p_value": float(
                    model.pvalues[variable_name]
                ),
                "ci_95_lower": float(
                    confidence_interval.iloc[0]
                ),
                "ci_95_upper": float(
                    confidence_interval.iloc[1]
                ),
                "istotne_statystycznie": bool(
                    model.pvalues[variable_name] < 0.05
                ),
            })

        interaction_coefficient = float(
            model.params[interaction_name]
        )

        interaction_p_value = float(
            model.pvalues[interaction_name]
        )

        moderator_standard_deviation = float(
            data[moderator_variable].std(ddof=1)
        )

        moderator_levels = {
            "niski": (
                    w_mean - moderator_standard_deviation
            ),
            "sredni": w_mean,
            "wysoki": (
                    w_mean + moderator_standard_deviation
            ),
        }

        main_x_effect = float(
            model.params[x_centered_name]
        )

        simple_slopes = {}

        for level_name, level_value in moderator_levels.items():
            centered_level = level_value - w_mean

            slope = (
                    main_x_effect
                    + interaction_coefficient * centered_level
            )

            simple_slopes[level_name] = {
                "wartosc_moderatora": float(level_value),
                "nachylenie_X": float(slope),
            }

        if interaction_p_value < 0.05:
            moderation_interpretation = (
                "Interakcja X × W jest istotna statystycznie. "
                "Wpływ zmiennej X na Y zależy od poziomu moderatora W."
            )
        else:
            moderation_interpretation = (
                "Interakcja X × W nie jest istotna statystycznie. "
                "Nie stwierdzono, aby wpływ X na Y zależał "
                "od poziomu moderatora W."
            )

        result = {
            "test": "moderation",
            "zmienna_niezalezna": independent_variable,
            "moderator": moderator_variable,
            "zmienna_zalezna": dependent_variable,
            "liczba_obserwacji": int(model.nobs),
            "srednia_X": x_mean,
            "srednia_W": w_mean,
            "r_squared": float(model.rsquared),
            "adjusted_r_squared": float(
                model.rsquared_adj
            ),
            "statystyka_F": float(model.fvalue),
            "p_value_modelu": float(
                model.f_pvalue
            ),
            "df_model": float(model.df_model),
            "df_residual": float(model.df_resid),
            "aic": float(model.aic),
            "bic": float(model.bic),
            "wspolczynniki": coefficients,
            "interakcja_wspolczynnik": (
                interaction_coefficient
            ),
            "interakcja_p_value": (
                interaction_p_value
            ),
            "interakcja_istotna": bool(
                interaction_p_value < 0.05
            ),
            "simple_slopes": simple_slopes,
            "interpretacja": moderation_interpretation,
        }

        self.report.append(
            "Wykonano analizę moderacji: "
            f"{independent_variable} × "
            f"{moderator_variable} → "
            f"{dependent_variable}."
        )

        return result
    #Mediacje
    def mediation_test(
            self,
            dataframe,
            independent_variable,
            mediator_variable,
            dependent_variable,
            bootstrap_samples=2000,
            random_state=42,
    ):
        variables = [
            independent_variable,
            mediator_variable,
            dependent_variable,
        ]

        if len(set(variables)) != 3:
            raise ValueError(
                "Zmienna niezależna, mediator i zmienna zależna "
                "muszą być różnymi kolumnami."
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

        data = dataframe[variables].copy()

        for variable in variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        if len(data) < 10:
            raise ValueError(
                "Analiza mediacji wymaga co najmniej "
                "10 kompletnych obserwacji."
            )

        x = data[independent_variable].astype(float)
        m = data[mediator_variable].astype(float)
        y = data[dependent_variable].astype(float)

        if x.nunique() < 2:
            raise ValueError(
                "Zmienna niezależna nie zawiera wystarczającej "
                "zmienności."
            )

        if m.nunique() < 2 or y.nunique() < 2:
            raise ValueError(
                "Mediator i zmienna zależna muszą zawierać "
                "co najmniej dwie różne wartości."
            )

        # Ścieżka a: X → M
        model_a_x = sm.add_constant(
            data[[independent_variable]],
            has_constant="add"
        )

        model_a = sm.OLS(
            m,
            model_a_x
        ).fit()

        path_a = float(
            model_a.params[independent_variable]
        )

        path_a_p = float(
            model_a.pvalues[independent_variable]
        )

        # Efekt całkowity c: X → Y
        model_c_x = sm.add_constant(
            data[[independent_variable]],
            has_constant="add"
        )

        model_c = sm.OLS(
            y,
            model_c_x
        ).fit()

        total_effect_c = float(
            model_c.params[independent_variable]
        )

        total_effect_p = float(
            model_c.pvalues[independent_variable]
        )

        # Ścieżki b i c′: X + M → Y
        model_direct_x = sm.add_constant(
            data[
                [
                    independent_variable,
                    mediator_variable,
                ]
            ],
            has_constant="add"
        )

        model_direct = sm.OLS(
            y,
            model_direct_x
        ).fit()

        path_b = float(
            model_direct.params[mediator_variable]
        )

        path_b_p = float(
            model_direct.pvalues[mediator_variable]
        )

        direct_effect_c_prime = float(
            model_direct.params[independent_variable]
        )

        direct_effect_p = float(
            model_direct.pvalues[independent_variable]
        )

        indirect_effect = float(
            path_a * path_b
        )

        # Bootstrap efektu pośredniego a × b.
        rng = np.random.default_rng(random_state)

        bootstrap_indirect_effects = []

        for _ in range(bootstrap_samples):
            sampled_indices = rng.integers(
                low=0,
                high=len(data),
                size=len(data),
            )

            sample = data.iloc[
                sampled_indices
            ].reset_index(drop=True)

            try:
                sample_m = sample[mediator_variable]
                sample_y = sample[dependent_variable]

                sample_a_x = sm.add_constant(
                    sample[[independent_variable]],
                    has_constant="add"
                )

                sample_a_model = sm.OLS(
                    sample_m,
                    sample_a_x
                ).fit()

                sample_direct_x = sm.add_constant(
                    sample[
                        [
                            independent_variable,
                            mediator_variable,
                        ]
                    ],
                    has_constant="add"
                )

                sample_direct_model = sm.OLS(
                    sample_y,
                    sample_direct_x
                ).fit()

                sample_a = float(
                    sample_a_model.params[
                        independent_variable
                    ]
                )

                sample_b = float(
                    sample_direct_model.params[
                        mediator_variable
                    ]
                )

                bootstrap_indirect_effects.append(
                    sample_a * sample_b
                )

            except Exception:
                continue

        if len(bootstrap_indirect_effects) < 100:
            raise ValueError(
                "Nie udało się uzyskać wystarczającej liczby "
                "poprawnych prób bootstrap."
            )

        bootstrap_values = np.asarray(
            bootstrap_indirect_effects,
            dtype=float
        )

        indirect_ci_lower = float(
            np.percentile(bootstrap_values, 2.5)
        )

        indirect_ci_upper = float(
            np.percentile(bootstrap_values, 97.5)
        )

        indirect_effect_significant = not (
                indirect_ci_lower <= 0 <= indirect_ci_upper
        )

        if indirect_effect_significant:
            mediation_interpretation = (
                "Przedział ufności dla efektu pośredniego "
                "nie obejmuje zera. Wynik wskazuje na "
                "statystycznie istotny efekt pośredni."
            )
        else:
            mediation_interpretation = (
                "Przedział ufności dla efektu pośredniego "
                "obejmuje zero. Nie stwierdzono istotnego "
                "efektu pośredniego."
            )

        result = {
            "test": "mediation",
            "zmienna_niezalezna": independent_variable,
            "mediator": mediator_variable,
            "zmienna_zalezna": dependent_variable,
            "liczba_obserwacji": int(len(data)),
            "bootstrap_samples_requested": int(
                bootstrap_samples
            ),
            "bootstrap_samples_valid": int(
                len(bootstrap_values)
            ),

            "path_a": path_a,
            "path_a_p_value": path_a_p,

            "path_b": path_b,
            "path_b_p_value": path_b_p,

            "total_effect_c": total_effect_c,
            "total_effect_p_value": total_effect_p,

            "direct_effect_c_prime": direct_effect_c_prime,
            "direct_effect_p_value": direct_effect_p,

            "indirect_effect_ab": indirect_effect,
            "indirect_ci_95_lower": indirect_ci_lower,
            "indirect_ci_95_upper": indirect_ci_upper,
            "indirect_effect_significant": bool(
                indirect_effect_significant
            ),

            "r_squared_mediator_model": float(
                model_a.rsquared
            ),
            "r_squared_outcome_model": float(
                model_direct.rsquared
            ),

            "interpretacja": mediation_interpretation,
        }

        self.report.append(
            "Wykonano analizę mediacji: "
            f"{independent_variable} → "
            f"{mediator_variable} → "
            f"{dependent_variable}."
        )

        return result
    #Regresja logistyczna
    def logistic_regression_test(
            self,
            dataframe,
            dependent_variable,
            independent_variables,
    ):
        if not dependent_variable:
            raise ValueError(
                "Nie podano zmiennej zależnej."
            )

        if not isinstance(
                independent_variables,
                (list, tuple)
        ):
            raise TypeError(
                "Zmienne niezależne muszą być listą lub krotką."
            )

        if len(independent_variables) < 2:
            raise ValueError(
                "Regresja logistyczna wieloraka wymaga "
                "co najmniej dwóch predyktorów."
            )

        all_variables = [
            dependent_variable,
            *independent_variables,
        ]

        missing_columns = [
            variable
            for variable in all_variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        if dependent_variable in independent_variables:
            raise ValueError(
                "Zmienna zależna nie może być predyktorem."
            )

        data = dataframe[all_variables].copy()
        data = data.dropna(
            subset=[dependent_variable]
        )

        dependent_categories = list(
            pd.unique(data[dependent_variable].dropna())
        )

        if len(dependent_categories) != 2:
            raise ValueError(
                "Binarna regresja logistyczna wymaga zmiennej "
                "zależnej mającej dokładnie dwie kategorie."
            )

        category_0 = dependent_categories[0]
        category_1 = dependent_categories[1]

        data[dependent_variable] = data[
            dependent_variable
        ].map({
            category_0: 0,
            category_1: 1,
        })

        for variable in independent_variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        minimum_observations = (
                len(independent_variables) + 3
        )

        if len(data) < minimum_observations:
            raise ValueError(
                "Za mało kompletnych obserwacji względem "
                "liczby predyktorów."
            )

        y = data[dependent_variable].astype(int)

        if y.nunique() != 2:
            raise ValueError(
                "Po usunięciu braków danych pozostała tylko "
                "jedna kategoria zmiennej zależnej."
            )

        x = data[list(independent_variables)].astype(float)

        # Logit nie dodaje wyrazu wolnego automatycznie.
        x = sm.add_constant(
            x,
            has_constant="add"
        )

        try:
            model = sm.Logit(
                y,
                x
            ).fit(
                disp=False,
                maxiter=200
            )
        except Exception as error:
            raise ValueError(
                "Nie udało się dopasować modelu logistycznego. "
                "Możliwą przyczyną jest idealne rozdzielenie "
                "kategorii, silna współliniowość albo za mała "
                f"liczba obserwacji. Szczegóły: {error}"
            ) from error

        confidence_intervals = model.conf_int()

        coefficients = []

        for variable_name in model.params.index:
            coefficient = float(
                model.params[variable_name]
            )

            standard_error = float(
                model.bse[variable_name]
            )

            z_statistic = float(
                model.tvalues[variable_name]
            )

            p_value = float(
                model.pvalues[variable_name]
            )

            ci_lower = float(
                confidence_intervals.loc[
                    variable_name
                ].iloc[0]
            )

            ci_upper = float(
                confidence_intervals.loc[
                    variable_name
                ].iloc[1]
            )

            odds_ratio = float(
                np.exp(coefficient)
            )

            odds_ratio_ci_lower = float(
                np.exp(ci_lower)
            )

            odds_ratio_ci_upper = float(
                np.exp(ci_upper)
            )

            if variable_name == "const":
                display_name = "Wyraz wolny"
            else:
                display_name = str(variable_name)

            coefficients.append({
                "zmienna": display_name,
                "nazwa_techniczna": str(variable_name),
                "wspolczynnik": coefficient,
                "blad_standardowy": standard_error,
                "statystyka_z": z_statistic,
                "p_value": p_value,
                "ci_95_lower": ci_lower,
                "ci_95_upper": ci_upper,
                "odds_ratio": odds_ratio,
                "or_ci_95_lower": odds_ratio_ci_lower,
                "or_ci_95_upper": odds_ratio_ci_upper,
                "istotne_statystycznie": bool(
                    p_value < 0.05
                ),
            })

        predicted_probabilities = model.predict(x)

        predicted_classes = (
                predicted_probabilities >= 0.5
        ).astype(int)

        accuracy = float(
            (predicted_classes == y).mean()
        )

        likelihood_ratio_statistic = float(
            model.llr
        )

        likelihood_ratio_p_value = float(
            model.llr_pvalue
        )

        result = {
            "test": "logistic_regression",
            "zmienna_zalezna": dependent_variable,
            "zmienne_niezalezne": list(
                independent_variables
            ),
            "kategoria_0": str(category_0),
            "kategoria_1": str(category_1),
            "liczba_obserwacji": int(model.nobs),
            "pseudo_r_squared_mcfadden": float(
                model.prsquared
            ),
            "log_likelihood": float(model.llf),
            "log_likelihood_null": float(model.llnull),
            "likelihood_ratio_statistic": (
                likelihood_ratio_statistic
            ),
            "p_value_modelu": likelihood_ratio_p_value,
            "aic": float(model.aic),
            "bic": float(model.bic),
            "accuracy_threshold_05": accuracy,
            "wspolczynniki": coefficients,
            "model_istotny": bool(
                likelihood_ratio_p_value < 0.05
            ),
            "interpretacja": self.interpret_p_value(
                likelihood_ratio_p_value
            ),
        }

        self.report.append(
            "Wykonano regresję logistyczną dla zmiennej "
            f"zależnej '{dependent_variable}' oraz "
            "predyktorów: "
            + ", ".join(independent_variables)
            + "."
        )

        return result

    #Regresja liniowa
    def linear_regression_test(
            self,
            dataframe,
            dependent_variable,
            independent_variables,
    ):
        if not dependent_variable:
            raise ValueError(
                "Nie podano zmiennej zależnej."
            )

        if not isinstance(
                independent_variables,
                (list, tuple)
        ):
            raise TypeError(
                "Zmienne niezależne muszą zostać "
                "przekazane jako lista lub krotka."
            )

        if len(independent_variables) < 2:
            raise ValueError(
                "Regresja wieloraka wymaga co najmniej "
                "dwóch zmiennych niezależnych."
            )

        all_variables = [
            dependent_variable,
            *independent_variables,
        ]

        missing_columns = [
            variable
            for variable in all_variables
            if variable not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Nie znaleziono kolumn: "
                + ", ".join(missing_columns)
            )

        if dependent_variable in independent_variables:
            raise ValueError(
                "Zmienna zależna nie może znajdować się "
                "na liście predyktorów."
            )

        data = dataframe[all_variables].copy()

        for variable in all_variables:
            data[variable] = pd.to_numeric(
                data[variable],
                errors="coerce"
            )

        data = data.dropna()

        minimum_observations = (
                len(independent_variables) + 2
        )

        if len(data) < minimum_observations:
            raise ValueError(
                "Za mało kompletnych obserwacji względem "
                "liczby predyktorów."
            )

        y = data[dependent_variable]

        x = data[list(independent_variables)]

        # OLS nie dodaje wyrazu wolnego automatycznie.
        x = sm.add_constant(
            x,
            has_constant="add"
        )

        model = sm.OLS(
            y,
            x
        ).fit()

        coefficients = []

        for variable_name in model.params.index:
            confidence_interval = model.conf_int().loc[
                variable_name
            ]

            if variable_name == "const":
                display_name = "Wyraz wolny"
            else:
                display_name = str(variable_name)

            coefficients.append({
                "zmienna": display_name,
                "nazwa_techniczna": str(variable_name),
                "wspolczynnik": float(
                    model.params[variable_name]
                ),
                "blad_standardowy": float(
                    model.bse[variable_name]
                ),
                "statystyka_t": float(
                    model.tvalues[variable_name]
                ),
                "p_value": float(
                    model.pvalues[variable_name]
                ),
                "ci_95_lower": float(
                    confidence_interval.iloc[0]
                ),
                "ci_95_upper": float(
                    confidence_interval.iloc[1]
                ),
                "istotne_statystycznie": bool(
                    model.pvalues[variable_name] < 0.05
                ),
            })

        result = {
            "test": "linear_regression",
            "zmienna_zalezna": dependent_variable,
            "zmienne_niezalezne": list(
                independent_variables
            ),
            "liczba_obserwacji": int(model.nobs),
            "r_squared": float(model.rsquared),
            "adjusted_r_squared": float(
                model.rsquared_adj
            ),
            "statystyka_F": float(model.fvalue),
            "p_value_modelu": float(
                model.f_pvalue
            ),
            "df_model": float(model.df_model),
            "df_residual": float(model.df_resid),
            "aic": float(model.aic),
            "bic": float(model.bic),
            "wspolczynniki": coefficients,
            "model_istotny": bool(
                model.f_pvalue < 0.05
            ),
            "interpretacja": (
                self.interpret_p_value(
                    model.f_pvalue
                )
            ),
        }

        self.report.append(
            "Wykonano regresję liniową dla zmiennej "
            f"zależnej '{dependent_variable}' oraz "
            "predyktorów: "
            + ", ".join(independent_variables)
            + "."
        )

        return result

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