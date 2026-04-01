"""
Tests para domain/analysis_snapshot.py y domain/dashboard_kpi_snapshot.py.

Valida la consistencia de los modelos de datos y la lógica de validación.
"""

import unittest
from datetime import datetime, timezone
from domain.analysis_snapshot import (
    AnalysisMode, TimeGrouping, Metadata, Filters, TableRow, PeriodMetrics,
    EvolutionData, ProductDistribution, ClientRank, PeriodSnapshot,
    ComparisonMetrics, EvolutionPointV2, EvolutionComparisonV2,
    ProductComparison, ComparisonSnapshot, AnalysisSnapshot,
    PieChartSegmentSnapshot, PieChartSnapshot,
)
from domain.dashboard_kpi_snapshot import DashboardKPISnapshot


# ── Helpers para construir snapshots de test ──────────────────

def _make_filters(start="2024-01-01", end="2024-06-30"):
    return Filters(date_start=start, date_end=end)


def _make_metrics():
    return PeriodMetrics(
        total_sales=10000.0, transactions=50,
        avg_ticket=200.0, total_quantity=50, unique_clients=5,
    )


def _make_evolution(grouping=TimeGrouping.MONTH):
    return EvolutionData(
        labels=["2024-01", "2024-02", "2024-03"],
        values=[1000.0, 2000.0, 3000.0],
        grouping=grouping,
    )


def _make_distribution():
    return ProductDistribution(
        labels=["A", "B"], values=[7000.0, 3000.0], percentages=[70.0, 30.0],
    )


def _make_period(label="Período A", grouping=TimeGrouping.MONTH):
    return PeriodSnapshot(
        label=label,
        filters=_make_filters(),
        table_data=[TableRow("Servicio", 30, 6000.0, 200.0, 100.0, 500.0)],
        metrics=_make_metrics(),
        evolution=_make_evolution(grouping),
        product_distribution=_make_distribution(),
        top_clients=[ClientRank(1, "TechNova", 5000.0, 20, 50.0)],
    )


def _make_utc(year, month, day, hour=0):
    return datetime(year, month, day, hour, tzinfo=timezone.utc)


def _make_evolution_point(key, label, start, end, val_a, val_b, partial=False):
    return EvolutionPointV2(
        key=key, label=label, start=start, end=end,
        value_a=val_a, value_b=val_b,
        difference=val_b - val_a, is_partial=partial,
    )


def _make_compare_snapshot(grouping=TimeGrouping.MONTH):
    points = [
        _make_evolution_point(
            "2024-01", "Ene 24",
            _make_utc(2024, 1, 1), _make_utc(2024, 2, 1),
            1000.0, 1200.0,
        ),
        _make_evolution_point(
            "2024-02", "Feb 24",
            _make_utc(2024, 2, 1), _make_utc(2024, 3, 1),
            2000.0, 1800.0,
        ),
    ]
    comparison = ComparisonSnapshot(
        metrics=ComparisonMetrics(
            absolute_changes={"total_sales": 1000.0},
            percentage_changes={"total_sales": 10.0},
        ),
        evolution=EvolutionComparisonV2(points=points),
        products=ProductComparison(
            labels=["A"], series_a=[5000.0], series_b=[6000.0],
            differences=[1000.0], percentage_diff=[20.0],
        ),
    )
    return AnalysisSnapshot(
        metadata=Metadata(
            mode=AnalysisMode.COMPARE, grouping=grouping,
            generated_at=datetime.now(timezone.utc),
        ),
        filters=_make_filters(),
        period_a=_make_period(grouping=grouping),
        period_b=_make_period(label="Período B", grouping=grouping),
        comparison=comparison,
    )


# ── Tests ─────────────────────────────────────────────────────

class TestAnalysisSnapshotValidateNormal(unittest.TestCase):
    """Validación en modo NORMAL."""

    def _make_normal(self, **overrides):
        kwargs = dict(
            metadata=Metadata(
                mode=AnalysisMode.NORMAL, grouping=TimeGrouping.MONTH,
                generated_at=datetime.now(timezone.utc),
            ),
            filters=_make_filters(),
            period_a=_make_period(),
            period_b=None,
            comparison=None,
        )
        kwargs.update(overrides)
        return AnalysisSnapshot(**kwargs)

    def test_valid_normal_mode(self):
        snap = self._make_normal()
        self.assertTrue(snap.validate())

    def test_normal_mode_with_period_b_raises(self):
        snap = self._make_normal(period_b=_make_period("B"))
        with self.assertRaises(ValueError, msg="period_b debe ser None"):
            snap.validate()

    def test_normal_mode_with_comparison_raises(self):
        comparison = ComparisonSnapshot(
            metrics=ComparisonMetrics({}, {}),
            evolution=EvolutionComparisonV2(points=[]),
            products=ProductComparison([], [], [], [], []),
        )
        snap = self._make_normal(comparison=comparison)
        with self.assertRaises(ValueError):
            snap.validate()


class TestAnalysisSnapshotValidateCompare(unittest.TestCase):
    """Validación en modo COMPARE."""

    def test_valid_compare_mode(self):
        snap = _make_compare_snapshot()
        self.assertTrue(snap.validate())

    def test_compare_mode_missing_period_b_raises(self):
        snap = _make_compare_snapshot()
        snap.period_b = None
        with self.assertRaises(ValueError):
            snap.validate()

    def test_compare_mode_missing_comparison_raises(self):
        snap = _make_compare_snapshot()
        snap.comparison = None
        with self.assertRaises(ValueError):
            snap.validate()

    def test_compare_mode_empty_points_raises(self):
        snap = _make_compare_snapshot()
        snap.comparison.evolution.points = []
        with self.assertRaises(ValueError):
            snap.validate()

    def test_compare_mode_naive_datetime_raises(self):
        snap = _make_compare_snapshot()
        snap.comparison.evolution.points[0].start = datetime(2024, 1, 1)
        with self.assertRaises(ValueError):
            snap.validate()

    def test_compare_mode_start_gte_end_raises(self):
        snap = _make_compare_snapshot()
        p = snap.comparison.evolution.points[0]
        snap.comparison.evolution.points[0] = EvolutionPointV2(
            key=p.key, label=p.label,
            start=_make_utc(2024, 3, 1), end=_make_utc(2024, 1, 1),
            value_a=p.value_a, value_b=p.value_b,
            difference=p.difference, is_partial=p.is_partial,
        )
        with self.assertRaises(ValueError):
            snap.validate()

    def test_compare_mode_wrong_difference_raises(self):
        snap = _make_compare_snapshot()
        p = snap.comparison.evolution.points[0]
        snap.comparison.evolution.points[0] = EvolutionPointV2(
            key=p.key, label=p.label, start=p.start, end=p.end,
            value_a=p.value_a, value_b=p.value_b,
            difference=9999.0, is_partial=p.is_partial,
        )
        with self.assertRaises(ValueError):
            snap.validate()


class TestValidateKeyFormat(unittest.TestCase):
    """Tests para _validate_key_format()."""

    def _snap_with_key(self, key, grouping):
        snap = _make_compare_snapshot(grouping)
        p = snap.comparison.evolution.points[0]
        snap.comparison.evolution.points = [
            EvolutionPointV2(
                key=key, label="test",
                start=_make_utc(2024, 1, 1), end=_make_utc(2024, 2, 1),
                value_a=100.0, value_b=200.0, difference=100.0,
            )
        ]
        return snap

    def test_valid_day_key(self):
        snap = self._snap_with_key("2024-03-15", TimeGrouping.DAY)
        self.assertTrue(snap.validate())

    def test_invalid_day_key(self):
        snap = self._snap_with_key("2024-13-01", TimeGrouping.DAY)
        with self.assertRaises(ValueError):
            snap.validate()

    def test_valid_week_key(self):
        snap = self._snap_with_key("2024-W12", TimeGrouping.WEEK)
        self.assertTrue(snap.validate())

    def test_valid_month_key(self):
        snap = self._snap_with_key("2024-03", TimeGrouping.MONTH)
        self.assertTrue(snap.validate())

    def test_valid_quarter_key(self):
        snap = self._snap_with_key("2024-Q1", TimeGrouping.QUARTER)
        self.assertTrue(snap.validate())

    def test_invalid_quarter_key(self):
        snap = self._snap_with_key("2024-Q5", TimeGrouping.QUARTER)
        with self.assertRaises(ValueError):
            snap.validate()

    def test_valid_year_key(self):
        snap = self._snap_with_key("2024", TimeGrouping.YEAR)
        self.assertTrue(snap.validate())


class TestHelperMethods(unittest.TestCase):
    """Tests para is_normal_mode() / is_compare_mode()."""

    def test_is_normal_mode(self):
        snap = AnalysisSnapshot(
            metadata=Metadata(AnalysisMode.NORMAL, TimeGrouping.MONTH, datetime.now(timezone.utc)),
            filters=_make_filters(),
            period_a=_make_period(),
        )
        self.assertTrue(snap.is_normal_mode())
        self.assertFalse(snap.is_compare_mode())

    def test_is_compare_mode(self):
        snap = _make_compare_snapshot()
        self.assertTrue(snap.is_compare_mode())
        self.assertFalse(snap.is_normal_mode())


class TestDashboardKPISnapshot(unittest.TestCase):
    """Tests para DashboardKPISnapshot."""

    def test_empty_factory(self):
        snap = DashboardKPISnapshot.empty()
        self.assertFalse(snap.has_data)
        self.assertEqual(snap.sales_rows, 0)
        self.assertEqual(snap.clients_rows, 0)
        self.assertIsNone(snap.last_import)
        self.assertEqual(snap.total_leads, 0)
        self.assertEqual(snap.leads_conversion_rate, 0.0)

    def test_frozen_dataclass(self):
        snap = DashboardKPISnapshot.empty()
        with self.assertRaises(AttributeError):
            snap.sales_rows = 10

    def test_all_fields_set(self):
        snap = DashboardKPISnapshot(
            has_data=True, sales_rows=100, clients_rows=20,
            last_import="2024-05-15T10:00:00",
            total_leads=50, leads_with_meeting=10,
            leads_conversion_rate=20.0, leads_this_month=5,
        )
        self.assertTrue(snap.has_data)
        self.assertEqual(snap.sales_rows, 100)
        self.assertEqual(snap.total_leads, 50)


if __name__ == "__main__":
    unittest.main()
