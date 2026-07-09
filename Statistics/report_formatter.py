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

        else:
            return "Formatowanie tego testu zostanie dodane później."

    def format_chi_square(self, result, independent_var, dependent_var):
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
"""

    def format_mann_whitney(self, result, independent_var, dependent_var):
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
"""