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

        elif test_id == "wilcoxon":
            return self.format_wilcoxon(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "t_paired":
            return self.format_t_paired(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "mcnemar":
            return self.format_mcnemar(
                result,
                independent_var,
                dependent_var
            )

        elif test_id == "friedman":
            return self.format_friedman(result)

        elif test_id == "cochran_q":
            return self.format_cochran_q(
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

    def format_mcnemar(
            self,
            result,
            first_variable,
            second_variable
    ):
        table = result["tabela"]

        return f"""
    ========================================
    TEST McNEMARA
    ========================================

    PIERWSZY POMIAR:
    {first_variable}

    DRUGI POMIAR:
    {second_variable}

    LICZBA KOMPLETNYCH PAR:
    {result['liczba_par']}

    KATEGORIE:
    {result['kategoria_1']}
    {result['kategoria_2']}

    TABELA 2 × 2:
    {table[0][0]}    {table[0][1]}
    {table[1][0]}    {table[1][1]}

    WYNIKI TESTU:
    Statystyka = {result['statystyka']:.4f}
    p-value = {result['p_value']:.4f}

    INTERPRETACJA:
    {result['interpretacja']}
    ========================================
    """.strip()

    def format_friedman(
            self,
            result,
            independent_var=None,
            dependent_var=None,
    ):
        measurements = "\n".join(
            f"- {measurement}"
            for measurement in result["pomiary"]
        )

        return f"""
    ========================================
    TEST FRIEDMANA
    ========================================

    PORÓWNYWANE POMIARY:
    {measurements}

    LICZBA POMIARÓW:
    {result['liczba_pomiarow']}

    LICZBA KOMPLETNYCH PRZYPADKÓW:
    {result['liczba_kompletnych_przypadkow']}

    WYNIKI TESTU:
    χ² = {result['statystyka_chi2']:.4f}
    df = {result['degrees_of_freedom']}
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

    def format_t_paired(
            self,
            result,
            first_variable,
            second_variable
    ):
        return f"""
    ========================================
    TEST T-STUDENTA DLA PRÓB ZALEŻNYCH
    ========================================

    PIERWSZY POMIAR:
    {first_variable}

    DRUGI POMIAR:
    {second_variable}

    LICZBA KOMPLETNYCH PAR:
    {result['liczba_par']}

    ŚREDNIA — POMIAR 1:
    {result['srednia_1']:.4f}

    ŚREDNIA — POMIAR 2:
    {result['srednia_2']:.4f}

    WYNIKI TESTU:
    t = {result['statystyka_t']:.4f}
    p-value = {result['p_value']:.4f}

    INTERPRETACJA:
    {result['interpretacja']}
    ========================================
    """.strip()

    def format_wilcoxon(
            self,
            result,
            first_variable,
            second_variable
    ):
        return f"""
    ========================================
    TEST WILCOXONA DLA PRÓB ZALEŻNYCH
    ========================================

    PIERWSZY POMIAR:
    {first_variable}

    DRUGI POMIAR:
    {second_variable}

    LICZBA KOMPLETNYCH PAR:
    {result['liczba_par']}

    WYNIKI TESTU:
    W = {result['statystyka_W']:.4f}
    p-value = {result['p_value']:.4f}

    INTERPRETACJA:
    {result['interpretacja']}
    ========================================
    """.strip()