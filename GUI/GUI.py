import pandas as pd
import html

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QStackedWidget,
    QCheckBox, QScrollArea, QTableView
)
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPageSize

from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import (
    QTextDocument,
    QPageSize,
    QPageLayout,
    QFont,
)
from PyQt6.QtPrintSupport import QPrinter

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

        self.current_analysis_result = None
        self.current_analysis_name = None
        self.report_sections = []

        self.test_selector = TestSelector()

        self.huba_pdf_path = "reports/huba_report.pdf"
        self.clean_file_path = "dane_clean.xlsx"
        self.statistics_report_path = "statistics_report.txt"

        main_layout = QHBoxLayout()

        self.sidebar = QVBoxLayout()
        self.content = QStackedWidget()

        self.build_sidebar()
        self.build_pages()

        self.content.currentChanged.connect(
            self.handle_page_changed
        )

        main_layout.addLayout(self.sidebar, 1)
        main_layout.addWidget(self.content, 5)

        self.setLayout(main_layout)

    def handle_page_changed(self, index):
        current_page = self.content.widget(index)

        if current_page is self.reports_page:
            self.refresh_report_preview()

    def build_sidebar(self):
        title = QLabel("StatAnalyzer")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        self.sidebar.addWidget(title)

        buttons = [
            ("Dane", 0),
            ("Analiza", 1),
            ("Raporty", 2),
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
        self.reports_page = QWidget()

        self.build_data_page()
        self.build_analysis_page()
        self.build_reports_page()

        self.content.addWidget(self.data_page)
        self.content.addWidget(self.analysis_page)
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
        self.relationship_button.clicked.connect(
            self.show_relationship_variables_count_question
        )
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

    def show_relationship_variables_count_question(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Ile zmiennych chcesz analizować?")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        two_variables_button = QPushButton("Tylko 2")
        more_variables_button = QPushButton("Więcej niż 2")

        two_variables_button.setMinimumHeight(50)
        more_variables_button.setMinimumHeight(50)

        two_variables_button.clicked.connect(
            lambda: self.show_relationship_variable_types_question(2)
        )

        more_variables_button.clicked.connect(
            self.show_advanced_relationship_question
        )

        layout.addWidget(title)
        layout.addWidget(two_variables_button)
        layout.addWidget(more_variables_button)
        layout.addStretch()

    def show_advanced_relationship_question(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Jaką analizę chcesz wykonać?")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Analizy dla więcej niż dwóch zmiennych."
        )
        description.setWordWrap(True)

        linear_regression_button = QPushButton(
            "Regresja liniowa"
        )

        logistic_regression_button = QPushButton(
            "Regresja logistyczna"
        )

        mediation_button = QPushButton(
            "Mediacja"
        )

        moderation_button = QPushButton(
            "Moderacja"
        )

        buttons = [
            linear_regression_button,
            logistic_regression_button,
            mediation_button,
            moderation_button,
        ]

        for button in buttons:
            button.setMinimumHeight(50)

        linear_regression_button.clicked.connect(
            self.show_linear_regression_variables
        )

        logistic_regression_button.clicked.connect(
            self.show_logistic_regression_variables
        )

        mediation_button.clicked.connect(
            self.show_mediation_variables
        )

        moderation_button.clicked.connect(
            self.show_moderation_variables
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )
        layout.addWidget(title)
        layout.addWidget(description)

        for button in buttons:
            layout.addWidget(button)

        layout.addWidget(back_button)
        layout.addStretch()

    def show_analysis_not_ready(self, analysis_name):
        QMessageBox.information(
            self,
            "W budowie",
            f"{analysis_name} zostanie dodana "
            "w następnym etapie."
        )

    def calculate_moderation(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            independent_variable = (
                self.moderation_x_combo.currentText()
            )

            moderator_variable = (
                self.moderation_w_combo.currentText()
            )

            dependent_variable = (
                self.moderation_y_combo.currentText()
            )

            selected_variables = {
                independent_variable,
                moderator_variable,
                dependent_variable,
            }

            if "" in selected_variables:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz wszystkie trzy zmienne."
                )
                return

            if len(selected_variables) != 3:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "X, moderator W i Y muszą być różnymi kolumnami."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id="moderation",
                dataframe=self.clean_df,
                independent_var=independent_variable,
                dependent_var=dependent_variable,
                variables=[moderator_variable],
            )

            text = formatter.format(
                test_id="moderation",
                result=result,
                independent_var=independent_variable,
                dependent_var=dependent_variable,
            )

            self.current_analysis_result = text
            self.current_analysis_name = "Analiza moderacji"

            self.recommended_test_output.setText(text)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd analizy moderacji",
                str(error)
            )

    def show_moderation_variables(self):
        if self.clean_df is None:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Najpierw wczytaj plik."
            )
            return

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Analiza moderacji")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz zmienną niezależną X, moderator W oraz "
            "zmienną zależną Y. Wszystkie zmienne muszą być ilościowe."
        )
        description.setWordWrap(True)

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.moderation_x_combo = QComboBox()
        self.moderation_w_combo = QComboBox()
        self.moderation_y_combo = QComboBox()

        self.moderation_x_combo.addItems(numeric_columns)
        self.moderation_w_combo.addItems(numeric_columns)
        self.moderation_y_combo.addItems(numeric_columns)

        if self.moderation_w_combo.count() > 1:
            self.moderation_w_combo.setCurrentIndex(1)

        if self.moderation_y_combo.count() > 2:
            self.moderation_y_combo.setCurrentIndex(2)

        calculate_button = QPushButton(
            "Oblicz analizę moderacji"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_moderation
        )

        add_to_report_button = QPushButton(
            "Dodaj do raportu"
        )
        add_to_report_button.setMinimumHeight(45)
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )

        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Zmienna niezależna X:"))
        layout.addWidget(self.moderation_x_combo)

        layout.addWidget(QLabel("Moderator W:"))
        layout.addWidget(self.moderation_w_combo)

        layout.addWidget(QLabel("Zmienna zależna Y:"))
        layout.addWidget(self.moderation_y_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def show_mediation_variables(self):
        if self.clean_df is None:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Najpierw wczytaj plik."
            )
            return

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Analiza mediacji")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz zmienną niezależną X, mediator M oraz "
            "zmienną zależną Y. Wszystkie zmienne muszą być ilościowe."
        )
        description.setWordWrap(True)

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.mediation_x_combo = QComboBox()
        self.mediation_m_combo = QComboBox()
        self.mediation_y_combo = QComboBox()

        self.mediation_x_combo.addItems(numeric_columns)
        self.mediation_m_combo.addItems(numeric_columns)
        self.mediation_y_combo.addItems(numeric_columns)

        if self.mediation_m_combo.count() > 1:
            self.mediation_m_combo.setCurrentIndex(1)

        if self.mediation_y_combo.count() > 2:
            self.mediation_y_combo.setCurrentIndex(2)

        calculate_button = QPushButton(
            "Oblicz analizę mediacji"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_mediation
        )

        add_to_report_button = QPushButton(
            "Dodaj do raportu"
        )
        add_to_report_button.setMinimumHeight(45)
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )
        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Zmienna niezależna X:"))
        layout.addWidget(self.mediation_x_combo)

        layout.addWidget(QLabel("Mediator M:"))
        layout.addWidget(self.mediation_m_combo)

        layout.addWidget(QLabel("Zmienna zależna Y:"))
        layout.addWidget(self.mediation_y_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_mediation(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            independent_variable = (
                self.mediation_x_combo.currentText()
            )

            mediator_variable = (
                self.mediation_m_combo.currentText()
            )

            dependent_variable = (
                self.mediation_y_combo.currentText()
            )

            selected_variables = {
                independent_variable,
                mediator_variable,
                dependent_variable,
            }

            if "" in selected_variables:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz wszystkie trzy zmienne."
                )
                return

            if len(selected_variables) != 3:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Zmienna X, mediator M i zmienna Y "
                    "muszą być różnymi kolumnami."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id="mediation",
                dataframe=self.clean_df,
                independent_var=independent_variable,
                dependent_var=dependent_variable,
                variables=[mediator_variable],
            )

            text = formatter.format(
                test_id="mediation",
                result=result,
                independent_var=independent_variable,
                dependent_var=dependent_variable,
            )

            self.current_analysis_result = text
            self.current_analysis_name = "Analiza mediacji"

            self.recommended_test_output.setText(text)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd analizy mediacji",
                str(error)
            )

    def show_logistic_regression_variables(self):
        if self.clean_df is None:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Najpierw wczytaj plik."
            )
            return

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Regresja logistyczna")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz binarną zmienną zależną, czyli kolumnę "
            "zawierającą dokładnie dwie kategorie, oraz co najmniej "
            "dwie ilościowe zmienne niezależne."
        )
        description.setWordWrap(True)

        # Kolumny z dokładnie dwiema niepustymi wartościami.
        binary_columns = [
            column
            for column in self.clean_df.columns
            if self.clean_df[column].dropna().nunique() == 2
        ]

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.logistic_dependent_combo = QComboBox()
        self.logistic_dependent_combo.addItems(binary_columns)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout()

        self.logistic_predictor_checkboxes = []

        for column in numeric_columns:
            checkbox = QCheckBox(str(column))
            self.logistic_predictor_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch()
        scroll_content.setLayout(checkbox_layout)
        scroll_area.setWidget(scroll_content)

        calculate_button = QPushButton(
            "Oblicz regresję logistyczną"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_logistic_regression
        )

        add_to_report_button = QPushButton(
            "Dodaj do raportu"
        )
        add_to_report_button.setMinimumHeight(45)
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )
        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Binarna zmienna zależna:"))
        layout.addWidget(self.logistic_dependent_combo)

        layout.addWidget(QLabel("Zmienne niezależne:"))
        layout.addWidget(scroll_area)

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_logistic_regression(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            dependent_variable = (
                self.logistic_dependent_combo.currentText()
            )

            independent_variables = [
                checkbox.text()
                for checkbox in self.logistic_predictor_checkboxes
                if checkbox.isChecked()
            ]

            if not dependent_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennej zależnej",
                    "Nie znaleziono lub nie wybrano binarnej "
                    "zmiennej zależnej."
                )
                return

            if dependent_variable in independent_variables:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Zmienna zależna nie może być jednocześnie "
                    "zmienną niezależną."
                )
                return

            if len(independent_variables) < 2:
                QMessageBox.warning(
                    self,
                    "Za mało predyktorów",
                    "Wybierz co najmniej dwie zmienne niezależne."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id="logistic_regression",
                dataframe=self.clean_df,
                dependent_var=dependent_variable,
                variables=independent_variables,
            )

            text = formatter.format(
                test_id="logistic_regression",
                result=result,
                independent_var=independent_variables,
                dependent_var=dependent_variable,
            )

            self.current_analysis_result = text
            self.current_analysis_name = (
                "Regresja logistyczna"
            )

            self.recommended_test_output.setText(text)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd regresji logistycznej",
                str(error)
            )


    def show_linear_regression_variables(self):
        if self.clean_df is None:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Najpierw wczytaj plik."
            )
            return

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Regresja liniowa")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz jedną ilościową zmienną zależną oraz "
            "co najmniej dwie ilościowe zmienne niezależne."
        )
        description.setWordWrap(True)

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.regression_dependent_combo = QComboBox()
        self.regression_dependent_combo.addItems(
            numeric_columns
        )

        predictors_label = QLabel(
            "Zmienne niezależne:"
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout()

        self.regression_predictor_checkboxes = []

        for column in numeric_columns:
            checkbox = QCheckBox(str(column))
            self.regression_predictor_checkboxes.append(
                checkbox
            )
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch()
        scroll_content.setLayout(checkbox_layout)
        scroll_area.setWidget(scroll_content)

        calculate_button = QPushButton(
            "Oblicz regresję liniową"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_linear_regression
        )

        add_to_report_button = QPushButton(
            "Dodaj do raportu"
        )
        add_to_report_button.setMinimumHeight(45)
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )

        self.recommended_test_output = QTextEdit()
        self.recommended_test_output.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(
            QLabel("Zmienna zależna:")
        )
        layout.addWidget(
            self.regression_dependent_combo
        )

        layout.addWidget(predictors_label)
        layout.addWidget(scroll_area)

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)

        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)

        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_linear_regression(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            dependent_variable = (
                self.regression_dependent_combo.currentText()
            )

            independent_variables = [
                checkbox.text()
                for checkbox
                in self.regression_predictor_checkboxes
                if checkbox.isChecked()
            ]

            if not dependent_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennej zależnej",
                    "Wybierz zmienną zależną."
                )
                return

            if dependent_variable in independent_variables:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Zmienna zależna nie może być jednocześnie "
                    "zmienną niezależną."
                )
                return

            if len(independent_variables) < 2:
                QMessageBox.warning(
                    self,
                    "Za mało zmiennych",
                    "Wybierz co najmniej dwie "
                    "zmienne niezależne."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id="linear_regression",
                dataframe=self.clean_df,
                dependent_var=dependent_variable,
                variables=independent_variables,
            )

            text = formatter.format(
                test_id="linear_regression",
                result=result,
                independent_var=independent_variables,
                dependent_var=dependent_variable,
            )

            self.current_analysis_result = text
            self.current_analysis_name = (
                "Regresja liniowa"
            )

            self.recommended_test_output.setText(text)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd regresji liniowej",
                str(error)
            )

    def show_mixed_relationship_question(self, mixed_type):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Wybierz zmienne")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        self.mixed_relationship_type = mixed_type

        self.mixed_nominal_combo = QComboBox()
        self.mixed_second_combo = QComboBox()

        numeric_columns, categorical_columns = (
            self.get_numeric_and_categorical_columns()
        )

        self.mixed_nominal_combo.addItems(categorical_columns)

        if mixed_type == "nominal_quantitative":
            self.mixed_second_combo.addItems(numeric_columns)
            second_label = "Zmienna ilościowa:"
        elif mixed_type == "nominal_ordinal":
            self.mixed_second_combo.addItems(numeric_columns)
            second_label = "Zmienna porządkowa:"
        else:
            QMessageBox.warning(
                self,
                "Błąd",
                "Nieznany typ analizy mieszanej."
            )
            return

        calculate_button = QPushButton(
            "Dobierz odpowiedni test"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_mixed_relationship_test
        )

        back_button = QPushButton("Wstecz")
        back_button.clicked.connect(
            self.return_to_analysis_start
        )

        layout.addWidget(title)
        layout.addWidget(QLabel("Zmienna nominalna / grupująca:"))
        layout.addWidget(self.mixed_nominal_combo)
        layout.addWidget(QLabel(second_label))
        layout.addWidget(self.mixed_second_combo)
        layout.addWidget(calculate_button)
        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_mixed_relationship_test(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            grouping_var = self.mixed_nominal_combo.currentText()
            dependent_var = self.mixed_second_combo.currentText()

            if not grouping_var or not dependent_var:
                QMessageBox.warning(
                    self,
                    "Brak wyboru",
                    "Wybierz obie zmienne."
                )
                return

            groups_count = (
                self.clean_df[grouping_var]
                .dropna()
                .nunique()
            )

            if groups_count < 2:
                QMessageBox.warning(
                    self,
                    "Za mało grup",
                    "Zmienna nominalna musi zawierać co najmniej dwie grupy."
                )
                return

            if self.mixed_relationship_type == "nominal_ordinal":
                if groups_count == 2:
                    test_id = "mann_whitney"
                    display_name = "Test U Manna-Whitneya"
                else:
                    test_id = "kruskal_wallis"
                    display_name = "Test Kruskala-Wallisa"

                self.show_recommended_test(
                    test_id=test_id,
                    display_name=display_name,
                    selected_independent_var=grouping_var,
                    selected_dependent_var=dependent_var,
                )
                return

            stats_engine = StatisticsEngine()

            normality_result = stats_engine.normality_test_by_groups(
                self.clean_df,
                grouping_var,
                dependent_var,
            )

            if not normality_result["all_groups_normal"]:
                if groups_count == 2:
                    test_id = "mann_whitney"
                    display_name = "Test U Manna-Whitneya"
                else:
                    test_id = "kruskal_wallis"
                    display_name = "Test Kruskala-Wallisa"

            else:
                variance_result = stats_engine.levene_test(
                    self.clean_df,
                    grouping_var,
                    dependent_var,
                )

                if groups_count == 2:
                    if variance_result["equal_variances"]:
                        test_id = "t_independent"
                        display_name = (
                            "Test t-Studenta dla prób niezależnych"
                        )
                    else:
                        test_id = "welch_t"
                        display_name = (
                            "Test t Welcha dla prób niezależnych"
                        )
                else:
                    if variance_result["equal_variances"]:
                        test_id = "anova"
                        display_name = "Jednoczynnikowa ANOVA"
                    else:
                        test_id = "welch_anova"
                        display_name = "Jednoczynnikowa ANOVA Welcha"

            information_text = self.build_mixed_relationship_information(
                grouping_var=grouping_var,
                dependent_var=dependent_var,
                groups_count=groups_count,
                normality_result=normality_result,
                variance_result=(
                    variance_result
                    if normality_result["all_groups_normal"]
                    else None
                ),
                display_name=display_name,
            )

            self.show_recommended_test(
                test_id=test_id,
                display_name=display_name,
                selected_independent_var=grouping_var,
                selected_dependent_var=dependent_var,
                information_text=information_text,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd doboru testu",
                str(error)
            )

    def build_mixed_relationship_information(
            self,
            grouping_var,
            dependent_var,
            groups_count,
            normality_result,
            variance_result,
            display_name,
    ):
        lines = [
            "=== DOBÓR TESTU DLA ZMIENNYCH MIESZANYCH ===",
            "",
            f"Zmienna nominalna: {grouping_var}",
            f"Zmienna ilościowa: {dependent_var}",
            f"Liczba grup: {groups_count}",
            "",
            "TESTY NORMALNOŚCI:",
        ]

        for group_name, group_result in normality_result["groups"].items():
            lines.append("")
            lines.append(f"Grupa: {group_name}")
            lines.append(
                f"Liczebność: {group_result['sample_size']}"
            )

            if group_result["p_value"] is None:
                lines.append(
                    "Nie udało się ocenić normalności."
                )
            else:
                lines.append(
                    f"W = {group_result['statistic']:.4f}"
                )
                lines.append(
                    f"p-value = {group_result['p_value']:.4f}"
                )

        if variance_result is not None:
            lines.extend([
                "",
                "TEST LEVENE’A:",
                f"Statystyka = {variance_result['statistic']:.4f}",
                f"p-value = {variance_result['p_value']:.4f}",
            ])

        lines.extend([
            "",
            f"Rekomendowany test: {display_name}",
        ])

        return "\n".join(lines)

    def show_advanced_relationship_not_ready(self):
        QMessageBox.information(
            self,
            "W budowie",
            "Analizy dla więcej niż dwóch zmiennych "
            "zostaną dodane w kolejnym etapie."
        )


    def show_relationship_variable_types_question(self, variables_count):
        self.relationship_variables_count = variables_count

        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Jakie masz zmienne?")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        both_quantitative_button = QPushButton(
            "Obie ilościowe"
        )

        both_ordinal_button = QPushButton(
            "Obie porządkowe"
        )

        both_nominal_button = QPushButton(
            "Obie nominalne"
        )

        ordinal_quantitative_button = QPushButton(
            "Porządkowa i ilościowa"
        )

        nominal_quantitative_button = QPushButton(
            "Nominalna i ilościowa"
        )

        nominal_ordinal_button = QPushButton(
            "Nominalna i porządkowa"
        )

        buttons = [
            both_quantitative_button,
            both_ordinal_button,
            both_nominal_button,
            ordinal_quantitative_button,
            nominal_quantitative_button,
            nominal_ordinal_button,
        ]

        for button in buttons:
            button.setMinimumHeight(48)

        both_quantitative_button.clicked.connect(
            self.show_quantitative_relationship_normality
        )

        both_ordinal_button.clicked.connect(
            lambda: self.show_relationship_test(
                test_id="spearman",
                display_name="Współczynnik korelacji Spearmana",
                variable_type="numeric",
            )
        )

        both_nominal_button.clicked.connect(
            lambda: self.show_relationship_test(
                test_id="chi_square_relationship",
                display_name=(
                    "Test Chi-kwadrat niezależności "
                    "z V Craméra"
                ),
                variable_type="categorical",
            )
        )

        ordinal_quantitative_button.clicked.connect(
            lambda: self.show_relationship_test(
                test_id="spearman",
                display_name="Współczynnik korelacji Spearmana",
                variable_type="numeric",
            )
        )

        nominal_quantitative_button.clicked.connect(
            lambda: self.show_mixed_relationship_question(
                mixed_type="nominal_quantitative"
            )
        )

        nominal_ordinal_button.clicked.connect(
            lambda: self.show_mixed_relationship_question(
                mixed_type="nominal_ordinal"
            )
        )

        layout.addWidget(title)

        for button in buttons:
            layout.addWidget(button)

        layout.addStretch()

    def show_quantitative_relationship_normality(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Sprawdzenie normalności rozkładów")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz dwie zmienne ilościowe. "
            "Program sprawdzi normalność obu zmiennych "
            "i automatycznie wybierze korelację Pearsona "
            "albo Spearmana."
        )
        description.setWordWrap(True)

        self.relationship_first_combo = QComboBox()
        self.relationship_second_combo = QComboBox()

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        self.relationship_first_combo.addItems(numeric_columns)
        self.relationship_second_combo.addItems(numeric_columns)

        if self.relationship_second_combo.count() > 1:
            self.relationship_second_combo.setCurrentIndex(1)

        calculate_button = QPushButton(
            "Sprawdź normalność i dobierz test"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_relationship_normality
        )

        back_button = QPushButton("Wstecz")
        back_button.clicked.connect(
            self.return_to_analysis_start
        )

        layout.addWidget(title)
        layout.addWidget(description)

        layout.addWidget(QLabel("Pierwsza zmienna:"))
        layout.addWidget(self.relationship_first_combo)

        layout.addWidget(QLabel("Druga zmienna:"))
        layout.addWidget(self.relationship_second_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_relationship_normality(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            first_variable = (
                self.relationship_first_combo.currentText()
            )
            second_variable = (
                self.relationship_second_combo.currentText()
            )

            if not first_variable or not second_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz dwie zmienne."
                )
                return

            if first_variable == second_variable:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Wybierz dwie różne zmienne."
                )
                return

            stats_engine = StatisticsEngine()

            first_result = stats_engine.normality_test(
                self.clean_df,
                first_variable
            )

            second_result = stats_engine.normality_test(
                self.clean_df,
                second_variable
            )

            if first_result is None or second_result is None:
                raise ValueError(
                    "Nie udało się sprawdzić normalności."
                )

            both_normal = (
                    first_result["rozkład_normalny"]
                    and second_result["rozkład_normalny"]
            )

            if both_normal:
                test_id = "pearson"
                display_name = (
                    "Współczynnik korelacji Pearsona"
                )
            else:
                test_id = "spearman"
                display_name = (
                    "Współczynnik korelacji Spearmana"
                )

            information_text = (
                "=== TESTY NORMALNOŚCI ===\n\n"
                f"{first_variable}:\n"
                f"W = {first_result['statystyka_W']:.4f}\n"
                f"p-value = {first_result['p_value']:.4f}\n\n"
                f"{second_variable}:\n"
                f"W = {second_result['statystyka_W']:.4f}\n"
                f"p-value = {second_result['p_value']:.4f}\n\n"
                f"Rekomendowany test: {display_name}"
            )

            self.show_relationship_test(
                test_id=test_id,
                display_name=display_name,
                variable_type="numeric",
                selected_first_variable=first_variable,
                selected_second_variable=second_variable,
                information_text=information_text,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd doboru testu",
                str(error)
            )

    def show_relationship_test(
            self,
            test_id,
            display_name,
            variable_type,
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

        self.relationship_test_first_combo = QComboBox()
        self.relationship_test_second_combo = QComboBox()

        numeric_columns, categorical_columns = (
            self.get_numeric_and_categorical_columns()
        )

        if variable_type == "numeric":
            columns = numeric_columns
        else:
            columns = categorical_columns

        self.relationship_test_first_combo.addItems(columns)
        self.relationship_test_second_combo.addItems(columns)

        if self.relationship_test_second_combo.count() > 1:
            self.relationship_test_second_combo.setCurrentIndex(1)

        if selected_first_variable:
            index = self.relationship_test_first_combo.findText(
                selected_first_variable
            )

            if index >= 0:
                self.relationship_test_first_combo.setCurrentIndex(index)

        if selected_second_variable:
            index = self.relationship_test_second_combo.findText(
                selected_second_variable
            )

            if index >= 0:
                self.relationship_test_second_combo.setCurrentIndex(index)

        calculate_button = QPushButton("Oblicz statystyki")
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            lambda: self.calculate_relationship_test(
                test_id,
                display_name
            )
        )

        add_to_report_button = QPushButton("Dodaj do raportu")
        add_to_report_button.clicked.connect(
            self.add_current_results_to_report
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

        layout.addWidget(QLabel("Pierwsza zmienna:"))
        layout.addWidget(self.relationship_test_first_combo)

        layout.addWidget(QLabel("Druga zmienna:"))
        layout.addWidget(self.relationship_test_second_combo)

        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)
        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)
        layout.addStretch()

    def calculate_relationship_test(
            self,
            test_id,
            display_name,
    ):
        try:
            first_variable = (
                self.relationship_test_first_combo.currentText()
            )

            second_variable = (
                self.relationship_test_second_combo.currentText()
            )

            if not first_variable or not second_variable:
                QMessageBox.warning(
                    self,
                    "Brak zmiennych",
                    "Wybierz dwie zmienne."
                )
                return

            if first_variable == second_variable:
                QMessageBox.warning(
                    self,
                    "Nieprawidłowy wybór",
                    "Wybierz dwie różne zmienne."
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

        # =========================================
        # PRÓBY ZALEŻNE
        # =========================================
        if self.compare_dependency == "dependent":
            test_id = self.test_selector.select_dependent_test(
                groups_count=self.compare_groups_count,
                dependent_type=self.compare_variable_type,
            )

            # Dla danych ilościowych trzeba najpierw sprawdzić normalność.
            if test_id == "dependent_normality_required":
                if self.compare_groups_count == 2:
                    self.show_dependent_quantitative_normality()
                else:
                    self.show_multiple_dependent_quantitative_normality()

                return

            display_names = {
                "mcnemar": "Test McNemara",
                "wilcoxon": "Test Wilcoxona",
                "cochran_q": "Test Q Cochrana",
                "friedman": "Test Friedmana",
                "t_paired": "Test t-Studenta dla prób zależnych",
                "repeated_measures_anova": (
                    "ANOVA z powtarzanymi pomiarami"
                ),
            }

            display_name = display_names.get(test_id)

            if display_name is None:
                QMessageBox.warning(
                    self,
                    "Brak testu",
                    f"Nie znaleziono nazwy dla testu: {test_id}"
                )
                return

            # Dwa pomiary zależne.
            if self.compare_groups_count == 2:
                self.show_dependent_test(
                    test_id,
                    display_name
                )

            # Więcej niż dwa pomiary zależne.
            else:
                self.show_multiple_dependent_test(
                    test_id,
                    display_name
                )

            return

        # =========================================
        # PRÓBY NIEZALEŻNE
        # =========================================
        if self.compare_dependency == "independent":
            test_id = self.test_selector.select_independent_test(
                groups_count=self.compare_groups_count,
                dependent_type=self.compare_variable_type,
            )

            # Dla danych ilościowych trzeba najpierw sprawdzić
            # normalność i jednorodność wariancji.
            if test_id == "normality_required":
                self.show_independent_quantitative_normality()
                return

            display_names = {
                "chi_square": "Test Chi-kwadrat niezależności",
                "mann_whitney": "Test U Manna-Whitneya",
                "kruskal_wallis": "Test Kruskala-Wallisa",
                "t_independent": (
                    "Test t-Studenta dla prób niezależnych"
                ),
                "welch_t": (
                    "Test t Welcha dla prób niezależnych"
                ),
                "anova": "Jednoczynnikowa ANOVA",
                "welch_anova": "Jednoczynnikowa ANOVA Welcha",
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
            return

        # =========================================
        # NIEPRAWIDŁOWY STAN KREATORA
        # =========================================
        QMessageBox.warning(
            self,
            "Błąd wyboru",
            "Nie udało się rozpoznać charakteru grup."
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
            self.return_to_analysis_start
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

    def show_recommended_test(
            self,
            test_id,
            display_name,
            selected_independent_var=None,
            selected_dependent_var=None,
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
            self.return_to_analysis_start
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
            self.return_to_analysis_start
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
            self.return_to_analysis_start
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

    def show_multiple_dependent_test(
            self,
            test_id,
            display_name,
            selected_variables=None,
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

        instruction = QLabel(
            "Wybierz co najmniej trzy kolumny odpowiadające "
            "kolejnym pomiarom tych samych osób."
        )
        instruction.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout()

        self.multiple_dependent_checkboxes = []

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        # Test Q Cochrana wymaga kolumn binarnych.
        if test_id == "cochran_q":
            columns = [
                column
                for column in self.clean_df.columns
                if self.clean_df[column].dropna().nunique() == 2
            ]

        # Friedman i ANOVA RM korzystają z kolumn liczbowych.
        else:
            columns = numeric_columns

        for column in columns:
            checkbox = QCheckBox(str(column))
            self.multiple_dependent_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)

        # Ponownie zaznacza zmienne wybrane na ekranie normalności.
        if selected_variables:
            selected_set = set(selected_variables)

            for checkbox in self.multiple_dependent_checkboxes:
                checkbox.setChecked(
                    checkbox.text() in selected_set
                )

        checkbox_layout.addStretch()
        scroll_content.setLayout(checkbox_layout)
        scroll_area.setWidget(scroll_content)

        calculate_button = QPushButton("Oblicz statystyki")
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            lambda: self.calculate_multiple_dependent_test(
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
            self.return_to_analysis_start
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

        layout.addWidget(instruction)
        layout.addWidget(scroll_area)
        layout.addWidget(calculate_button)
        layout.addWidget(add_to_report_button)
        layout.addWidget(QLabel("Wyniki:"))
        layout.addWidget(self.recommended_test_output)
        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_multiple_dependent_test(
            self,
            test_id,
            display_name,
    ):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            selected_variables = [
                checkbox.text()
                for checkbox in self.multiple_dependent_checkboxes
                if checkbox.isChecked()
            ]

            if len(selected_variables) < 3:
                QMessageBox.warning(
                    self,
                    "Za mało pomiarów",
                    "Wybierz co najmniej trzy pomiary."
                )
                return

            stats_engine = StatisticsEngine()
            formatter = ReportFormatter()

            result = stats_engine.run_test(
                test_id=test_id,
                dataframe=self.clean_df,
                variables=selected_variables,
            )

            text = formatter.format(
                test_id,
                result,
                None,
                None,
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

        try:
            stats_engine = StatisticsEngine()

            if data_type == "ilościowe":
                result = stats_engine.descriptive_statistics_selected(
                    self.clean_df,
                    selected_columns
                )

                analysis_name = (
                    "Statystyki opisowe — dane ilościowe"
                )

            else:
                result = stats_engine.qualitative_statistics_selected(
                    self.clean_df,
                    selected_columns
                )

                analysis_name = (
                    "Statystyki opisowe — dane jakościowe"
                )

            if result is None or result.empty:
                QMessageBox.warning(
                    self,
                    "Brak wyników",
                    "Nie udało się obliczyć statystyk "
                    "dla wybranych zmiennych."
                )
                return

            model = PandasTableModel(result)
            self.analysis_table.setModel(model)
            self.analysis_table.resizeColumnsToContents()

            # Zachowuje model, aby nie został usunięty z pamięci.
            self.analysis_table_model = model

            # Te linie są konieczne do dodawania wyniku do raportu.
            self.current_analysis_result = result
            self.current_analysis_name = analysis_name

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd statystyk opisowych",
                str(error)
            )

    def return_to_analysis_start(self):
        self.build_analysis_page()

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

    def refresh_report_preview(self):
        if not hasattr(self, "report_preview"):
            return

        if not self.report_sections:
            self.report_preview.clear()
            self.report_preview.setPlaceholderText(
                "Raport jest pusty.\n"
                "Wykonaj analizę i kliknij „Dodaj do raportu”."
            )
            return

        report_content = "<hr>".join(
            self.report_sections
        )

        report_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 10pt;
                    margin: 0;
                    padding: 8px;
                }}

                h1 {{
                    font-size: 18pt;
                    margin-bottom: 12px;
                }}

                h2 {{
                    font-size: 15pt;
                    margin-bottom: 4px;
                }}

                h3 {{
                    font-size: 12pt;
                    margin-top: 0;
                    margin-bottom: 14px;
                }}

                .report-section {{
                    margin-bottom: 24px;
                }}

                table.report-table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 10px;
                    margin-bottom: 18px;
                    font-size: 9pt;
                }}

                table.report-table th {{
                    font-weight: bold;
                    padding: 5px;
                    border: 1px solid #555;
                    text-align: center;
                }}

                table.report-table td {{
                    padding: 5px;
                    border: 1px solid #777;
                    text-align: center;
                }}

                pre {{
                    white-space: pre-wrap;
                    font-family: Consolas, monospace;
                    font-size: 9pt;
                }}

                hr {{
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>

        <body>
            <h1>Raport statystyczny</h1>
            {report_content}
        </body>
        </html>
        """
        self.report_preview.setHtml(report_html)

    def build_reports_page(self):
        layout = QVBoxLayout()

        title = QLabel("Podgląd raportu")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setPlaceholderText(
            "Raport jest pusty.\n"
            "Wykonaj analizę i kliknij „Dodaj do raportu”."
        )
        self.report_preview.setMinimumHeight(450)

        refresh_button = QPushButton(
            "Odśwież podgląd"
        )
        refresh_button.setMinimumHeight(40)
        refresh_button.clicked.connect(
            self.refresh_report_preview
        )

        export_pdf_button = QPushButton(
            "Zapisz raport jako PDF"
        )
        export_pdf_button.setMinimumHeight(45)
        export_pdf_button.clicked.connect(
            self.export_report_to_pdf
        )

        layout.addWidget(title)
        layout.addWidget(self.report_preview)
        layout.addWidget(refresh_button)
        layout.addWidget(export_pdf_button)

        self.reports_page.setLayout(layout)

    def export_report_to_pdf(self):
        try:
            if not self.report_sections:
                QMessageBox.warning(
                    self,
                    "Raport jest pusty",
                    "Najpierw dodaj przynajmniej jeden wynik "
                    "do raportu."
                )
                return

            self.refresh_report_preview()

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Zapisz raport jako PDF",
                "raport_statystyczny.pdf",
                "Pliki PDF (*.pdf)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            # ScreenResolution zapobiega bardzo małemu tekstowi.
            printer = QPrinter(
                QPrinter.PrinterMode.ScreenResolution
            )

            printer.setOutputFormat(
                QPrinter.OutputFormat.PdfFormat
            )
            printer.setOutputFileName(file_path)

            page_layout = QPageLayout(
                QPageSize(QPageSize.PageSizeId.A4),
                QPageLayout.Orientation.Portrait,
                QMarginsF(15, 15, 15, 15),
                QPageLayout.Unit.Millimeter,
            )

            printer.setPageLayout(page_layout)

            document = QTextDocument()

            default_font = QFont("Arial")
            default_font.setPointSize(10)
            document.setDefaultFont(default_font)

            # Pobiera pełny sformatowany raport z podglądu.
            document.setHtml(
                self.report_preview.toHtml()
            )

            # Dopasowuje szerokość dokumentu do obszaru strony A4.
            page_rectangle = printer.pageRect(
                QPrinter.Unit.Point
            )
            document.setPageSize(
                page_rectangle.size()
            )

            document.print(printer)

            QMessageBox.information(
                self,
                "Raport zapisany",
                "Raport został poprawnie zapisany:\n\n"
                f"{file_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd zapisu PDF",
                "Nie udało się zapisać raportu.\n\n"
                f"{error}"
            )

    def show_multiple_dependent_quantitative_normality(self):
        self.clear_analysis_page()
        layout = self.analysis_page.layout()

        title = QLabel("Sprawdzenie założeń analizy")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
        """)

        description = QLabel(
            "Wybierz co najmniej trzy pomiary ilościowe. "
            "Program sprawdzi normalność reszt i automatycznie "
            "wybierze ANOVA z powtarzanymi pomiarami albo "
            "test Friedmana."
        )
        description.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout()

        self.multiple_normality_checkboxes = []

        numeric_columns, _ = (
            self.get_numeric_and_categorical_columns()
        )

        for column in numeric_columns:
            checkbox = QCheckBox(str(column))
            self.multiple_normality_checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch()
        scroll_content.setLayout(checkbox_layout)
        scroll_area.setWidget(scroll_content)

        calculate_button = QPushButton(
            "Sprawdź normalność i dobierz test"
        )
        calculate_button.setMinimumHeight(45)
        calculate_button.clicked.connect(
            self.calculate_multiple_dependent_normality
        )

        back_button = QPushButton("Wstecz")
        back_button.setMinimumHeight(40)
        back_button.clicked.connect(
            self.return_to_analysis_start
        )
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(scroll_area)
        layout.addWidget(calculate_button)
        layout.addWidget(back_button)
        layout.addStretch()

    def calculate_multiple_dependent_normality(self):
        try:
            if self.clean_df is None:
                QMessageBox.warning(
                    self,
                    "Brak danych",
                    "Najpierw wczytaj plik."
                )
                return

            selected_variables = [
                checkbox.text()
                for checkbox in self.multiple_normality_checkboxes
                if checkbox.isChecked()
            ]

            if len(selected_variables) < 3:
                QMessageBox.warning(
                    self,
                    "Za mało pomiarów",
                    "Wybierz co najmniej trzy pomiary."
                )
                return

            stats_engine = StatisticsEngine()

            normality_result = (
                stats_engine.repeated_measures_normality_test(
                    self.clean_df,
                    selected_variables,
                )
            )

            test_id = self.test_selector.select_dependent_test(
                groups_count=3,
                dependent_type="quantitative",
                normal=normality_result["is_normal"],
            )

            display_names = {
                "repeated_measures_anova": (
                    "ANOVA z powtarzanymi pomiarami"
                ),
                "friedman": "Test Friedmana",
            }

            display_name = display_names.get(test_id)

            if display_name is None:
                raise ValueError(
                    f"Nie znaleziono nazwy testu: {test_id}"
                )

            normality_text = (
                "=== TEST NORMALNOŚCI RESZT ===\n\n"
                f"Pomiary: {', '.join(selected_variables)}\n"
                f"Liczba pomiarów: "
                f"{normality_result['liczba_pomiarow']}\n"
                f"Liczba kompletnych przypadków: "
                f"{normality_result['liczba_kompletnych_przypadkow']}\n\n"
                f"W = {normality_result['statystyka_W']:.4f}\n"
                f"p-value = {normality_result['p_value']:.4f}\n\n"
            )

            if normality_result["is_normal"]:
                normality_text += (
                    "Reszty mają rozkład zgodny z normalnym.\n"
                    "Wybrano ANOVA z powtarzanymi pomiarami."
                )
            else:
                normality_text += (
                    "Reszty odbiegają od rozkładu normalnego.\n"
                    "Wybrano test Friedmana."
                )

            self.show_multiple_dependent_test(
                test_id=test_id,
                display_name=display_name,
                selected_variables=selected_variables,
                information_text=normality_text,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Błąd doboru testu",
                str(error)
            )

    def add_current_results_to_report(self):
        if self.current_analysis_result is None:
            QMessageBox.warning(
                self,
                "Brak wyników",
                "Najpierw wykonaj analizę."
            )
            return

        analysis_name = (
                self.current_analysis_name
                or "Analiza statystyczna"
        )

        section_number = len(self.report_sections) + 1

        # Wynik tabelaryczny, np. statystyki opisowe.
        if isinstance(self.current_analysis_result, pd.DataFrame):
            result = self.current_analysis_result.copy()

            table_html = result.to_html(
                index=False,
                border=0,
                justify="center",
                classes="report-table",
                na_rep="—",
            )

            report_section = f"""
            <div class="report-section">
                <h2>Analiza {section_number}</h2>
                <h3>{html.escape(analysis_name)}</h3>
                {table_html}
            </div>
            """

        # Wynik tekstowy, np. regresja, korelacja lub test.
        else:
            result_text = html.escape(
                str(self.current_analysis_result)
            )

            report_section = f"""
            <div class="report-section">
                <h2>Analiza {section_number}</h2>
                <h3>{html.escape(analysis_name)}</h3>
                <pre>{result_text}</pre>
            </div>
            """

        self.report_sections.append(report_section)

        self.refresh_report_preview()

        QMessageBox.information(
            self,
            "Dodano do raportu",
            f"Analiza „{analysis_name}” została dodana do raportu."
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