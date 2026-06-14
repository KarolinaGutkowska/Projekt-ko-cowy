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

    #Korelacje
    def correlations(self, df):
        numeric_df = df.select_dtypes(include="number")

        if numeric_df.shape[1] < 2:
            self.report.append("Za mało kolumn liczbowych do obliczenia korelacji.")
            return None

        correlation_matrix = numeric_df.corr(method="pearson")

        self.report.append("Obliczono macierz korelacji Pearsona.")

        return correlation_matrix

    def run(self, df):
        descriptive_stats = self.descriptive_statistics(df)
        correlation_matrix = self.correlations(df)

        return {
            "descriptive_statistics": descriptive_stats,
            "correlations": correlation_matrix
        }