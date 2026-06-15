import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QFileDialog, QTextEdit, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer - HUBA")
        self.setGeometry(100, 100, 1000, 700)

        self.file_path = None

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

        self.setLayout(layout)

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

    def run_analysis(self):
        try:
            if not self.file_path:
                self.output.setText("Najpierw wybierz plik.")
                return

            password = self.password_input.text()

            if password == "":
                password = None

            huba = HUBA()

            clean_df = huba.run(
                self.file_path,
                "dane_clean.xlsx",
                "huba_report.txt",
                password=password
            )

            self.show_dataframe_preview(clean_df)

            stats_engine = StatisticsEngine()

            results = stats_engine.run(
                clean_df,
                "statistics_report.txt"
            )

            text = "=== RAPORT HUBA ===\n"

            for line in huba.report:
                text += line + "\n"

            text += "\n=== TYPY ZMIENNYCH ===\n"

            for column, var_type in results["variable_types"].items():
                text += f"{column}: {var_type}\n"

            text += "\n=== STATYSTYKI OPISOWE ===\n"
            text += str(results["descriptive_statistics"])

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