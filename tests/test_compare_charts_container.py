"""
Smoke tests for CompareChartsContainer compare-mode guards.
"""

from unittest.mock import MagicMock

from components.compare_charts_container import CompareChartsContainer


def test_update_from_non_compare_snapshot_hides_container():
    container = CompareChartsContainer()

    snapshot = MagicMock()
    snapshot.is_compare_mode.return_value = False
    snapshot.comparison = None

    container.update_from_snapshot(snapshot)

    assert container.visible is False
    assert container._snapshot is None
    assert container._visual_grouping is None
