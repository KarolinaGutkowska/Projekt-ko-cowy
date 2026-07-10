import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QStackedWidget,
    QCheckBox, QScrollArea, QTableView
)
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtCore import QTimer

from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine
from Statistics.report_formatter import ReportFormatter
from Statistics.test_selector import TestSelector


class PandasTableModel(QAbstractTableModel):
    def __init__(self, dataframe):
        super().__init__()
        self.dataframe = dataframe

    def rowCount(self, parent=None):
        return len(self.dataframe)

    def columnCount(self, parent=None):
        return len(self.dataframe.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.dataframe.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self.dataframe.columns[section])
            else:
                return str(section + 1)
        return None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer")
        self.setGeometry(100, 100, 1300, 800)

        self.file_path = None
        self.clean_df = None
        self.results = None

        self.test_selector = TestSelector()

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
        self.results_page = QWidget()
        self.reports_page = QWidget()

        self.build_data_page()
        self.build_analysis_page()
        self.build_results_page()
        self.build_reports_page()

        self.content.addWidget(self.data_page)
        self.content.addWidget(self.analysis_page)
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
        if self.analysis_page.layout() is not None:
            self.clear_analysis_page()
            layout = self.analysis_page.layout()
        else:
            layout = QVBoxLayout()
            self.analysis_page.setLayout(layout)

        title = QLabel("Co chcesz zrobić?")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")

        self.descriptive_button = QPushButton("Statystyka opisowa")
        self.descriptive_button.clicked.connect(self.show_descriptive_data_type_question)
        self.compare_groups_button = QPushButton("Porównanie grup pomiędzy sobą")
        self.compare_groups_button.clicked.connect(
            self.show_compare_groups_question_1
        )
        self.relationship_button = QPushButton("Badanie związku między grupami")

        self.descriptive_button.setMinimumHeight(50)
        self.compare_groups_button.setMinimumHeight(50)
        self.relationship_button.setMinimumHeight(50)

        self.analysis_table = QTableWidget()

        layout.addWidget(title)
        layout.addWidget(self.descriptive_button)
        layout.addWidget(self.compare_groups_button)
        layout.addWidget(self.relationship_button)
        layout.addStretch()

        self.analysis_page.setLayout(layout)

    def show_descriptive_data_type_question(self):


        layout = self.analysis_page.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        title = QLabel("Rodzaj danych:")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")

        quantitative_button = QPushButton("Dane ilościowe")
        qualitative_button = QPushButton("Dane jakościowe")
        quantitative_button.clicked.connect(
            lambda: self.show_variable_checkbox_list("ilościowe")
        )

        qualitative_button.clicked.connect(
            lambda: self.show_variable_checkbox_list("jakościowe")
        )

        quantitative_button.setMinimumHeight(50)
        qualitative_button.setMinimumHeight(50)

        layout.addWidget(title)
        layout.addWidget(quantitative_button)
        layout.addWidget(qualitative_button)
        layout.addStretch()

    def show_compare_groups_question_1(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Jaki charakter mają zmienne?")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        dependent_button = QPushButton("Zależne")
        independent_button = QPushButton("Niezależne")

        dependent_button.setMinimumHeight(50)
        independent_button.setMinimumHeight(50)

        dependent_button.clicked.connect(
            lambda: self.compare_groups_question_2(
                "dependent"
            )
        )

        independent_button.clicked.connect(
            lambda: self.compare_groups_question_2(
                "independent"
            )
        )

        layout.addWidget(title)
        layout.addWidget(dependent_button)
        layout.addWidget(independent_button)
        layout.addStretch()

    def compare_groups_question_2(self, dependency):
        self.compare_dependency = dependency

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Ile grup porównujesz?")
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
            padding:10px;
        """)

        two_groups_button = QPushButton("Tylko 2")
        more_groups_button = QPushButton("Więcej niż 2")

        two_groups_button.setMinimumHeight(50)
        more_groups_button.setMinimumHeight(50)

        two_groups_button.clicked.connect(
            lambda: self.compare_groups_question_3(2)
        )

        more_groups_button.clicked.connect(
            lambda: self.compare_groups_question_3(3)
        )

        layout.addWidget(title)
        layout.addWidget(two_groups_button)
        layout.addWidget(more_groups_button)
        layout.addStretch()

    def compare_groups_question_3(self, groups_count):
        self.compare_groups_count = groups_count

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Jaką masz zmienną zależną?")
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
            padding:10px;
        """)

        nominal_button = QPushButton("Nominalną")
        ordinal_button = QPushButton("Porządkową")
        quantitative_button = QPushButton("Ilościową")

        nominal_button.setMinimumHeight(50)
        ordinal_button.setMinimumHeight(50)
        quantitative_button.setMinimumHeight(50)

        nominal_button.clicked.connect(
            lambda: self.compare_groups_question_4("nominal")
        )

        ordinal_button.clicked.connect(
            lambda: self.compare_groups_question_4("ordinal")
        )

        quantitative_button.clicked.connect(
            lambda: self.compare_groups_question_4("quantitative")
        )

        layout.addWidget(title)
        layout.addWidget(nominal_button)
        layout.addWidget(ordinal_button)
        layout.addWidget(quantitative_button)
        layout.addStretch()

    def compare_groups_question_4(self, variable_type):
        self.compare_variable_type = variable_type

        if self.compare_dependency == "dependent":
            test_id = self.test_selector.select_dependent_test(
                groups_count=self.compare_groups_count,
                dependent_type=self.compare_variable_type,
            )

            if test_id == "dependent_normality_required":
                self.show_dependent_quantitative_normality()
                return

            display_names = {
                "mcnemar": "Test McNemara",
                "wilcoxon": "Test Wilcoxona",
                "cochran_q": "Test Q Cochrana",
                "friedman": "Test Friedmana",
            }

            display_name = display_names.get(test_id)

            if display_name is None:
                QMessageBox.warning(
                    self,
                    "Brak testu",
                    f"Nie znaleziono nazwy dla testu: {test_id}"
                )
                return

            self.show_dependent_test(
                test_id,
                display_name
            )
            return

        if self.compare_dependency != "independent":
            QMessageBox.warning(
                self,
                "Błąd wyboru",
                "Nie udało się rozpoznać charakteru grup."
            )
            return

        test_id = self.test_selector.select_independent_test(
            groups_count=self.compare_groups_count,
            dependent_type=self.compare_variable_type,
        )

        if test_id == "normality_required":
            self.show_independent_quantitative_normality()
            return

        display_names = {
            "chi_square": "Test Chi-kwadrat niezależności",
            "mann_whitney": "Test U Manna-Whitneya",
            "kruskal_wallis": "Test Kruskala-Wallisa",
        }

        display_name = display_names.get(test_id)

        if display_name is None:
            QMessageBox.warning(
                self,
                "Brak testu",
                f"Nie znaleziono nazwy dla testu: {test_id}"
            )
            return

        self.show_recommended_test(
            test_id,
            display_name
        )

    def show_independent_quantitative_normality(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Sprawdzenie normalności rozkładu")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz zmienną grupującą oraz zmienną ilościową. "
            "Program sprawdzi normalność rozkładu i automatycznie "
            "dobierze odpowiedni test statystyczny."
        )
        description.setWordWrap(True)

        self.normality_grouping_combo = QComboBox()
        self.normality_dependent_combo = QComboBox()

        numeric_columns, categorical_columns = (
            self.get_numeric_and_categorical_columns()
        )

        self.normality_grouping_combo.addItems(categorical_columns)
        self.normality_dependent_combo.addItems(numeric_columns)

        calculate_button = QPushButton(
            "Sprawdź normalność i dobierz test"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_independent_groups_normality
        )

        self.compare_normality_output = QTextEdit()
        self.compare_normality_output.setReadOnly(True)
        self.compare_normality_output.setMaximumHeight(220)

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            lambda: self.compare_groups_question_3(
                self.compare_groups_count
            )
        )

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Zmienna grupująca:"))
        layout.addWidget(self.normality_grouping_combo)

        layout.addWidget(QLabel("Zmienna zależna ilościowa:"))
        layout.addWidget(self.normality_dependent_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(self.compare_normality_output)
        layout.addWidget(back_button)
        layout.addStretch()

    def check_normality_for_dependent_variable(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            dependent_var = self.dependent_variable_combo.currentText()

            if dependent_var == "":
                self.normality_result_output.setText(
                    "Nie wybrano zmiennej zależnej."
                )
                return

            stats_engine = StatisticsEngine()
            result = stats_engine.normality_test(
                self.clean_df,
                dependent_var
            )

            if result is None:
                self.normality_result_output.setText(
                    "Nie udało się wykonać testu normalności."
                )
                return

            text = "=== TEST NORMALNOŚCI ROZKŁADU ===\n\n"
            text += f"Zmienna: {result['kolumna']}\n"
            text += f"Test: {result['test']}\n"
            text += f"Statystyka W: {result['statystyka_W']:.4f}\n"
            text += f"p-value: {result['p_value']:.4f}\n\n"
            text += result["interpretacja"]

            self.normality_result_output.setText(text)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd normalności",
                str(e)
            )

    def calculate_independent_groups_normality(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            grouping_var = self.normality_grouping_combo.currentText()
            dependent_var = self.normality_dependent_combo.currentText()

            if not grouping_var:
                QMessageBox.warning(
                    self,
                    "Brak zmiennej grupującej",
                    "Wybierz zmienną grupującą."
                )
                return

            if not dependent_var:
                QMessageBox.warning(
                    self,
                    "Brak zmiennej zależnej",
                    "Wybierz zmienną zależną."
                )
                return

            stats_engine = StatisticsEngine()

            normality_result = stats_engine.normality_test_by_groups(
                self.clean_df,
                grouping_var,
                dependent_var,
            )

            if normality_result is None:
                QMessageBox.warning(
                    self,
                    "Błąd normalności",
                    "Nie udało się wykonać testu normalności."
                )
                return

            number_of_groups = normality_result["number_of_groups"]
            all_groups_normal = normality_result["all_groups_normal"]

            variance_result = None

            if not all_groups_normal:
                test_id = self.test_selector.select_independent_test(
                    groups_count=number_of_groups,
                    dependent_type="quantitative",
                    normal=False,
                )
            else:
                variance_result = stats_engine.levene_test(
                    self.clean_df,
                    grouping_var,
                    dependent_var,
                )

                test_id = self.test_selector.select_independent_test(
                    groups_count=number_of_groups,
                    dependent_type="quantitative",
                    normal=True,
                    equal_variances=variance_result["equal_variances"],
                )

            display_names = {
                "t_independent": "Test t-Studenta dla prób niezależnych",
                "welch_t": "Test t Welcha dla prób niezależnych",
                "mann_whitney": "Test U Manna-Whitneya",
                "anova": "Jednoczynnikowa ANOVA",
                "welch_anova": "Jednoczynnikowa ANOVA Welcha",
                "kruskal_wallis": "Test Kruskala-Wallisa",
            }

            display_name = display_names.get(test_id, test_id)

            self.show_recommended_test(
                test_id,
                display_name
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd doboru testu",
                str(error)
            )
    def get_numeric_and_categorical_columns(self):
        numeric_columns = []
        categorical_columns = []

        if self.clean_df is None:
            return numeric_columns, categorical_columns

        for column in self.clean_df.columns:
            converted = pd.to_numeric(self.clean_df[column], errors="coerce")
            valid_ratio = converted.notna().sum() / len(converted)

            if valid_ratio >= 0.8:
                numeric_columns.append(column)
            else:
                categorical_columns.append(column)

        return numeric_columns, categorical_columns

    def show_recommended_test(self, test_id, display_name):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Rekomendowany test:")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        result_label = QLabel(display_name)
        result_label.setStyleSheet("""
            font-size: 20px;
            padding: 10px;
        """)
        result_label.setWordWrap(True)

        self.independent_variable_combo = QComboBox()
        self.dependent_variable_combo = QComboBox()

        if self.clean_df is not None:
            numeric_columns, categorical_columns = (
                self.get_numeric_and_categorical_columns()
            )

            if test_id == "chi_square":
                self.independent_variable_combo.addItems(
                    categorical_columns
                )
                self.dependent_variable_combo.addItems(
                    categorical_columns
                )

            elif test_id in [
                "mann_whitney",
                "t_independent",
                "anova",
                "kruskal_wallis",
            ]:
                self.independent_variable_combo.addItems(
                    categorical_columns
                )
                self.dependent_variable_combo.addItems(
                    numeric_columns
                )

            else:
                all_columns = list(self.clean_df.columns)

                self.independent_variable_combo.addItems(
                    all_columns
                )
                self.dependent_variable_combo.addItems(
                    all_columns
                )

        calculate_test_button = QPushButton("Oblicz statystyki")
        calculate_test_button.setMinimumHeight(45)
        calculate_test_button.clicked.connect(
            lambda: self.calculate_recommended_test(
                test_id,
                display_name
            )
        )

        add_test_to_report_button = QPushButton("Dodaj do raportu")
        add_test_to_report_button.setMinimumHeight(45)
        add_test_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.show_compare_groups_question_1
        )

        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(result_label)

        layout.addWidget(
            QLabel("Zmienna niezależna / grupująca:")
        )
        layout.addWidget(self.independent_variable_combo)

        layout.addWidget(QLabel("Zmienna zależna:"))
        layout.addWidget(self.dependent_variable_combo)

        layout.addWidget(calculate_test_button)
        layout.addWidget(add_test_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def show_dependent_test(
            self,
            test_id,
            display_name,
            selected_first_variable=None,
            selected_second_variable=None,
            information_text=None,
    ):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Rekomendowany test:")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        test_label = QLabel(display_name)
        test_label.setStyleSheet("""
            font-size: 20px;
            padding: 10px;
        """)

        test_label.setWordWrap(True)

        self.dependent_first_variable_combo = QComboBox()
        self.dependent_second_variable_combo = QComboBox()

        if self.clean_df is not None:
            numeric_columns, categorical_columns = (
                self.get_numeric_and_categorical_columns()
            )

            if test_id == "mcnemar":
                columns = categorical_columns
            else:
                columns = numeric_columns

            self.dependent_first_variable_combo.addItems(columns)
            self.dependent_second_variable_combo.addItems(columns)

            if self.dependent_second_variable_combo.count() > 1:
                self.dependent_second_variable_combo.setCurrentIndex(1)

        calculate_button = QPushButton("Oblicz statystyki")
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            lambda: self.calculate_dependent_test(
                test_id,
                display_name
            )
        )

        add_to_report_button = QPushButton("Dodaj do raportu")
        add_to_report_button.setMinimumHeight(45)
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.show_compare_groups_question_1
        )

        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(test_label)
        if information_text:
            information_output = QTextEdit()
            information_output.setReadOnly(True)
            information_output.setMaximumHeight(240)
            information_output.setText(information_text)
            layout.addWidget(information_output)

        layout.addWidget(QLabel("Pierwszy pomiar:"))
        layout.addWidget(self.dependent_first_variable_combo)

        layout.addWidget(QLabel("Drugi pomiar:"))
        layout.addWidget(self.dependent_second_variable_combo)
        if selected_first_variable:
            index = self.dependent_first_variable_combo.findText(
                selected_first_variable
            )

            if index >= 0:
                self.dependent_first_variable_combo.setCurrentIndex(
                    index
                )

        if selected_second_variable:
            index = self.dependent_second_variable_combo.findText(
                selected_second_variable
            )

            if index >= 0:
                self.dependent_second_variable_combo.setCurrentIndex(
                    index
                )

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_dependent_test(self, test_id, display_name):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            first_variable = (
                self.dependent_first_variable_combo.currentText()
            )

            second_variable = (
                self.dependent_second_variable_combo.currentText()
            )

            if not first_variable or not second_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz oba pomiary."
                )
                return

            if first_variable == second_variable:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Pierwszy i drugi pomiar muszą być różnymi kolumnami."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id,
                self.clean_df,
                first_variable,
                second_variable,
            )

            text = formatter.format(
                test_id,
                result,
                first_variable,
                second_variable,
            )

            self.current_analysis_result = text
            self.current_analysis_name = display_name

            self.recommended_test_output.setText(text)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd obliczeń",
                str(error)
            )

    def calculate_recommended_test(self, test_id, display_name):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            independent_var = self.independent_variable_combo.currentText()
            dependent_var = self.dependent_variable_combo.currentText()

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id,
                self.clean_df,
                independent_var,
                dependent_var
            )

            text = formatter.format(
                test_id,
                result,
                independent_var,
                dependent_var
            )

            self.current_analysis_result = text
            self.current_analysis_name = display_name

            self.recommended_test_output.setText(text)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd obliczeń",
                str(e)
            )

    def show_dependent_quantitative_normality(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Sprawdzenie normalności różnic")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz dwa pomiary. Program obliczy różnice między "
            "nimi, sprawdzi ich normalność i automatycznie wybierze "
            "test t dla prób zależnych albo test Wilcoxona."
        )
        description.setWordWrap(True)

        self.paired_normality_first_combo = QComboBox()
        self.paired_normality_second_combo = QComboBox()

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.paired_normality_first_combo.addItems(
            numeric_columns
        )

        self.paired_normality_second_combo.addItems(
            numeric_columns
        )

        if self.paired_normality_second_combo.count() > 1:
            self.paired_normality_second_combo.setCurrentIndex(1)

        calculate_button = QPushButton(
            "Sprawdź normalność i dobierz test"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_dependent_quantitative_normality
        )

        self.paired_normality_output = QTextEdit()
        self.paired_normality_output.setReadOnly(True)
        self.paired_normality_output.setMaximumHeight(220)

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            lambda: self.compare_groups_question_3(
                self.compare_groups_count
            )
        )

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Pierwszy pomiar:"))
        layout.addWidget(self.paired_normality_first_combo)

        layout.addWidget(QLabel("Drugi pomiar:"))
        layout.addWidget(self.paired_normality_second_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(self.paired_normality_output)
        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_dependent_quantitative_normality(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            first_variable = (
                self.paired_normality_first_combo.currentText()
            )

            second_variable = (
                self.paired_normality_second_combo.currentText()
            )

            if not first_variable or not second_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz oba pomiary."
                )
                return

            if first_variable == second_variable:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Wybierz dwie różne kolumny."
                )
                return

            stats_engine = StatisticsEngine()

            normality_result = (
                stats_engine.paired_differences_normality_test(
                    self.clean_df,
                    first_variable,
                    second_variable,
                )
            )

            test_id = self.test_selector.select_dependent_test(
                groups_count=2,
                dependent_type="quantitative",
                normal=normality_result["is_normal"],
            )

            display_names = {
                "t_paired": (
                    "Test t-Studenta dla prób zależnych"
                ),
                "wilcoxon": "Test Wilcoxona",
            }

            display_name = display_names.get(test_id)

            if display_name is None:
                raise ValueError(
                    f"Nie znaleziono nazwy testu: {test_id}"
                )

            normality_text = (
                "=== TEST NORMALNOŚCI RÓŻNIC ===\n\n"
                f"Pierwszy pomiar: {first_variable}\n"
                f"Drugi pomiar: {second_variable}\n"
                f"Liczba par: "
                f"{normality_result['sample_size']}\n\n"
                f"Statystyka W: "
                f"{normality_result['statistic']:.4f}\n"
                f"p-value: "
                f"{normality_result['p_value']:.4f}\n\n"
            )

            if normality_result["is_normal"]:
                normality_text += (
                    "Różnice mają rozkład zgodny z normalnym.\n"
                    "Wybrano test t dla prób zależnych."
                )
            else:
                normality_text += (
                    "Różnice odbiegają od rozkładu normalnego.\n"
                    "Wybrano test Wilcoxona."
                )

            self.show_dependent_test(
                test_id,
                display_name,
                selected_first_variable=first_variable,
                selected_second_variable=second_variable,
                information_text=normality_text,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd doboru testu",
                str(error)
            )


    def show_variable_checkbox_list(self, data_type):
        if self.clean_df is None:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Najpierw wczytaj plik w zakładce Dane."
            )
            return

        layout = self.analysis_page.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        title = QLabel("Wybierz z listy zmienne, dla których chcesz obliczyć statystyki:")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout()

        self.selected_variable_checkboxes = []

        for column in self.clean_df.columns:
            checkbox = QCheckBox(str(column))
            self.selected_variable_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch()
        scroll_content.setLayout(checkbox_layout)
        scroll_area.setWidget(scroll_content)

        calculate_button = QPushButton("Oblicz statystyki")
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            lambda: self.calculate_descriptive_statistics(data_type)
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(self.build_analysis_page)


        layout.addWidget(title)
        layout.addWidget(scroll_area)
        layout.addWidget(calculate_button)
        layout.addWidget(back_button)
        layout.addWidget(QLabel("Wyniki:"))

        self.analysis_table = QTableView()
        layout.addWidget(self.analysis_table)

        self.add_to_report_button = QPushButton("Dodaj wyniki do raportu")
        self.add_to_report_button.setMinimumHeight(40)
        self.add_to_report_button.clicked.connect(self.add_current_results_to_report)
        layout.addWidget(self.add_to_report_button)

    def calculate_descriptive_statistics(self, data_type):
        selected_columns = []

        for checkbox in self.selected_variable_checkboxes:
            if checkbox.isChecked():
                selected_columns.append(checkbox.text())

        if not selected_columns:
            QMessageBox.warning(
                self,
                "Brak wyboru",
                "Wybierz przynajmniej jedną zmienną."
            )
            return

        stats_engine = StatisticsEngine()

        if data_type == "ilościowe":
            result = stats_engine.descriptive_statistics_selected(
                self.clean_df,
                selected_columns
            )

            model = PandasTableModel(result)
            self.analysis_table.setModel(model)
            self.analysis_table.resizeColumnsToContents()

            self.analysis_table_model = model


        else:

            result = stats_engine.qualitative_statistics_selected(

                self.clean_df,

                selected_columns

            )

            model = PandasTableModel(result)

            self.analysis_table.setModel(model)

            self.analysis_table.resizeColumnsToContents()

            self.analysis_table_model = model

            self.current_analysis_result = result

            self.current_analysis_name = "Statystyki opisowe - dane jakościowe"

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

    def add_current_results_to_report(self):
        try:
            if not hasattr(self, "current_analysis_result"):
                QMessageBox.warning(
                    self,
                    "Brak wyników",
                    "Najpierw wykonaj analizę."
                )
                return

            with open(self.statistics_report_path, "a", encoding="utf-8") as file:
                file.write("\n\n=== DODANE WYNIKI ANALIZY ===\n")
                file.write(f"{self.current_analysis_name}\n")
                file.write("-------------------\n")

                if hasattr(self.current_analysis_result, "to_string"):
                    file.write(self.current_analysis_result.to_string(index=False))
                else:
                    file.write(str(self.current_analysis_result))

                file.write("\n")

            QMessageBox.information(
                self,
                "Zapisano",
                f"Wyniki dodano do raportu: {self.statistics_report_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd zapisu do raportu",
                str(e)
            )
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

    def clear_analysis_page(self):
        layout = self.analysis_page.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()