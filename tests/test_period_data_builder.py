"""
Tests para services/period_data_builder.py — Construcción de datos de período.
"""

import unittest
from unittest.mock import patch, MagicMock
import polars as pl
from domain.analysis_snapshot import TableRow, PeriodMetrics, EvolutionData, TimeGrouping


class TestBuildPeriodData(unittest.TestCase):
    """Tests para build_period_data()."""

    def _make_df_summary(self):
        """Crea un DataFrame simulando la salida de get_sales_summary."""
        return pl.DataFrame({
            "product_type": ["Servicio", "Producto"],
            "total": [3000.0, 5000.0],
            "cantidad": [10, 5],
            "promedio": [300.0, 1000.0],
            "minimo": [100.0, 500.0],
            "maximo": [500.0, 2000.0],
        })

    def _make_evolution_df(self):
        return pl.DataFrame({
            "date": ["2024-05-01", "2024-05-02"],
            "total": [1000.0, 2000.0],
        })

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_returns_expected_keys(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 3
        mock_stats.return_value = []
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "day",
        )
        expected_keys = {"table_data", "metrics", "evolution", "product_distribution", "top_clients", "evolution_raw"}
        self.assertEqual(set(result.keys()), expected_keys)

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_metrics_calculated_correctly(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 3
        mock_stats.return_value = []
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "day",
        )
        metrics = result["metrics"]
        self.assertAlmostEqual(metrics.total_sales, 8000.0)
        self.assertEqual(metrics.total_quantity, 15)
        self.assertAlmostEqual(metrics.avg_ticket, 8000.0 / 15)
        self.assertEqual(metrics.unique_clients, 3)

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_empty_dataframe_returns_zeros(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = None
        mock_clients.return_value = 0
        mock_stats.return_value = []
        empty_df = pl.DataFrame(schema={
            "product_type": pl.Utf8, "total": pl.Float64,
            "cantidad": pl.Int64, "promedio": pl.Float64,
            "minimo": pl.Float64, "maximo": pl.Float64,
        })
        from services.period_data_builder import build_period_data
        result = build_period_data(empty_df, "2024-05-01", "2024-05-31", "day")
        self.assertEqual(result["metrics"].total_sales, 0.0)
        self.assertEqual(result["metrics"].total_quantity, 0)
        self.assertEqual(result["table_data"], [])

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_top_clients_limited_to_5(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 10
        mock_stats.return_value = [
            {"client_id": f"C{i:03d}", "name": f"Client{i}", "total_sales": i, "total_amount": float(i * 1000)}
            for i in range(10)
        ]
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "day",
        )
        self.assertLessEqual(len(result["top_clients"]), 5)

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_compare_mode_stores_evolution_raw(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 3
        mock_stats.return_value = []
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "month",
            is_compare=True,
        )
        self.assertIsNotNone(result["evolution_raw"])
        self.assertIsInstance(result["evolution_raw"], list)

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_normal_mode_evolution_raw_is_none(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 3
        mock_stats.return_value = []
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "day",
            is_compare=False,
        )
        self.assertIsNone(result["evolution_raw"])

    @patch("services.period_data_builder.get_clients_sales_stats")
    @patch("services.period_data_builder.count_unique_clients")
    @patch("services.period_data_builder.get_sales_evolution")
    def test_product_distribution_percentages(self, mock_evolution, mock_clients, mock_stats):
        mock_evolution.return_value = self._make_evolution_df()
        mock_clients.return_value = 3
        mock_stats.return_value = []
        from services.period_data_builder import build_period_data
        result = build_period_data(
            self._make_df_summary(), "2024-05-01", "2024-05-31", "day",
        )
        dist = result["product_distribution"]
        self.assertAlmostEqual(sum(dist.percentages), 100.0)


if __name__ == "__main__":
    unittest.main()
