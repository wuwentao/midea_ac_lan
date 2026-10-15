"""Regression checks for completion reservations through the actual HA entity."""

# These checks use unittest to avoid adding a test-runner dependency.
# ruff: file-ignore[pytest-unittest-assertion, pytest-unittest-raises-assertion]

import unittest
from datetime import UTC, datetime, time, timedelta
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

from midea_ac_lan.time import MideaTime


class CompletionTimeTests(unittest.TestCase):
    """Cover repeated and missing local hours without connecting to appliances."""

    def setUp(self) -> None:
        """Build a time entity with only its reservation state and a mock device."""
        self.entity = object.__new__(MideaTime)
        self.entity._config = {  # ruff: ignore[private-member-access]
            "completion_attribute": "appointment_finish",
        }
        self.entity._entity_key = "appointment_finish"  # ruff: ignore[private-member-access]
        self.device = Mock()
        self.entity._device = self.device  # ruff: ignore[private-member-access]

    def test_reservation_uses_earliest_future_instant(self) -> None:
        """Choose the second repeated hour when the first occurrence has passed."""
        zone = ZoneInfo("America/New_York")
        cases = [
            (
                datetime(2025, 11, 2, 0, 30, tzinfo=zone),
                time(1, 30),
                "2025-11-02T01:30:00-04:00",
            ),
            (
                datetime(2025, 11, 2, 1, 15, tzinfo=zone),
                time(1, 30),
                "2025-11-02T01:30:00-04:00",
            ),
            (
                datetime(2025, 11, 2, 1, 30, tzinfo=zone),
                time(1, 30),
                "2025-11-02T01:30:00-05:00",
            ),
            (
                datetime(2025, 11, 2, 1, 45, tzinfo=zone),
                time(1, 30),
                "2025-11-02T01:30:00-05:00",
            ),
            (
                datetime(2025, 11, 2, 1, 15, tzinfo=zone, fold=1),
                time(1, 30),
                "2025-11-02T01:30:00-05:00",
            ),
            (
                datetime(2025, 11, 2, 1, 45, tzinfo=zone, fold=1),
                time(1, 30),
                "2025-11-03T01:30:00-05:00",
            ),
            (
                datetime(2025, 3, 9, 1, 30, tzinfo=zone),
                time(3, 30),
                "2025-03-09T03:30:00-04:00",
            ),
            (
                datetime(2025, 3, 9, 3, 30, tzinfo=zone),
                time(2, 30),
                "2025-03-10T02:30:00-04:00",
            ),
            (
                datetime(2025, 3, 8, 23, 30, tzinfo=zone),
                time(23, 0),
                "2025-03-09T23:00:00-04:00",
            ),
        ]
        for now, selected, expected in cases:
            with self.subTest(now=now, selected=selected):
                self.device.reset_mock()
                with patch(
                    "midea_ac_lan.time.dt_util.now",
                    return_value=now,
                ):
                    self.entity.set_value(selected)
                self.device.set_attribute.assert_called_once_with(
                    "appointment_finish",
                    expected,
                )
                deadline = datetime.fromisoformat(expected).astimezone(UTC)
                self.assertGreater(deadline, now.astimezone(UTC))
                self.assertLessEqual(deadline, now.astimezone(UTC) + timedelta(days=1))

    def test_invalid_local_time_never_writes(self) -> None:
        """Reject spring gaps, over-24-hour deadlines, and sub-minute precision."""
        zone = ZoneInfo("America/New_York")
        cases = [
            (datetime(2025, 3, 9, 1, 30, tzinfo=zone), time(2, 30)),
            (datetime(2025, 3, 8, 23, 30, tzinfo=zone), time(2, 30)),
            (datetime(2025, 11, 1, 23, 30, tzinfo=zone), time(23, 0)),
            (datetime(2025, 3, 8, 23, 30, tzinfo=zone), time(23, 0, 1)),
            (datetime(2025, 3, 8, 23, 30, tzinfo=zone), time(23, 0, microsecond=1)),
        ]
        for now, selected in cases:
            with self.subTest(now=now, selected=selected):
                self.device.reset_mock()
                with (
                    patch(
                        "midea_ac_lan.time.dt_util.now",
                        return_value=now,
                    ),
                    self.assertRaises(ValueError),
                ):
                    self.entity.set_value(selected)
                self.device.set_attribute.assert_not_called()

    def test_cross_midnight_and_exact_24_hours(self) -> None:
        """Ordinary timezones retain next-day and whole-minute behavior."""
        zone = ZoneInfo("Asia/Shanghai")
        now = datetime(2026, 10, 15, 23, 30, tzinfo=zone)
        for selected, expected in [
            (time(8), "2026-10-16T08:00:00+08:00"),
            (time(23, 30), "2026-10-16T23:30:00+08:00"),
        ]:
            with (
                self.subTest(selected=selected),
                patch(
                    "midea_ac_lan.time.dt_util.now",
                    return_value=now,
                ),
            ):
                self.entity.set_value(selected)
                self.device.set_attribute.assert_called_with(
                    "appointment_finish",
                    expected,
                )

    def test_invalid_report_is_unknown(self) -> None:
        """Malformed and naive timestamps do not break HA state reads."""
        for value in ["bad", "2026-02-30T08:00:00+08:00", "2026-10-15T08:00:00"]:
            with self.subTest(value=value):
                self.device.get_attribute.return_value = value
                with self.assertLogs(
                    "midea_ac_lan.time",
                    level="WARNING",
                ):
                    self.assertIsNone(self.entity.native_value)
        for missing in [None, False, 0]:
            with self.subTest(value=missing):
                self.device.get_attribute.return_value = missing
                self.assertIsNone(self.entity.native_value)

    def test_valid_report_remains_device_driven(self) -> None:
        """Read the actual reported deadline in Home Assistant's timezone."""
        self.device.get_attribute.return_value = "2026-10-15T00:00:00+00:00"
        with patch(
            "midea_ac_lan.time.dt_util.DEFAULT_TIME_ZONE",
            ZoneInfo("Asia/Shanghai"),
        ):
            self.assertEqual(self.entity.native_value, time(8))


if __name__ == "__main__":
    unittest.main()
