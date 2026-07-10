class ReportFormatter:

    def format(self, test_id, result, independent_var, dependent_var):
        if result is None:
            return f"Nie udało się wykonać testu: {test_id}"

        if test_id == "chi_square":
            return self.format_chi_square(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "mann_whitney":
            return self.format_mann_whitney(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "t_independent":
            return self.format_t_independent(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "welch_t":
            return self.format_welch_t(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "kruskal_wallis":
            return self.format_kruskal_wallis(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "anova":
            return self.format_anova(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "welch_anova":
            return self.format_welch_anova(
                result,
                independent_var,
                dependent_var
            )

        else:
            return (
                f"Formatowanie testu „{test_id}” "
                "zostanie dodane później."
            )

    def format_chi_square(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
TEST CHI-KWADRAT NIEZALEŻNOŚCI
========================================

ZMIENNA NIEZALEŻNA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

WYNIKI TESTU:
χ² = {result['chi2']:.4f}
df = {result['degrees_of_freedom']}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_mann_whitney(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
TEST U MANNA-WHITNEYA
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

GRUPA 1:
{result['grupa_1']}

GRUPA 2:
{result['grupa_2']}

WYNIKI TESTU:
U = {result['statystyka_U']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_t_independent(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
TEST T-STUDENTA DLA PRÓB NIEZALEŻNYCH
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

GRUPA 1:
{result['grupa_1']}

GRUPA 2:
{result['grupa_2']}

WYNIKI TESTU:
t = {result['statystyka_t']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_welch_t(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
TEST T WELCHA DLA PRÓB NIEZALEŻNYCH
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

GRUPA 1:
{result['grupa_1']}

GRUPA 2:
{result['grupa_2']}

WYNIKI TESTU:
t = {result['statystyka_t']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_kruskal_wallis(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
TEST KRUSKALA-WALLISA
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

LICZBA GRUP:
{result['liczba_grup']}

GRUPY:
{result['grupy']}

WYNIKI TESTU:
H = {result['statystyka_H']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_anova(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
JEDNOCZYNNIKOWA ANOVA
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

LICZBA GRUP:
{result['liczba_grup']}

GRUPY:
{result['grupy']}

WYNIKI TESTU:
F = {result['statystyka_F']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()

    def format_welch_anova(
        self,
        result,
        independent_var,
        dependent_var
    ):
        return f"""
========================================
JEDNOCZYNNIKOWA ANOVA WELCHA
========================================

ZMIENNA GRUPUJĄCA:
{independent_var}

ZMIENNA ZALEŻNA:
{dependent_var}

LICZBA GRUP:
{result['liczba_grup']}

GRUPY:
{result['grupy']}

WYNIKI TESTU:
F = {result['statystyka_F']:.4f}
p-value = {result['p_value']:.4f}

INTERPRETACJA:
{result['interpretacja']}
========================================
""".strip()