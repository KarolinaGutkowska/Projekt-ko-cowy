#Statystyki opisowe
import pandas as pd


class StatisticsEngine:

    def __init__(self):
        self.report = []

    def descriptive_statistics(self, df):
        numeric_df = df.select_dtypes(include="number")

        if numeric_df.empty:
            self.report.append("Brak kolumn liczbowych do analizy opisowej.")
            return None

        stats = numeric_df.describe().T

        self.report.append("Wygenerowano statystyki opisowe dla kolumn liczbowych.")

        return stats

    def run(self, df):
        descriptive_stats = self.descriptive_statistics(df)

        return {
            "descriptive_statistics": descriptive_stats
        }