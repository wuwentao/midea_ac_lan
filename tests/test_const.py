"""Tests for integration constants and device filters."""

import pytest

from custom_components.midea_ac_lan.const import (
    FanSpeed,
    supports_device,
    supports_model,
)


@pytest.mark.parametrize(
    ("model", "config", "expected"),
    [
        ("A", {}, True),
        ("A", {"models": []}, True),
        ("A", {"models": ["A", "B"]}, True),
        (1, {"models": ["1"]}, True),
        ("C", {"models": ["A", "B"]}, False),
    ],
)
def test_supports_model(
    model: object,
    config: dict[str, object],
    expected: bool,
) -> None:
    """Filter model-specific entity configurations."""
    assert supports_model(model, config) is expected


@pytest.mark.parametrize(
    ("model", "subtype", "config", "expected"),
    [
        ("A", 1, {}, True),
        ("A", "1", {"removed": True}, False),
        ("A", 1, {"excluded_devices": [("A", 1)]}, False),
        ("A", 1, {"excluded_subtypes": [1]}, False),
        ("A", 1, {"subtypes": [1, 2]}, True),
        ("A", 3, {"subtypes": [1, 2]}, False),
        ("B", 1, {"models": ["A"]}, False),
        ("A", 1, {"models": ["A"], "subtypes": [1]}, True),
    ],
)
def test_supports_device(
    model: object,
    subtype: object,
    config: dict[str, object],
    expected: bool,
) -> None:
    """Apply removal, exclusion, model, and subtype filters."""
    assert supports_device(model, subtype, config) is expected


def test_fan_speed_values() -> None:
    """Keep the percentage reference values stable."""
    assert [speed.value for speed in FanSpeed] == [20, 40, 60, 80, 100]
