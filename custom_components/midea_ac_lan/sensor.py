"""Sensor for Midea Lan."""

import time
from datetime import timedelta
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from midealocal.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_model
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_sensors = config_entry.options.get(CONF_SENSORS, [])
    sensors = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] != Platform.SENSOR
            or not supports_model(device.model, config)
            or (not config.get("default") and entity_key not in extra_sensors)
        ):
            continue
        required_attribute = config.get("required_attribute")
        if (
            required_attribute is not None
            and required_attribute not in device.attributes
        ):
            continue
        sensor = (
            MideaEstimatedUsageSensor(device, entity_key)
            if config.get("estimate")
            else MideaSensor(device, entity_key)
        )
        sensors.append(sensor)
    async_add_entities(sensors)


class MideaSensor(MideaEntity, SensorEntity):
    """Represent a Midea sensor."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize Midea sensor."""
        super().__init__(device, entity_key)
        # Timer configuration: "down" for countdown, "up" for countup
        self._timer = self._config.get("timer")
        self._timer_base_value: int | None = None
        self._timer_last_update: float | None = None
        self._timer_listener = None

    @property
    def native_value(self) -> StateType:
        """Native value of the sensor."""
        value = self._device.get_attribute(self._entity_key)
        # If an options mapping exists, translate the raw value to its enum key.
        options = self._config.get("options")
        if options is not None and isinstance(value, int):
            # For an enum sensor an unmapped value is not a valid state, so
            # report it as unknown (None) instead of leaking the raw int.
            return cast("StateType", options.get(value))

        # Timer mode: calculate elapsed time
        if self._timer and isinstance(value, int):
            now = time.time()
            if self._timer_last_update is not None:
                elapsed = int(now - self._timer_last_update)
                if self._timer == "down":
                    # Countdown: value decreases by elapsed seconds
                    return cast("StateType", max(0, value - elapsed))
                if self._timer == "up":
                    # Countup: value increases by elapsed seconds
                    return cast("StateType", value + elapsed)
            return cast("StateType", value)

        return cast("StateType", value)

    @property
    def device_class(self) -> SensorDeviceClass:
        """Device class of the sensor."""
        return cast("SensorDeviceClass", self._config.get("device_class"))

    @property
    def state_class(self) -> SensorStateClass | None:
        """State class of the sensor."""
        return cast("SensorStateClass | None", self._config.get("state_class"))

    @property
    def options(self) -> list[str] | None:
        """List of possible states for an enum sensor."""
        if self.device_class != SensorDeviceClass.ENUM:
            return None
        options = self._config.get("options")
        return list(options.values()) if options else None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Unit of measurement for the sensor."""
        return cast("str | None", self._config.get("unit"))

    @property
    def suggested_display_precision(self) -> int | None:
        """Suggested number of decimal digits for display."""
        return cast("int | None", self._config.get("suggested_display_precision"))

    @property
    def capability_attributes(self) -> dict[str, Any] | None:
        """Capability attributes of the sensor."""
        if self.options is not None:
            return {"options": self.options}
        return {"state_class": self.state_class} if self.state_class else {}

    async def async_added_to_hass(self) -> None:
        """Subscribe to device updates and start timer tracking."""
        await super().async_added_to_hass()
        # Start timer tracking if configured
        if self._timer:
            value = self._device.get_attribute(self._entity_key)
            if isinstance(value, int):
                self._timer_base_value = value
                self._timer_last_update = time.time()
            # Register 1-second interval update
            self._timer_listener = async_track_time_interval(
                self.hass,
                self._async_timer_update,
                timedelta(seconds=1),
            )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from device updates and stop timer tracking."""
        await super().async_will_remove_from_hass()
        if self._timer_listener:
            self._timer_listener()
            self._timer_listener = None

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Update entity state."""
        if self._timer and self._entity_key in status:
            value = self._device.get_attribute(self._entity_key)
            if isinstance(value, int):
                self._timer_base_value = value
                self._timer_last_update = time.time()
        super().update_state(status)

    @callback
    def _async_timer_update(self, _now: Any) -> None:  # ruff:ignore[any-type]
        """Update timer state every second."""
        self.schedule_update_ha_state()


class MideaEstimatedUsageSensor(MideaSensor, RestoreEntity):
    """Represent estimated dishwasher usage accumulated per run.

    The dishwasher does not report actual energy/water usage, so this sensor
    accumulates a fixed per-mode estimate (from the product manual) once each
    time a wash run *completes*. Completion is detected by the device
    ``progress`` attribute reaching ``"Complete"``; a cancelled or errored run
    never reaches that state and is therefore not counted.
    """

    _COMPLETE_PROGRESS = "Complete"
    _RUNNING_STATUS = "Running"

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize estimated usage sensor."""
        super().__init__(device, entity_key)
        self._native_value: float = 0.0
        self._last_progress: str | None = None
        self._running_mode: str | None = None

    async def async_added_to_hass(self) -> None:
        """Register for device updates and restore the accumulated value."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            try:
                self._native_value = float(last_state.state)
            except (TypeError, ValueError):
                self._native_value = 0.0
        self._last_progress = cast(
            "str | None",
            self._device.get_attribute("progress"),
        )
        if self._device.get_attribute("status") == self._RUNNING_STATUS:
            self._running_mode = cast("str | None", self._device.get_attribute("mode"))

    @property
    def native_value(self) -> StateType:
        """Accumulated estimated usage."""
        return round(self._native_value, 3)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Estimate metadata for the sensor."""
        estimate = cast("dict[str, Any]", self._config["estimate"])
        return {
            "estimate_source": "fixed_per_wash_mode",
            "known_modes": list(cast("dict[str, float]", estimate["values"]).keys()),
            "last_progress": self._last_progress,
            "running_mode": self._running_mode,
        }

    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Accumulate the estimate once when a dishwasher run completes."""
        current_status = self._device.get_attribute("status")
        current_progress = cast(
            "str | None",
            self._device.get_attribute("progress"),
        )
        current_mode = cast("str | None", self._device.get_attribute("mode"))

        # Remember the mode selected while the machine is actually running so we
        # can still attribute usage after it stops reporting the mode on finish.
        if current_status == self._RUNNING_STATUS:
            self._running_mode = current_mode

        # Count once, on the edge into the "Complete" progress state. A cancel or
        # error transition never reaches "Complete", so it is not counted.
        if (
            current_progress == self._COMPLETE_PROGRESS
            and self._last_progress != self._COMPLETE_PROGRESS
        ):
            mode = self._running_mode or current_mode
            values = cast("dict[str, float]", self._config["estimate"]["values"])
            if mode in values:
                self._native_value += values[mode]
            self._running_mode = None

        self._last_progress = current_progress
        super().update_state(status)
        if (
            self.hass
            and not self.hass.is_stopping
            and ("progress" in status or "status" in status or "mode" in status)
        ):
            self.schedule_update_ha_state()
