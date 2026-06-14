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

    def normalize_decimal_separator(self, df):
        changes = 0

        for column in df.columns:
            if df[column].dtype == "object":
                for idx, value in df[column].items():
                    if isinstance(value, str):
                        if value.replace(",", "").replace(".", "").isdigit():
                            new_value = value.replace(",", ".")

                            if new_value != value:
                                df.at[idx, column] = new_value
                                changes += 1

        self.report.append(
            f"Zamieniono przecinki dziesiętne na kropki w {changes} komórkach."
        )

        return df

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

    def remove_duplicates(self, df):
        duplicates_count = df.duplicated().sum()

        if duplicates_count > 0:
            df = df.drop_duplicates()
            self.report.append(f"Usunięto {duplicates_count} zduplikowanych wierszy.")
        else:
            self.report.append("Nie wykryto zduplikowanych wierszy.")

        return df

    def detect_suspicious_values(self, df):
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                negative_count = (df[column] < 0).sum()

                if negative_count > 0:
                    self.report.append(
                        f"Kolumna '{column}' zawiera {negative_count} wartości ujemnych."
                    )

                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1

                lower_limit = q1 - 1.5 * iqr
                upper_limit = q3 + 1.5 * iqr

                outliers_count = (
                    (df[column] < lower_limit) | (df[column] > upper_limit)
                ).sum()

                if outliers_count > 0:
                    self.report.append(
                        f"Kolumna '{column}' zawiera {outliers_count} wartości odstających."
                    )

        return df

    def run(self, input_file, output_file=None):
        df = self.load_data(input_file)

        df = self.normalize_decimal_separator(df)
        df = self.remove_sparse_columns(df)
        df = self.remove_duplicates(df)
        df = self.detect_suspicious_values(df)

        return df