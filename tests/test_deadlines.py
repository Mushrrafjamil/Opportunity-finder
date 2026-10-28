
from datetime import date
import sys
from pathlib import Path

# Make the src folder importable for this test.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import parse_deadline


def test_parse_deadline_with_month_name():
    assert parse_deadline("November 21, 2026") == date(2026, 11, 21)


def test_parse_deadline_with_iso_format():
    assert parse_deadline("2026-11-25") == date(2026, 11, 25)


def test_parse_deadline_inside_sentence():
    assert (
        parse_deadline("Apply before November 21, 2026")
        == date(2026, 11, 21)
    )


def test_missing_deadline_returns_none():
    assert parse_deadline("") is None
    assert parse_deadline("Not stated in the source") is None


def test_invalid_deadline_returns_none():
    assert parse_deadline("February 30, 2026") is None
