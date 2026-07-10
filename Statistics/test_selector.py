class TestSelector:

    def select_independent_test(
        self,
        groups_count,
        dependent_type,
        normal=None,
        equal_variances=None,
    ):
        if dependent_type == "nominal":
            return "chi_square"

        if dependent_type == "ordinal":
            if groups_count == 2:
                return "mann_whitney"
            return "kruskal_wallis"

        if dependent_type != "quantitative":
            raise ValueError("Nieznany typ zmiennej zależnej.")

        if normal is None:
            return "normality_required"

        if not normal:
            if groups_count == 2:
                return "mann_whitney"
            return "kruskal_wallis"

        if equal_variances is None:
            return "variance_test_required"

        if groups_count == 2:
            if equal_variances:
                return "t_independent"
            return "welch_t"

        if equal_variances:
            return "anova"

        return "welch_anova"

    def select_dependent_test(
            self,
            groups_count,
            dependent_type,
            normal=None,
    ):
        if groups_count not in (2, 3):
            raise ValueError(
                "Nieprawidłowa liczba porównywanych pomiarów."
            )

        if dependent_type == "nominal":
            if groups_count == 2:
                return "mcnemar"

            return "cochran_q"

        if dependent_type == "ordinal":
            if groups_count == 2:
                return "wilcoxon"

            return "friedman"

        if dependent_type != "quantitative":
            raise ValueError(
                "Nieznany typ zmiennej zależnej."
            )

        if normal is None:
            return "dependent_normality_required"

        if groups_count == 2:
            if normal:
                return "t_paired"

            return "wilcoxon"

        if normal:
            return "repeated_measures_anova"

        return "friedman"