import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QFileDialog, QTextEdit
)
from PyQt6.QtWidgets import QMessageBox
import traceback
from HUBA.huba import HUBA
from Statistics.statistics_engine import StatisticsEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StatAnalyzer - HUBA")
        self.setGeometry(100, 100, 800, 600)

        self.file_path = None

        self.label = QLabel("Nie wybrano pliku")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.choose_button = QPushButton("Wybierz plik CSV lub Excel")
        self.choose_button.clicked.connect(self.choose_file)

        self.run_button = QPushButton("Uruchom HUBA i analizę")
        self.run_button.clicked.connect(self.run_analysis)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.choose_button)
        layout.addWidget(self.run_button)
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

    def run_analysis(self):
        try:
            if not self.file_path:
                self.output.setText("Najpierw wybierz plik.")
                return

            huba = HUBA()

            clean_df = huba.run(
                self.file_path,
                "dane_clean.xlsx",
                "huba_report.txt"
            )

            stats_engine = StatisticsEngine()
            results = stats_engine.run(clean_df, "statistics_report.txt")

            text = "=== RAPORT HUBA ===\n"
            for line in huba.report:
                text += line + "\n"

            text += "\n=== TYPY ZMIENNYCH ===\n"
            for column, var_type in results["variable_types"].items():
                text += f"{column}: {var_type}\n"

            self.output.setText(text)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd",
                f"Wystąpił błąd:\n{e}\n\n{traceback.format_exc()}"
            )


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())