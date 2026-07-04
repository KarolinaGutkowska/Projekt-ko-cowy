from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTabWidget, QFormLayout
)

from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer")
        self.setGeometry(100, 100, 1100, 750)

        self.file_path = None
        self.clean_df = None
        self.results = None

        self.tabs = QTabWidget()

        self.data_tab = QWidget()
        self.test_tab = QWidget()

        self.tabs.addTab(self.data_tab, "Dane i HUBA")
        self.tabs.addTab(self.test_tab, "Dobór testu")

        self.build_data_tab()
        self.build_test_tab()

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

        self.run_button = QPushButton("Uruchom HUBA i analizę")
        self.run_button.clicked.connect(self.run_analysis)

        self.preview_table = QTableWidget()

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.choose_button)
        layout.addWidget(self.password_input)
        layout.addWidget(self.run_button)
        layout.addWidget(self.preview_table)
        layout.addWidget(self.output)

        self.data_tab.setLayout(layout)

    def build_test_tab(self):
        self.variable_1_combo = QComboBox()
        self.variable_2_combo = QComboBox()

        self.goal_combo = QComboBox()
        self.goal_combo.addItems([
            "Porównać grupy między sobą",
            "Zbadać związek między zmiennymi",
            "Opisać jedną zmienną"
        ])

        self.dependency_combo = QComboBox()
        self.dependency_combo.addItems([
            "Niezależne",
            "Zależne"
        ])

        self.groups_combo = QComboBox()
        self.groups_combo.addItems([
            "2 grupy",
            "Więcej niż 2 grupy"
        ])

        self.variable_type_combo = QComboBox()
        self.variable_type_combo.addItems([
            "Nominalna",
            "Porządkowa",
            "Ilościowa"
        ])

        self.normality_combo = QComboBox()
        self.normality_combo.addItems([
            "Tak",
            "Nie",
            "Nie wiem"
        ])

        self.variance_combo = QComboBox()
        self.variance_combo.addItems([
            "Tak",
            "Nie",
            "Nie wiem"
        ])

        self.recommend_button = QPushButton("Dobierz test")
        self.recommend_button.clicked.connect(self.recommend_test)

        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Wybierz zmienną:", self.variable_1_combo)
        form.addRow("Wybierz drugą zmienną:", self.variable_2_combo)
        form.addRow("Co chcesz zbadać?", self.goal_combo)
        form.addRow("Jaki charakter mają zmienne?", self.dependency_combo)
        form.addRow("Ile grup porównujesz?", self.groups_combo)
        form.addRow("Jaki typ ma zmienna zależna?", self.variable_type_combo)
        form.addRow("Czy zmienna ma rozkład normalny?", self.normality_combo)
        form.addRow("Czy wariancje są jednorodne?", self.variance_combo)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.recommend_button)
        layout.addWidget(self.test_result)

        self.test_tab.setLayout(layout)

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

    def show_dataframe_preview(self, df, max_rows=100):
        preview_df = df.head(max_rows)

        self.preview_table.setRowCount(len(preview_df))
        self.preview_table.setColumnCount(len(preview_df.columns))
        self.preview_table.setHorizontalHeaderLabels(
            preview_df.columns.astype(str)
        )

        for row_idx, row in enumerate(preview_df.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                self.preview_table.setItem(
                    row_idx,
                    col_idx,
                    QTableWidgetItem(str(value))
                )

        self.preview_table.resizeColumnsToContents()

    def update_variable_lists(self):
        self.variable_1_combo.clear()
        self.variable_2_combo.clear()

        if self.clean_df is not None:
            columns = list(self.clean_df.columns)
            self.variable_1_combo.addItems(columns)
            self.variable_2_combo.addItems(columns)

    def run_analysis(self):
        try:
            if not self.file_path:
                self.output.setText("Najpierw wybierz plik.")
                return

            password = self.password_input.text()
            if password == "":
                password = None

            huba = HUBA()

            self.clean_df = huba.run(
                self.file_path,
                "dane_clean.xlsx",
                "huba_report.txt",
                password=password
            )

            self.show_dataframe_preview(self.clean_df)
            self.update_variable_lists()

            stats_engine = StatisticsEngine()

            self.results = stats_engine.run(
                self.clean_df,
                "statistics_report.txt"
            )

            text = "=== RAPORT HUBA ===\n"
            for line in huba.report:
                text += line + "\n"

            text += "\n=== TYPY ZMIENNYCH ===\n"
            for column, var_type in self.results["variable_types"].items():
                text += f"{column}: {var_type}\n"

            text += "\n=== STATYSTYKI OPISOWE ===\n"
            text += str(self.results["descriptive_statistics"])

            text += "\n\n=== RAPORT STATYSTYCZNY ===\n"
            for line in stats_engine.report:
                text += line + "\n"

            self.output.setText(text)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd",
                str(e)
            )

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
            elif variable_type == "Ilościowa" and normality == "Nie":
                test = "Korelacja Spearmana"
            elif variable_type == "Nominalna":
                test = "Test Chi-kwadrat niezależności"
            else:
                test = "Korelacja Spearmana"

        elif goal == "Porównać grupy między sobą":
            if dependency == "Niezależne":
                if groups == "2 grupy":
                    if variable_type == "Ilościowa" and normality == "Tak":
                        test = "Test t-Studenta dla prób niezależnych"
                    elif variable_type == "Ilościowa" and normality == "Nie":
                        test = "Test U Manna-Whitneya"
                    elif variable_type == "Porządkowa":
                        test = "Test U Manna-Whitneya"
                    else:
                        test = "Test Chi-kwadrat niezależności"

                else:
                    if variable_type == "Ilościowa" and normality == "Tak" and variance == "Tak":
                        test = "Jednoczynnikowa ANOVA"
                    elif variable_type == "Ilościowa":
                        test = "Test Kruskala-Wallisa"
                    elif variable_type == "Porządkowa":
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