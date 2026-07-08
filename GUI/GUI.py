import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTabWidget, QHBoxLayout, QFormLayout
)
from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.file_path = None
        self.clean_df = None
        self.results = None
        self.huba_pdf_path = "huba_report.pdf"
        self.clean_file_path = "dane_clean.xlsx"
        self.statistics_report_path = "statistics_report.txt"

        self.tabs = QTabWidget()

        self.data_tab = QWidget()
        self.test_tab = QWidget()
        self.results_tab = QWidget()

        self.normality_tab = QWidget()

        self.statistics_tab = QWidget()

        self.tabs.addTab(self.data_tab, "Dane i HUBA")
        self.tabs.addTab(self.test_tab, "Dobór testu")
        self.tabs.addTab(self.results_tab, "Wyniki")
        self.tabs.addTab(self.normality_tab, "Rozkład normalny")
        self.tabs.addTab(self.statistics_tab, "Statystyka")

        self.build_data_tab()
        self.build_test_tab()
        self.build_results_tab()
        self.build_normality_tab()
        self.build_statistics_tab()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def build_data_tab(self):
        self.label = QLabel("Nie wybrano pliku")

        self.choose_button = QPushButton("Wybierz plik CSV lub Excel")
        self.choose_button.clicked.connect(self.choose_file)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło do pliku Excel (opcjonalnie)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.refresh_button = QPushButton("Odśwież analizę")
        self.refresh_button.clicked.connect(self.run_analysis)

        self.preview_table = QTableWidget()

        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.choose_button)
        top_layout.addWidget(self.password_input)
        top_layout.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(top_layout)
        layout.addWidget(QLabel("Podgląd oczyszczonych danych:"))
        layout.addWidget(self.preview_table)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_output)

        self.data_tab.setLayout(layout)

    def build_test_tab(self):
        self.answers = {}

        self.question_label = QLabel("")
        self.question_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.answer_layout = QVBoxLayout()

        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)

        self.restart_survey_button = QPushButton("Rozpocznij ankietę od nowa")
        self.restart_survey_button.clicked.connect(self.start_test_survey)

        layout = QVBoxLayout()
        layout.addWidget(self.question_label)
        layout.addLayout(self.answer_layout)
        layout.addWidget(self.restart_survey_button)
        layout.addWidget(self.test_result)

        self.test_tab.setLayout(layout)

        self.start_test_survey()

    def build_results_tab(self):
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wyniki analizy statystycznej:"))
        layout.addWidget(self.results_output)

        self.results_tab.setLayout(layout)

    def clear_answers(self):
        while self.answer_layout.count():
            item = self.answer_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_question(self, question, options, callback):
        self.clear_answers()
        self.question_label.setText(question)

        for option in options:
            button = QPushButton(option)
            button.clicked.connect(lambda checked, value=option: callback(value))
            self.answer_layout.addWidget(button)

    def start_test_survey(self):
        self.answers = {}
        self.test_result.clear()

        self.show_question(
            "Co chcesz zbadać?",
            [
                "Opisać jedną zmienną",
                "Zbadać związek między zmiennymi",
                "Porównać grupy między sobą"
            ],
            self.answer_goal
        )

    def answer_goal(self, value):
        self.answers["goal"] = value

        if value == "Opisać jedną zmienną":
            self.ask_variable_1()
        elif value == "Zbadać związek między zmiennymi":
            self.ask_variable_1()
        elif value == "Porównać grupy między sobą":
            self.ask_variable_1()

    def ask_variable_1(self):
        if self.clean_df is None:
            self.test_result.setText("Najpierw wczytaj plik w zakładce 'Dane i HUBA'.")
            return

        columns = list(self.clean_df.columns)

        self.show_question(
            "Wybierz zmienną główną:",
            columns,
            self.answer_variable_1
        )

    def answer_variable_1(self, value):
        self.answers["variable_1"] = value

        goal = self.answers["goal"]

        if goal == "Opisać jedną zmienną":
            self.ask_variable_type()
        elif goal == "Zbadać związek między zmiennymi":
            self.ask_variable_2()
        elif goal == "Porównać grupy między sobą":
            self.ask_variable_2()

    def ask_variable_2(self):
        columns = list(self.clean_df.columns)

        self.show_question(
            "Wybierz drugą zmienną:",
            columns,
            self.answer_variable_2
        )

    def answer_variable_2(self, value):
        self.answers["variable_2"] = value

        goal = self.answers["goal"]

        if goal == "Zbadać związek między zmiennymi":
            self.ask_variable_type()
        elif goal == "Porównać grupy między sobą":
            self.ask_dependency()

    def ask_dependency(self):
        self.show_question(
            "Czy grupy są zależne czy niezależne?",
            ["Niezależne", "Zależne"],
            self.answer_dependency
        )

    def answer_dependency(self, value):
        self.answers["dependency"] = value
        self.ask_groups_count()

    def ask_groups_count(self):
        self.show_question(
            "Ile grup porównujesz?",
            ["2 grupy", "Więcej niż 2 grupy"],
            self.answer_groups_count
        )

    def answer_groups_count(self, value):
        self.answers["groups"] = value
        self.ask_variable_type()

    def ask_variable_type(self):
        self.show_question(
            "Jaki typ ma zmienna zależna?",
            ["Nominalna", "Porządkowa", "Ilościowa"],
            self.answer_variable_type
        )

    def answer_variable_type(self, value):
        self.answers["variable_type"] = value

        goal = self.answers["goal"]

        if goal == "Opisać jedną zmienną":
            self.finish_test_survey()
        elif goal == "Zbadać związek między zmiennymi":
            if value == "Ilościowa":
                self.ask_normality()
            else:
                self.finish_test_survey()
        elif goal == "Porównać grupy między sobą":
            if value == "Ilościowa":
                self.ask_normality()
            else:
                self.finish_test_survey()

    def ask_normality(self):
        self.show_question(
            "Czy zmienna ma rozkład normalny?",
            ["Tak", "Nie", "Nie wiem"],
            self.answer_normality
        )

    def answer_normality(self, value):
        self.answers["normality"] = value

        goal = self.answers["goal"]
        groups = self.answers.get("groups")

        if goal == "Porównać grupy między sobą" and groups == "Więcej niż 2 grupy":
            self.ask_variance()
        else:
            self.finish_test_survey()

    def ask_variance(self):
        self.show_question(
            "Czy wariancje są jednorodne?",
            ["Tak", "Nie", "Nie wiem"],
            self.answer_variance
        )

    def answer_variance(self, value):
        self.answers["variance"] = value
        self.finish_test_survey()

    def finish_test_survey(self):
        goal = self.answers.get("goal")
        variable_type = self.answers.get("variable_type")
        normality = self.answers.get("normality")
        dependency = self.answers.get("dependency")
        groups = self.answers.get("groups")

        if goal == "Opisać jedną zmienną":
            test = "Statystyki opisowe"

        elif goal == "Zbadać związek między zmiennymi":
            if variable_type == "Ilościowa" and normality == "Tak":
                test = "Korelacja Pearsona"
            elif variable_type == "Nominalna":
                test = "Test Chi-kwadrat niezależności"
            else:
                test = "Korelacja Spearmana"

        elif goal == "Porównać grupy między sobą":
            if dependency == "Niezależne":
                if groups == "2 grupy":
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Test t-Studenta dla prób niezależnych"
                    elif variable_type in ["Ilościowa", "Porządkowa"]:
                        test = "Test U Manna-Whitneya"
                    else:
                        test = "Test Chi-kwadrat niezależności"
                else:
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Jednoczynnikowa ANOVA"
                    elif variable_type in ["Ilościowa", "Porządkowa"]:
                        test = "Test Kruskala-Wallisa"
                    else:
                        test = "Test Chi-kwadrat niezależności"
            else:
                if groups == "2 grupy":
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Test t-Studenta dla prób zależnych"
                    else:
                        test = "Test Wilcoxona"
                else:
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "ANOVA z powtarzanym pomiarem"
                    else:
                        test = "Test Friedmana"
        else:
            test = "Nie udało się dobrać testu."

        text = "=== WYNIK DOBORU TESTU ===\n\n"

        for key, value in self.answers.items():
            text += f"{key}: {value}\n"

        text += f"\nRekomendowany test: {test}\n"

        self.question_label.setText("Ankieta zakończona")
        self.clear_answers()
        self.test_result.setText(text)

    def build_normality_tab(self):
        self.normality_variable_combo = QComboBox()

        self.normality_button = QPushButton("Sprawdź rozkład normalny")
        self.normality_button.clicked.connect(self.check_normality)

        self.normality_output = QTextEdit()
        self.normality_output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wybierz zmienną ilościową:"))
        layout.addWidget(self.normality_variable_combo)
        layout.addWidget(self.normality_button)
        layout.addWidget(self.normality_output)

        self.normality_tab.setLayout(layout)

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik",
            "",
            "Pliki danych (*.csv *.xlsx *.xls)"
        )

        if file_path:
            self.file_path = file_path
            self.label.setText(f"Wybrano plik: {file_path}")
            self.run_analysis()

    def show_dataframe_preview(self, df, max_rows=100):
        preview_df = df.head(max_rows)

        self.preview_table.setRowCount(len(preview_df))
        self.preview_table.setColumnCount(len(preview_df.columns))
        self.preview_table.setHorizontalHeaderLabels(preview_df.columns.astype(str))

        for row_idx, row in enumerate(preview_df.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                self.preview_table.setItem(
                    row_idx,
                    col_idx,
                    QTableWidgetItem(str(value))
                )

        self.preview_table.resizeColumnsToContents()

    def update_variable_lists(self):
        self.normality_variable_combo.clear()

        if self.clean_df is not None:
            numeric_columns = []

            for column in self.clean_df.columns:
                converted = pd.to_numeric(
                    self.clean_df[column],
                    errors="coerce"
                )

                if converted.notna().sum() > 0:
                    numeric_columns.append(column)

            self.normality_variable_combo.addItems(numeric_columns)
            self.stat_variable_1_combo.clear()
            self.stat_variable_2_combo.clear()
            self.stat_group_combo.clear()

            self.stat_variable_1_combo.addItems(all_columns)
            self.stat_variable_2_combo.addItems(all_columns)
            self.stat_group_combo.addItems(all_columns)


    def check_normality(self):
        try:
            if self.clean_df is None:
                self.normality_output.setText(
                    "Najpierw wczytaj plik w zakładce 'Dane i HUBA'."
                )
                return

            column = self.normality_variable_combo.currentText()

            if column == "":
                self.normality_output.setText(
                    "Brak zmiennych ilościowych do sprawdzenia."
                )
                return

            stats_engine = StatisticsEngine()
            result = stats_engine.normality_test(self.clean_df, column)

            if result is None:
                self.normality_output.setText("Nie udało się wykonać testu.")
                return

            text = "=== TEST NORMALNOŚCI ROZKŁADU ===\n\n"
            text += f"Test: {result['test']}\n"
            text += f"Zmienna: {result['kolumna']}\n"
            text += f"Statystyka W: {result['statystyka_W']:.4f}\n"
            text += f"p-value: {result['p_value']:.4f}\n"
            text += f"Rozkład normalny: {result['rozkład_normalny']}\n\n"
            text += result["interpretacja"]

            self.normality_output.setText(text)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def run_selected_statistic(self):
        try:
            if self.clean_df is None:
                self.statistics_output.setText(
                    "Najpierw wczytaj plik w zakładce 'Dane i HUBA'."
                )
                return

            analysis = self.analysis_type_combo.currentText()
            var1 = self.stat_variable_1_combo.currentText()
            var2 = self.stat_variable_2_combo.currentText()
            group = self.stat_group_combo.currentText()

            stats_engine = StatisticsEngine()

            if analysis == "Statystyki opisowe":
                result = stats_engine.descriptive_statistics(self.clean_df)

            elif analysis == "Korelacja Pearsona":
                result = self.clean_df[[var1, var2]].corr(method="pearson")

            elif analysis == "Test t-Studenta":
                result = stats_engine.t_test(self.clean_df, var1, group)

            elif analysis == "Mann–Whitney":
                result = stats_engine.mann_whitney_test(self.clean_df, var1, group)

            elif analysis == "ANOVA":
                result = stats_engine.anova_test(self.clean_df, var1, group)

            elif analysis == "Kruskal–Wallis":
                result = stats_engine.kruskal_wallis_test(self.clean_df, var1, group)

            elif analysis == "Chi-kwadrat":
                result = stats_engine.chi_square_test(self.clean_df, var1, var2)

            else:
                result = "Nieznany typ analizy."

            self.statistics_output.setText(str(result))

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def run_analysis(self):
        try:
            if not self.file_path:
                self.status_output.setText("Najpierw wybierz plik.")
                return

            password = self.password_input.text()
            if password == "":
                password = None

            huba = HUBA()

            self.clean_df = huba.run(
                self.file_path,
                self.clean_file_path,
                self.huba_pdf_path,
                password=password
            )

            self.show_dataframe_preview(self.clean_df)
            self.update_variable_lists()

            stats_engine = StatisticsEngine()
            self.results = stats_engine.run(
                self.clean_df,
                self.statistics_report_path
            )

            self.status_output.setText(
                "HUBA zakończyła czyszczenie danych.\n"
                f"Oczyszczony plik: {self.clean_file_path}\n"
                f"Raport HUBA PDF: {self.huba_pdf_path}\n"
                f"Raport statystyczny: {self.statistics_report_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def recommend_test(self):
        variable_1 = self.variable_1_combo.currentText()
        variable_2 = self.variable_2_combo.currentText()
        goal = self.goal_combo.currentText()
        dependency = self.dependency_combo.currentText()
        groups = self.groups_combo.currentText()
        variable_type = self.variable_type_combo.currentText()
        normality = self.normality_combo.currentText()
        variance = self.variance_combo.currentText()

        text = "=== DOBÓR TESTU ===\n\n"
        text += f"Zmienna główna: {variable_1}\n"
        text += f"Druga zmienna: {variable_2}\n"
        text += f"Cel analizy: {goal}\n"
        text += f"Charakter zmiennych: {dependency}\n"
        text += f"Liczba grup: {groups}\n"
        text += f"Typ zmiennej zależnej: {variable_type}\n"
        text += f"Rozkład normalny: {normality}\n"
        text += f"Jednorodność wariancji: {variance}\n\n"

        if goal == "Opisać jedną zmienną":
            test = "Statystyki opisowe"

        elif goal == "Zbadać związek między zmiennymi":
            if variable_type == "Ilościowa" and normality == "Tak":
                test = "Korelacja Pearsona"
            elif variable_type == "Nominalna":
                test = "Test Chi-kwadrat niezależności"
            else:
                test = "Korelacja Spearmana"

        elif goal == "Porównać grupy między sobą":
            if dependency == "Niezależne":
                if groups == "2 grupy":
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Test t-Studenta dla prób niezależnych"
                    elif variable_type in ["Ilościowa", "Porządkowa"]:
                        test = "Test U Manna-Whitneya"
                    else:
                        test = "Test Chi-kwadrat niezależności"
                else:
                    if variable_type == "Ilościowa" and normality == "Tak" and variance == "Tak":
                        test = "Jednoczynnikowa ANOVA"
                    elif variable_type in ["Ilościowa", "Porządkowa"]:
                        test = "Test Kruskala-Wallisa"
                    else:
                        test = "Test Chi-kwadrat niezależności"
            else:
                if groups == "2 grupy":
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Test t-Studenta dla prób zależnych"
                    else:
                        test = "Test Wilcoxona"
                else:
                    if variable_type == "Ilościowa" and normality == "Tak" and variance == "Tak":
                        test = "ANOVA z powtarzanym pomiarem"
                    else:
                        test = "Test Friedmana"
        else:
            test = "Nie udało się dobrać testu."

        text += f"Rekomendowany test: {test}\n"
        self.test_result.setText(text)

    def build_statistics_tab(self):
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Statystyki opisowe",
            "Korelacja Pearsona",
            "Test t-Studenta",
            "Mann–Whitney",
            "ANOVA",
            "Kruskal–Wallis",
            "Chi-kwadrat"
        ])

        self.stat_variable_1_combo = QComboBox()
        self.stat_variable_2_combo = QComboBox()
        self.stat_group_combo = QComboBox()

        self.run_stat_button = QPushButton("Wykonaj analizę")
        self.run_stat_button.clicked.connect(self.run_selected_statistic)

        self.statistics_output = QTextEdit()
        self.statistics_output.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Rodzaj analizy:", self.analysis_type_combo)
        form.addRow("Zmienna 1:", self.stat_variable_1_combo)
        form.addRow("Zmienna 2:", self.stat_variable_2_combo)
        form.addRow("Zmienna grupująca:", self.stat_group_combo)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.run_stat_button)
        layout.addWidget(self.statistics_output)

        self.statistics_tab.setLayout(layout)

def run_selected_statistic(self):
    self.statistics_output.setText("Tu będą wykonywane analizy statystyczne.")