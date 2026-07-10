import sys
from PyQt6.QtWidgets import QApplication
from GUI.GUI import MainWindow
import faulthandler

faulthandler.enable()


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
    QWidget {
        background-color: #2b2b2b;
        color: white;
        font-size: 11pt;
    }

    QPushButton {
        background-color: #3c3f41;
        color: white;
        border: 1px solid #5a5a5a;
        border-radius: 6px;
        padding: 6px;
    }

    QPushButton:hover {
        background-color: #4a90e2;
    }

    QLineEdit, QTextEdit, QComboBox, QTableWidget {
        background-color: #3c3f41;
        color: white;
        border: 1px solid #5a5a5a;
    }

    QHeaderView::section {
        background-color: #444444;
        color: white;
    }

    QTabBar::tab {
        background: #3c3f41;
        color: white;
        padding: 8px;
    }

    QTabBar::tab:selected {
        background: #4a90e2;
    }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()