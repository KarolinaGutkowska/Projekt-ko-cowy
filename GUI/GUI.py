import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QStackedWidget
)

from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer")
        self.setGeometry(100, 100, 1300, 800)

        self.file_path = None
        self.clean_df = None
        self.results = None

        self.huba_pdf_path = "reports/huba_report.pdf"
        self.clean_file_path = "dane_clean.xlsx"
        self.statistics_report_path = "statistics_report.txt"

        main_layout = QHBoxLayout()

        self.sidebar = QVBoxLayout()
        self.content = QStackedWidget()

        self.build_sidebar()
        self.build_pages()

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.content, 5)

        self.setLayout(main_layout)

    def build_sidebar(self):
        title = QLabel("StatAnalyzer")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        self.sidebar.addWidget(title)

        buttons = [
            ("Dane", 0),
            ("Analiza", 1),
            ("Wyniki", 2),
            ("Raporty", 3),
        ]

        for name, index in buttons:
            button = QPushButton(name)
            button.setMinimumHeight(45)
            button.clicked.connect(lambda checked, i=index: self.content.setCurrentIndex(i))
            self.sidebar.addWidget(button)

        self.sidebar.addStretch()

    def build_pages(self):
        self.data_page = QWidget()
        self.analysis_page = QWidget()
        self.normality_page = QWidget()
        self.test_page = QWidget()
        self.results_page = QWidget()
        self.reports_page = QWidget()

        self.build_data_page()
        self.build_analysis_page()
        self.build_normality_page()
        self.build_test_page()
        self.build_results_page()
        self.build_reports_page()

        self.content.addWidget(self.data_page)
        self.content.addWidget(self.analysis_page)
        self.content.addWidget(self.normality_page)
        self.content.addWidget(self.test_page)
        self.content.addWidget(self.results_page)
        self.content.addWidget(self.reports_page)

    def build_data_page(self):
        self.file_label = QLabel("Nie wybrano pliku")

        self.choose_button = QPushButton("Wybierz plik CSV lub Excel")
        self.choose_button.clicked.connect(self.choose_file)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło do pliku Excel, jeśli potrzebne")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.refresh_button = QPushButton("Odśwież HUBA")
        self.refresh_button.clicked.connect(self.run_analysis)

        self.preview_table = QTableWidget()

        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)

        top = QHBoxLayout()
        top.addWidget(self.choose_button)
        top.addWidget(self.password_input)
        top.addWidget(self.refresh_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dane i HUBA"))
        layout.addWidget(self.file_label)
        layout.addLayout(top)
        layout.addWidget(QLabel("Podgląd oczyszczonych danych"))
        layout.addWidget(self.preview_table)
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self.status_output)

        self.data_page.setLayout(layout)

    def build_analysis_page(self):
        layout = QVBoxLayout()

        title = QLabel("Co chcesz zrobić?")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")

        self.descriptive_button = QPushButton("Statystyka opisowa")
        self.compare_groups_button = QPushButton("Porównanie grup pomiędzy sobą")
        self.relationship_button = QPushButton("Badanie związku między grupami")

        self.descriptive_button.setMinimumHeight(50)
        self.compare_groups_button.setMinimumHeight(50)
        self.relationship_button.setMinimumHeight(50)

        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(self.descriptive_button)
        layout.addWidget(self.compare_groups_button)
        layout.addWidget(self.relationship_button)
        layout.addWidget(self.analysis_output)

        self.analysis_page.setLayout(layout)

    def build_normality_page(self):
        layout = QVBoxLayout()

        self.normality_variable_combo = QComboBox()

        self.normality_button = QPushButton("Sprawdź rozkład normalny")
        self.normality_button.clicked.connect(self.check_normality)

        self.normality_output = QTextEdit()
        self.normality_output.setReadOnly(True)

        layout.addWidget(QLabel("Rozkład normalny"))
        layout.addWidget(QLabel("Wybierz zmienną ilościową"))
        layout.addWidget(self.normality_variable_combo)
        layout.addWidget(self.normality_button)
        layout.addWidget(self.normality_output)

        self.normality_page.setLayout(layout)

    def build_test_page(self):
        layout = QVBoxLayout()

        self.test_question = QLabel("Dobór testu")
        self.test_question.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.test_answers_layout = QVBoxLayout()

        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)

        self.restart_test_button = QPushButton("Rozpocznij ankietę")
        self.restart_test_button.clicked.connect(self.start_test_survey)

        layout.addWidget(self.test_question)
        layout.addLayout(self.test_answers_layout)
        layout.addWidget(self.restart_test_button)
        layout.addWidget(self.test_result)

        self.test_page.setLayout(layout)

    def build_results_page(self):
        layout = QVBoxLayout()

        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)

        layout.addWidget(QLabel("Wyniki"))
        layout.addWidget(self.results_output)

        self.results_page.setLayout(layout)

    def build_reports_page(self):
        layout = QVBoxLayout()

        self.reports_output = QTextEdit()
        self.reports_output.setReadOnly(True)

        layout.addWidget(QLabel("Raporty"))
        layout.addWidget(self.reports_output)

        self.reports_page.setLayout(layout)

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik",
            "",
            "Pliki danych (*.csv *.xlsx *.xls)"
        )

        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Wybrano plik: {file_path}")
            self.run_analysis()

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

            self.results_output.setText(
                "Dane zostały wczytane i oczyszczone.\n"
                "Możesz przejść do modułu Analiza lub Rozkład normalny."
            )

            self.reports_output.setText(
                f"Raport HUBA: {self.huba_pdf_path}\n"
                f"Raport statystyczny: {self.statistics_report_path}\n"
                f"Oczyszczony plik: {self.clean_file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

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
        if self.clean_df is None:
            return

        all_columns = list(self.clean_df.columns)

        self.analysis_var1.clear()
        self.analysis_var2.clear()
        self.analysis_group.clear()
        self.normality_variable_combo.clear()

        self.analysis_var1.addItems(all_columns)
        self.analysis_var2.addItems(all_columns)
        self.analysis_group.addItems(all_columns)

        numeric_columns = []

        for column in self.clean_df.columns:
            converted = pd.to_numeric(self.clean_df[column], errors="coerce")
            valid_ratio = converted.notna().sum() / len(converted)

            if valid_ratio >= 0.8:
                numeric_columns.append(column)

        self.normality_variable_combo.addItems(numeric_columns)

    def run_selected_statistic(self):
        try:
            if self.clean_df is None:
                self.analysis_output.setText("Najpierw wczytaj plik.")
                return

            analysis = self.analysis_type_combo.currentText()
            var1 = self.analysis_var1.currentText()
            var2 = self.analysis_var2.currentText()
            group = self.analysis_group.currentText()

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

            self.analysis_output.setText(str(result))
            self.results_output.setText(str(result))

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def check_normality(self):
        try:
            if self.clean_df is None:
                self.normality_output.setText("Najpierw wczytaj plik.")
                return

            column = self.normality_variable_combo.currentText()

            if column == "":
                self.normality_output.setText("Brak zmiennych ilościowych.")
                return

            stats_engine = StatisticsEngine()
            result = stats_engine.normality_test(self.clean_df, column)

            self.normality_output.setText(str(result))
            self.results_output.setText(str(result))

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def clear_test_answers(self):
        while self.test_answers_layout.count():
            item = self.test_answers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_test_question(self, question, options, callback):
        self.clear_test_answers()
        self.test_question.setText(question)

        for option in options:
            button = QPushButton(option)
            button.clicked.connect(lambda checked, value=option: callback(value))
            self.test_answers_layout.addWidget(button)

    def start_test_survey(self):
        self.test_answers = {}
        self.test_result.clear()

        self.show_test_question(
            "Co chcesz zbadać?",
            [
                "Opisać jedną zmienną",
                "Zbadać związek między zmiennymi",
                "Porównać grupy między sobą"
            ],
            self.answer_goal
        )

    def answer_goal(self, value):
        self.test_answers["goal"] = value
        self.finish_test_survey()

    def finish_test_survey(self):
        goal = self.test_answers.get("goal")

        if goal == "Opisać jedną zmienną":
            test = "Statystyki opisowe"
        elif goal == "Zbadać związek między zmiennymi":
            test = "Korelacja Pearsona / Spearmana albo Chi-kwadrat"
        elif goal == "Porównać grupy między sobą":
            test = "t-Studenta / Mann–Whitney / ANOVA / Kruskal–Wallis"
        else:
            test = "Nie udało się dobrać testu."

        self.clear_test_answers()
        self.test_question.setText("Ankieta zakończona")

        self.test_result.setText(
            f"Cel analizy: {goal}\n"
            f"Rekomendowany kierunek: {test}"
        )