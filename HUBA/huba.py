import pandas as pd
from pathlib import Path


class HUBA:

    def __init__(self):
        self.report = []

    def load_data(self, file_path, sheet_name=0):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku: {file_path}")

        if path.suffix.lower() == ".csv":
            try:
                df = pd.read_csv(path, sep=None, engine="python")
            except UnicodeDecodeError:
                df = pd.read_csv(path, sep=None, engine="python", encoding="latin1")

            self.report.append("Wczytano plik CSV.")

        elif path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path, sheet_name=sheet_name)
            self.report.append("Wczytano plik Excel.")

        else:
            raise ValueError("Obsługiwane formaty to tylko: .csv, .xlsx, .xls")

        if df.empty:
            raise ValueError("Plik jest pusty lub nie zawiera danych.")

        self.report.append(f"Liczba wierszy: {df.shape[0]}")
        self.report.append(f"Liczba kolumn: {df.shape[1]}")

        return df

    #sprawdzanie ilości pustych komórek
    def remove_sparse_columns(self, df, threshold=0.5):
        rows = len(df)

        columns_to_remove = []

        for column in df.columns:
            missing = df[column].isna().sum()
            missing_ratio = missing / rows

            if missing_ratio > threshold:
                columns_to_remove.append(column)

                self.report.append(
                    f"Usunięto kolumnę '{column}' - "
                    f"{missing} braków ({missing_ratio:.1%})"
                )

        df = df.drop(columns=columns_to_remove)

        self.report.append(
            f"Usunięto {len(columns_to_remove)} kolumn z ponad {threshold:.0%} braków."
        )

        return df

    def run(self, input_file, output_file):
        df = self.load_data(input_file)

        # Usuwanie kolumn z dużą liczbą braków
        df = self.remove_sparse_columns(df)

        # Walidacja
        # Czyszczenie
        # Normalizacja
        # Raport

        return df