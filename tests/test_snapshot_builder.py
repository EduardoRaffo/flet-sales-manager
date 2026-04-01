"""
Tests para services/snapshot_builder.py — Ensamblaje de AnalysisSnapshot.
"""

import unittest
from datetime import datetime, timezone
from domain.analysis_snapshot import (
    AnalysisMode, TimeGrouping, Filters, TableRow, PeriodMetrics,
    EvolutionData, ProductDistribution, ClientRank, AnalysisSnapshot,
)
from services.snapshot_builder import build_sales_snapshot, build_normal_snapshot


def _make_filters(start="2024-01-01", end="2024-06-30"):
    return Filters(date_start=start, date_end=end)


def _make_period_data(grouping="month"):
    return {
        "table_data": [TableRow("Servicio", 10, 5000.0, 500.0, 100.0, 1000.0)],
        "metrics": PeriodMetrics(5000.0, 10, 500.0, 10, 3),
        "evolution": EvolutionData(
            labels=["2024-01", "2024-02"],
            values=[2000.0, 3000.0],
            grouping=TimeGrouping(grouping),
        ),
        "product_distribution": ProductDistribution(
            labels=["Servicio"], values=[5000.0], percentages=[100.0],
        ),
        "top_clients": [ClientRank(1, "TechNova", 3000.0, 5, 60.0)],
        "evolution_raw": [("2024-01-15", 2000.0), ("2024-02-10", 3000.0)],
    }


class TestBuildSalesSnapshotNormal(unittest.TestCase):
    """Tests para build_sales_snapshot en modo NORMAL."""

    def test_normal_mode_success(self):
        snap = build_sales_snapshot(
            mode=AnalysisMode.NORMAL,
            grouping=TimeGrouping.MONTH,
            filters_a=_make_filters(),
            period_a_data=_make_period_data(),
        )
        self.assertIsInstance(snap, AnalysisSnapshot)
        self.assertTrue(snap.is_normal_mode())
        self.assertIsNone(snap.period_b)
        self.assertIsNone(snap.comparison)

    def test_normal_mode_with_period_b_raises(self):
        with self.assertRaises(ValueError):
            build_sales_snapshot(
                mode=AnalysisMode.NORMAL,
                grouping=TimeGrouping.MONTH,
                filters_a=_make_filters(),
                period_a_data=_make_period_data(),
                period_b_data=_make_period_data(),
                filters_b=_make_filters(),
            )


class TestBuildSalesSnapshotCompare(unittest.TestCase):
    """Tests para build_sales_snapshot en modo COMPARE."""

    def test_compare_mode_success(self):
        snap = build_sales_snapshot(
            mode=AnalysisMode.COMPARE,
            grouping=TimeGrouping.MONTH,
            filters_a=_make_filters("2024-01-01", "2024-06-30"),
            period_a_data=_make_period_data(),
            period_b_data=_make_period_data(),
            filters_b=_make_filters("2023-01-01", "2023-06-30"),
        )
        self.assertIsInstance(snap, AnalysisSnapshot)
        self.assertTrue(snap.is_compare_mode())
        self.assertIsNotNone(snap.period_b)
        self.assertIsNotNone(snap.comparison)

    def test_compare_mode_missing_period_b_raises(self):
        with self.assertRaises(ValueError):
            build_sales_snapshot(
                mode=AnalysisMode.COMPARE,
                grouping=TimeGrouping.MONTH,
                filters_a=_make_filters(),
                period_a_data=_make_period_data(),
            )

    def test_compare_mode_missing_filters_b_raises(self):
        with self.assertRaises(ValueError):
            build_sales_snapshot(
                mode=AnalysisMode.COMPARE,
                grouping=TimeGrouping.MONTH,
                filters_a=_make_filters(),
                period_a_data=_make_period_data(),
                period_b_data=_make_period_data(),
                filters_b=None,
            )


class TestBuildNormalSnapshot(unittest.TestCase):
    """Tests para build_normal_snapshot() — convenience wrapper."""

    def test_delegates_to_build_sales_snapshot(self):
        snap = build_normal_snapshot(
            grouping=TimeGrouping.MONTH,
            filters=_make_filters(),
            period_data=_make_period_data(),
        )
        self.assertIsInstance(snap, AnalysisSnapshot)
        self.assertTrue(snap.is_normal_mode())

    def test_period_b_is_none(self):
        snap = build_normal_snapshot(
            grouping=TimeGrouping.MONTH,
            filters=_make_filters(),
            period_data=_make_period_data(),
        )
        self.assertIsNone(snap.period_b)
        self.assertIsNone(snap.comparison)


class TestComparisonCalculations(unittest.TestCase):
    """Tests para cálculos de comparación dentro de build_sales_snapshot."""

    def _build_compare(self, metrics_a=None, metrics_b=None):
        data_a = _make_period_data()
        data_b = _make_period_data()
        if metrics_a:
            data_a["metrics"] = metrics_a
        if metrics_b:
            data_b["metrics"] = metrics_b
        return build_sales_snapshot(
            mode=AnalysisMode.COMPARE,
            grouping=TimeGrouping.MONTH,
            filters_a=_make_filters("2024-01-01", "2024-06-30"),
            period_a_data=data_a,
            period_b_data=data_b,
            filters_b=_make_filters("2023-01-01", "2023-06-30"),
        )

    def test_comparison_metrics_exist(self):
        snap = self._build_compare()
        self.assertIsNotNone(snap.comparison.metrics)
        self.assertIn("total_sales", snap.comparison.metrics.absolute_changes)

    def test_evolution_comparison_v2_exists(self):
        snap = self._build_compare()
        self.assertIsNotNone(snap.comparison.evolution)
        self.assertIsInstance(snap.comparison.evolution.points, list)

    def test_product_comparison_exists(self):
        snap = self._build_compare()
        self.assertIsNotNone(snap.comparison.products)
        self.assertIsInstance(snap.comparison.products.labels, list)


if __name__ == "__main__":
    unittest.main()
