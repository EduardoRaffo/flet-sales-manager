import pytest
from ..time_grouping import group_time_series


# ============================================================
#  FIXTURES
# ============================================================

@pytest.fixture
def sample_rows():
    """
    Datos base desordenados a propósito.
    Formato: (date_iso, value)
    """
    return [
        ("2024-01-10", 100.0),
        ("2024-01-05", 50.0),
        ("2024-02-01", 200.0),
        ("2024-03-15", 75.0),
        ("2024-04-20", 300.0),
    ]

@pytest.mark.parametrize(
    "grouping",
    ["day", "week", "month", "quarter", "year"],
)
def test_group_time_series_contract(grouping):
    rows = [("2024-01-01", 10.0)]

    result = group_time_series(rows, grouping)

    assert isinstance(result, list)
    assert len(result) == 1

    row = result[0]
    assert set(row.keys()) == {"key", "label", "total"}
    assert isinstance(row["key"], str)
    assert isinstance(row["label"], str)
    assert isinstance(row["total"], float)
# ============================================================
#  DAY
# ============================================================

def test_group_day_identity(sample_rows):
    result = group_time_series(sample_rows, "day")

    assert len(result) == 5
    assert result[0]["key"] == "2024-01-05"
    assert result[0]["total"] == 50.0
    assert result[-1]["key"] == "2024-04-20"


# ============================================================
#  WEEK
# ============================================================

def test_group_week_iso():
    rows = [
        ("2024-01-01", 10.0),  # week 1
        ("2024-01-03", 20.0),  # same week
        ("2024-01-10", 30.0),  # week 2
    ]

    result = group_time_series(rows, "week")

    assert len(result) == 2

    week1 = result[0]
    week2 = result[1]

    assert week1["key"] == "2024-W01"
    assert week1["total"] == 30.0

    assert week2["key"] == "2024-W02"
    assert week2["total"] == 30.0


# ============================================================
#  MONTH
# ============================================================

def test_group_month():
    rows = [
        ("2024-01-01", 10.0),
        ("2024-01-15", 20.0),
        ("2024-02-01", 5.0),
    ]

    result = group_time_series(rows, "month")

    assert result == [
        {
            "key": "2024-01",
            "label": "Jan 24",
            "total": 30.0,
        },
        {
            "key": "2024-02",
            "label": "Feb 24",
            "total": 5.0,
        },
    ]


# ============================================================
#  QUARTER
# ============================================================

def test_group_quarter():
    rows = [
        ("2024-01-10", 10.0),  # Q1
        ("2024-03-31", 20.0),  # Q1
        ("2024-04-01", 30.0),  # Q2
    ]

    result = group_time_series(rows, "quarter")

    assert result == [
        {
            "key": "2024-Q1",
            "label": "Q1 24",
            "total": 30.0,
        },
        {
            "key": "2024-Q2",
            "label": "Q2 24",
            "total": 30.0,
        },
    ]


# ============================================================
#  YEAR
# ============================================================

def test_group_year():
    rows = [
        ("2023-12-31", 100.0),
        ("2024-01-01", 50.0),
        ("2024-06-01", 25.0),
    ]

    result = group_time_series(rows, "year")

    assert result == [
        {
            "key": "2023",
            "label": "2023",
            "total": 100.0,
        },
        {
            "key": "2024",
            "label": "2024",
            "total": 75.0,
        },
    ]


# ============================================================
#  EDGE CASES
# ============================================================

def test_empty_rows():
    assert group_time_series([], "month") == []


def test_invalid_grouping_raises():
    with pytest.raises(ValueError):
        group_time_series([("2024-01-01", 10.0)], "decade")

def test_group_week_crossing_year():
    rows = [
        ("2023-12-31", 100.0),  # ISO week 52 or 53
        ("2024-01-01", 200.0),  # same ISO week
    ]

    result = group_time_series(rows, "week")

    assert len(result) == 2
    
    assert result[0]["key"] == "2023-W52"
    assert result[0]["total"] == 100.0

    assert result[1]["key"] == "2024-W01"
    assert result[1]["total"] == 200.0

