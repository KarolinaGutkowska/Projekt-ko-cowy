import pandas as pd
from pathlib import Path


class HUBA:

    def __init__(self):
        self.report = []
    #Wczytywanie plików
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
    #Zamiana przecinków na kropki
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
    #Usuwanie kolumn z brakami powyżej 50%
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
    #Usuwanie duplikatów
    def remove_duplicates(self, df):
        duplicates_count = df.duplicated().sum()

        if duplicates_count > 0:
            df = df.drop_duplicates()
            self.report.append(f"Usunięto {duplicates_count} zduplikowanych wierszy.")
        else:
            self.report.append("Nie wykryto zduplikowanych wierszy.")

        return df
    #Wyszukiwanie podejrzanych wartości - ujemnych, znacznie odstających
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

    # Wykrywanie niewłaściwych typów danych
    def detect_invalid_data_types(self, df):
        for column in df.columns:
            if df[column].dtype == "object":
                numeric_version = pd.to_numeric(df[column], errors="coerce")

                invalid_count = (
                        numeric_version.isna().sum()
                        - df[column].isna().sum()
                )

                if invalid_count > 0:
                    self.report.append(
                        f"Kolumna '{column}' zawiera "
                        f"{invalid_count} potencjalnie błędnych wartości "
                        f"uniemożliwiających konwersję na liczby."
                    )

        return df

    # Zapisywanie oczyszczonego pliku
    def save_clean_data(self, df, output_file):
        path = Path(output_file)

        if path.suffix.lower() == ".csv":
            df.to_csv(path, index=False)

        elif path.suffix.lower() in [".xlsx", ".xls"]:
            df.to_excel(path, index=False)

        else:
            raise ValueError(
                "Obsługiwane formaty zapisu to tylko: .csv, .xlsx, .xls"
            )

        self.report.append(
            f"Zapisano oczyszczone dane do pliku: {output_file}"
        )

    # Zapisywanie raportu
    def save_report(self, report_file):
        with open(report_file, "w", encoding="utf-8") as file:
            file.write("=== RAPORT HUBA ===\n\n")

            for line in self.report:
                file.write(line + "\n")

        self.report.append(
            f"Zapisano raport do pliku: {report_file}"
        )

    #Usuwanie pustych wierszy
    def remove_empty_rows(self, df):
        empty_rows_count = df.isna().all(axis=1).sum()

        if empty_rows_count > 0:
            df = df.dropna(how="all")
            self.report.append(f"Usunięto {empty_rows_count} całkowicie pustych wierszy.")
        else:
            self.report.append("Nie wykryto całkowicie pustych wierszy.")

        return df

    def run(self, input_file, output_file, report_file):
        df = self.load_data(input_file)

        df = self.detect_invalid_data_types(df)
        df = self.normalize_decimal_separator(df)
        df = self.remove_empty_rows(df)
        df = self.remove_sparse_columns(df)
        df = self.remove_duplicates(df)
        df = self.detect_suspicious_values(df)

        self.save_clean_data(df, output_file)
        self.save_report(report_file)

        return df