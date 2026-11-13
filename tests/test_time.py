"""Regression checks for completion reservations through the actual time entity.

Covers the laundry completion-time logic in ``midea_ac_lan.time`` for both the
washer (0xDB) and dryer (0xDC) device types; the reservation handling is shared,
so the washer entity exercises the same code path both devices use.
"""

from datetime import UTC, datetime, time, timedelta
from unittest.mock import Mock, call, patch
from zoneinfo import ZoneInfo

import pytest
from homeassistant.const import Platform

from custom_components.midea_ac_lan.time import MideaTime, async_setup_entry

from .helpers import DeviceFactory, InstallConfig, setup_context


@pytest.fixture
def entity() -> tuple[MideaTime, Mock]:
    """Build a time entity with only its reservation state and a mock device."""
    item = object.__new__(MideaTime)
    item._config = {"completion_attribute": "appointment_finish"}
    item._entity_key = "appointment_finish"
    device = Mock()
    item._device = device
    return item, device


@pytest.mark.parametrize(
    ("now", "selected", "expected"),
    [
        # End of DST: 01:30 occurs twice on 2025-11-02 in America/New_York.
        (
            datetime(2025, 11, 2, 0, 30, tzinfo=ZoneInfo("America/New_York")),
            time(1, 30),
            "2025-11-02T01:30:00-04:00",
        ),
        (
            datetime(2025, 11, 2, 1, 15, tzinfo=ZoneInfo("America/New_York")),
            time(1, 30),
            "2025-11-02T01:30:00-04:00",
        ),
        (
            datetime(2025, 11, 2, 1, 30, tzinfo=ZoneInfo("America/New_York")),
            time(1, 30),
            "2025-11-02T01:30:00-05:00",
        ),
        (
            datetime(2025, 11, 2, 1, 45, tzinfo=ZoneInfo("America/New_York")),
            time(1, 30),
            "2025-11-02T01:30:00-05:00",
        ),
        (
            datetime(2025, 11, 2, 1, 15, tzinfo=ZoneInfo("America/New_York"), fold=1),
            time(1, 30),
            "2025-11-02T01:30:00-05:00",
        ),
        (
            datetime(2025, 11, 2, 1, 45, tzinfo=ZoneInfo("America/New_York"), fold=1),
            time(1, 30),
            "2025-11-03T01:30:00-05:00",
        ),
        # Start of DST: 02:30 does not exist on 2025-03-09, so 03:30 is chosen.
        (
            datetime(2025, 3, 9, 1, 30, tzinfo=ZoneInfo("America/New_York")),
            time(3, 30),
            "2025-03-09T03:30:00-04:00",
        ),
        (
            datetime(2025, 3, 9, 3, 30, tzinfo=ZoneInfo("America/New_York")),
            time(2, 30),
            "2025-03-10T02:30:00-04:00",
        ),
        (
            datetime(2025, 3, 8, 23, 30, tzinfo=ZoneInfo("America/New_York")),
            time(23, 0),
            "2025-03-09T23:00:00-04:00",
        ),
    ],
)
def test_reservation_uses_earliest_future_instant(
    entity: tuple[MideaTime, Mock],
    now: datetime,
    selected: time,
    expected: str,
) -> None:
    """Choose the earliest valid future occurrence within the next 24 hours."""
    item, device = entity
    with patch("custom_components.midea_ac_lan.time.dt_util.now", return_value=now):
        item.set_value(selected)
    device.set_attribute.assert_called_once_with(
        "appointment_finish",
        expected,
    )
    deadline = datetime.fromisoformat(expected).astimezone(UTC)
    assert deadline > now.astimezone(UTC)
    assert deadline <= now.astimezone(UTC) + timedelta(days=1)


@pytest.mark.parametrize(
    ("now", "selected"),
    [
        # Spring-forward gap, over-24h deadline, and sub-minute precision.
        (datetime(2025, 3, 9, 1, 30, tzinfo=ZoneInfo("America/New_York")), time(2, 30)),
        (
            datetime(2025, 3, 8, 23, 30, tzinfo=ZoneInfo("America/New_York")),
            time(2, 30),
        ),
        (
            datetime(2025, 11, 1, 23, 30, tzinfo=ZoneInfo("America/New_York")),
            time(23, 0),
        ),
        (
            datetime(2025, 3, 8, 23, 30, tzinfo=ZoneInfo("America/New_York")),
            time(23, 0, 1),
        ),
        (
            datetime(2025, 3, 8, 23, 30, tzinfo=ZoneInfo("America/New_York")),
            time(23, 0, microsecond=1),
        ),
    ],
)
def test_invalid_local_time_never_writes(
    entity: tuple[MideaTime, Mock],
    now: datetime,
    selected: time,
) -> None:
    """Reject spring gaps, over-24-hour deadlines, and sub-minute precision."""
    item, device = entity
    with (
        patch("custom_components.midea_ac_lan.time.dt_util.now", return_value=now),
        pytest.raises(ValueError, match=r"Completion time|does not exist"),
    ):
        item.set_value(selected)
    device.set_attribute.assert_not_called()


@pytest.mark.parametrize(
    ("selected", "expected"),
    [
        (time(8), "2026-10-16T08:00:00+08:00"),
        (time(23, 30), "2026-10-16T23:30:00+08:00"),
    ],
)
def test_cross_midnight_and_exact_24_hours(
    entity: tuple[MideaTime, Mock],
    selected: time,
    expected: str,
) -> None:
    """Ordinary timezones retain next-day and whole-minute behavior."""
    item, device = entity
    now = datetime(2026, 10, 15, 23, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    with patch("custom_components.midea_ac_lan.time.dt_util.now", return_value=now):
        item.set_value(selected)
    device.set_attribute.assert_called_with("appointment_finish", expected)


@pytest.mark.parametrize(
    "value",
    ["bad", "2026-02-30T08:00:00+08:00", "2026-10-15T08:00:00"],
)
def test_invalid_report_is_unknown(
    entity: tuple[MideaTime, Mock],
    value: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Malformed and naive timestamps do not break HA state reads."""
    item, device = entity
    device.get_attribute.return_value = value
    with caplog.at_level("WARNING", logger="custom_components.midea_ac_lan.time"):
        assert item.native_value is None
    assert caplog.records


@pytest.mark.parametrize("missing", [None, False, 0])
def test_missing_report_is_unknown(
    entity: tuple[MideaTime, Mock],
    missing: object,
) -> None:
    """Absent reports read as unknown without logging a warning."""
    item, device = entity
    device.get_attribute.return_value = missing
    assert item.native_value is None


def test_valid_report_remains_device_driven(entity: tuple[MideaTime, Mock]) -> None:
    """Read the actual reported deadline in Home Assistant's timezone."""
    item, device = entity
    device.get_attribute.return_value = "2026-10-15T00:00:00+00:00"
    with patch(
        "custom_components.midea_ac_lan.time.dt_util.DEFAULT_TIME_ZONE",
        ZoneInfo("Asia/Shanghai"),
    ):
        assert item.native_value == time(8)


async def test_async_setup_entry_filters_times(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add selected, supported times with available capabilities."""
    install_config(
        {
            "selected": {"type": Platform.TIME},
            "not_selected": {"type": Platform.TIME},
            "missing": {
                "type": Platform.TIME,
                "required_attribute": "capability",
            },
            "unsupported": {
                "type": Platform.TIME,
                "models": ["OTHER"],
            },
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(
        device,
        switches=["selected", "missing", "unsupported"],
    )
    await async_setup_entry(hass, entry, add_entities)
    assert [item._entity_key for item in add_entities.call_args.args[0]] == ["selected"]


@pytest.mark.parametrize(
    ("key", "config", "expected"),
    [
        ("start_hour", {}, ("start_hour", "start_min")),
        ("start", {}, ("start_hour", "start_min")),
        (
            "start",
            {"hour_attr": "custom_hour", "min_attr": "custom_min"},
            ("custom_hour", "custom_min"),
        ),
    ],
)
def test_regular_time_attribute_resolution(
    key: str,
    config: dict[str, str],
    expected: tuple[str, str],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Resolve explicit and conventional hour/minute attribute names."""
    install_config({key: {"type": Platform.TIME, **config}})
    device, _ = device_factory()
    item = MideaTime(device, key)
    assert (item._hour_attr, item._min_attr) == expected


@pytest.mark.parametrize(
    ("hour", "minute", "expected"),
    [
        (8, 30, time(8, 30)),
        (None, 30, None),
        (8, None, None),
        (24, 0, None),
        ("bad", 0, None),
    ],
)
def test_regular_time_read_and_write(
    hour: object,
    minute: object,
    expected: time | None,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Read valid hour/minute pairs and safely reject malformed reports."""
    install_config({"start": {"type": Platform.TIME}})
    device, _ = device_factory(
        attributes={"start_hour": hour, "start_min": minute},
    )
    item = MideaTime(device, "start")
    assert item.native_value == expected
    item.set_value(time(9, 45))
    assert device.set_attribute.call_args_list[-2:] == [
        call("start_hour", 9),
        call("start_min", 45),
    ]


def test_regular_time_refreshes_for_minute_report(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Refresh HA state when a mapped minute attribute changes."""
    install_config({"start_hour": {"type": Platform.TIME}})
    device, _ = device_factory()
    item = MideaTime(device, "start_hour")
    item.hass = Mock()
    item.schedule_update_if_running = Mock()

    item.update_state({"start_min": 45})
    item.update_state({"unrelated": True})

    item.schedule_update_if_running.assert_called_once_with()
