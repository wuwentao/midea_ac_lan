"""Time for Midea Lan."""

import logging
from datetime import UTC, datetime, time, timedelta
from typing import cast

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from midealan.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_device
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


def _next_completion_time(now: datetime, value: time) -> datetime:
    """Choose the earliest future occurrence, rejecting nonexistent local times.

    Returns
    -------
    datetime
        The earliest valid local completion datetime in the next 24 hours.

    Raises
    ------
    ValueError
        If the selected local time does not exist or is outside the next 24 hours.

    """
    now_utc = now.astimezone(UTC)
    limit = now_utc + timedelta(days=1)
    for day in range(2):
        local = datetime.combine(
            now.date() + timedelta(days=day),
            value.replace(tzinfo=None),
            tzinfo=now.tzinfo,
        )
        occurrences = []
        for fold in (0, 1):
            candidate = local.replace(fold=fold)
            utc = candidate.astimezone(UTC)
            if utc.astimezone(now.tzinfo).replace(tzinfo=None) == local.replace(
                tzinfo=None,
            ):
                occurrences.append(utc)
        if not occurrences and local.replace(tzinfo=None) > now.replace(tzinfo=None):
            msg = "Selected completion time does not exist in the local timezone"
            raise ValueError(msg)
        future = [utc for utc in occurrences if now_utc < utc <= limit]
        if future:
            return min(future).astimezone(now.tzinfo)
    msg = "Completion time must be within the next 24 hours"
    raise ValueError(msg)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up times for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    times = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] == Platform.TIME
            and supports_device(device.model, device.subtype, config)
            and entity_key in extra_switches
        ):
            required_attribute = config.get("required_attribute")
            if (
                required_attribute is not None
                and required_attribute not in device.attributes
            ):
                continue
            dev = MideaTime(device, entity_key)
            times.append(dev)
    async_add_entities(times)


class MideaTime(MideaEntity, TimeEntity):
    """Represent a Midea time entity."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea time entity init."""
        super().__init__(device, entity_key)
        # Config can specify hour/min attribute names explicitly:
        #   "hour_attr": "timing_regeneration_hour"
        #   "min_attr": "timing_regeneration_min"
        # Otherwise derive from entity_key: if it ends with "_hour",
        # use it directly and replace "_hour" with "_min" for minute.
        self._hour_attr = self._config.get("hour_attr")
        self._min_attr = self._config.get("min_attr")
        if self._hour_attr is None:
            if self._entity_key.endswith("_hour"):
                self._hour_attr = self._entity_key
                self._min_attr = self._entity_key[:-5] + "_min"
            else:
                self._hour_attr = f"{self._entity_key}_hour"
                self._min_attr = f"{self._entity_key}_min"

    @property
    def native_value(self) -> time | None:
        """Native value of the entity."""
        if self._config.get("completion_attribute"):
            value = self._device.get_attribute(self._config["completion_attribute"])
            if not isinstance(value, str):
                return None
            try:
                completion = datetime.fromisoformat(value)
            except ValueError:
                completion = None
            if completion is None or completion.tzinfo is None:
                _LOGGER.warning(
                    "Invalid completion time for %s: %s",
                    self._entity_key,
                    value,
                )
                return None
            return cast("time", dt_util.as_local(completion).time())
        hour = self._device.get_attribute(self._hour_attr)
        minute = self._device.get_attribute(self._min_attr)
        if hour is None or minute is None:
            return None
        try:
            return time(hour=cast("int", hour), minute=cast("int", minute))
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Invalid time value for %s: hour=%s, minute=%s",
                self._entity_key,
                hour,
                minute,
            )
            return None

    def set_value(self, value: time) -> None:
        """Set entity value.

        Raises
        ------
        ValueError
            If a completion time includes seconds rather than whole minutes.

        """
        if self._config.get("completion_attribute"):
            if value.second or value.microsecond:
                msg = "Completion time must use whole minutes"
                raise ValueError(msg)
            target = _next_completion_time(dt_util.now(), value)
            self._device.set_attribute(
                self._config["completion_attribute"],
                target.isoformat(),
            )
            return
        self._device.set_attribute(self._hour_attr, value.hour)
        self._device.set_attribute(self._min_attr, value.minute)
