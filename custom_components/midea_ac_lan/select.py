"""Select for Midea Lan."""

import time
from asyncio import CancelledError
from threading import Lock, RLock
from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from midealan.device import DeviceType, MideaDevice

from .const import (
    DEVICES,
    DOMAIN,
    PERSON_AIRFLOW_AVOID,
    PERSON_AIRFLOW_MODE,
    PERSON_AIRFLOW_MODES,
    PERSON_AIRFLOW_OFF,
    PERSON_AIRFLOW_TOWARD,
    supports_device,
)
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

if TYPE_CHECKING:
    from asyncio import Task, TimerHandle

    from midealan.devices.ac import MideaACDevice
    from midealan.devices.e1 import MideaE1Device


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up selects for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    selects = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] != Platform.SELECT
            or not supports_device(device.model, device.subtype, config)
            or (not config.get("default") and entity_key not in extra_switches)
        ):
            continue
        required_attribute = config.get("required_attribute")
        if (
            required_attribute is not None
            and required_attribute not in device.attributes
        ):
            continue
        dev: MideaSelect
        if device.device_type == DeviceType.AC and entity_key == PERSON_AIRFLOW_MODE:
            dev = MideaPersonAirflowSelect(device, entity_key)
        else:
            dev = MideaSelect(device, entity_key)
        selects.append(dev)
    async_add_entities(selects)


class MideaSelect(MideaEntity, SelectEntity):
    """Represent a Midea select."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea select init."""
        super().__init__(device, entity_key)
        self._options_name = self._config.get("options")
        self._options_dict_name = self._config.get("options_dict")
        self._options_method = self._config.get("options_method")

    @property
    def options(self) -> list[str]:
        """Available options for the entity."""
        if self._options_method:
            return cast(
                "list[str]",
                getattr(self._device, self._options_method)(self._attribute_key),
            )
        if self._options_dict_name:
            options = self._get_options_dict()
            codes_by_model = self._config.get("options_codes_by_model", {})
            codes = codes_by_model.get(str(self._device.model)) or self._config.get(
                "options_codes",
            )
            exclude = self._config.get("options_exclude_codes", [])
            if codes:
                return [
                    options[code]
                    for code in codes
                    if code in options and code not in exclude
                ]
            return [name for code, name in options.items() if code not in exclude]
        if isinstance(self._options_name, dict):
            return list(self._options_name.values())
        if isinstance(self._options_name, list):
            return [str(option) for option in self._options_name]
        return cast("list", getattr(self._device, self._options_name))

    @property
    def current_option(self) -> str | None:
        """Currently selected option."""
        value = self._device.get_attribute(self._state_attribute_key)
        if value is None:
            return None
        state_map = self._config.get("state_map")
        if state_map is not None:
            value = state_map.get(value)
        if isinstance(self._options_name, dict):
            return cast("str | None", self._options_name.get(value))
        option = (
            str(value) if isinstance(self._options_name, list) else cast("str", value)
        )
        return option if option in self.options else None

    @property
    def available(self) -> bool:
        """Whether the entity is available."""
        if not super().available:
            return False
        power_attribute = self._config.get("available_power_attribute")
        return not power_attribute or bool(self._device.get_attribute(power_attribute))

    def select_option(self, option: str) -> None:
        """Select entity option.

        Raises
        ------
        ValueError
            If a mapped option is not supported.

        """
        if self._config.get("set_message") == "e1_work_mode":
            self._select_e1_work_mode(option)
            return
        value: Any = option
        if isinstance(self._options_name, dict):
            value = self._get_dict_key_by_value(self._options_name, option)
            if value is None:
                raise ValueError(f"Unsupported select option: {option}")
        elif self._config.get("option_type") == "int":
            value = int(option)
        self._device.set_attribute(self._attribute_key, value)

    def _get_options_dict(self) -> dict[int, str]:
        """Return option dict from the backing midea-lan device.

        Returns
        -------
        Option labels keyed by the raw mode code.

        """
        return cast("dict[int, str]", getattr(self._device, self._options_dict_name))

    def _select_e1_work_mode(self, option: str) -> None:
        """Set dishwasher work mode via midea-lan's public E1 API.

        Raises
        ------
        ValueError
            If the requested option is not a supported work mode.

        """
        mode = self._get_dict_key_by_value(self._get_options_dict(), option)
        if mode is None:
            raise ValueError(f"Unsupported dishwasher mode: {option}")
        cast("MideaE1Device", self._device).set_work_mode(mode)

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Update entity state."""
        super().update_state(status)
        power_attribute = self._config.get("available_power_attribute")
        if (
            power_attribute
            and self.hass
            and (self._attribute_key in status or power_attribute in status)
        ):
            self.schedule_update_if_running()

    @staticmethod
    def _get_dict_key_by_value(source: dict[int, str], value: str) -> int | None:
        for key, item in source.items():
            if item == value:
                return key
        return None


class MideaPersonAirflowSelect(MideaSelect, RestoreEntity):
    """Remember the mutually exclusive person-airflow preference across boots."""

    _RESTORE_DELAY_SECONDS = 2.0
    _WRITE_SETTLE_SECONDS = 15.0
    _ACTIVE_MODES = (PERSON_AIRFLOW_TOWARD, PERSON_AIRFLOW_AVOID)

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Keep the preference separate from temporary firmware boot reports."""
        super().__init__(device, entity_key)
        self._desired_option: str | None = None
        self._last_power: bool | None = None
        self._last_available: bool | None = None
        self._pending_until = 0.0
        self._restore_handle: TimerHandle | None = None
        self._restore_task: Task[None] | None = None
        self._restore_generation = 0
        self._removed = False
        self._preference_lock = RLock()
        self._write_lock = Lock()
        self._restore_requested = False
        self._manual_pending_generation: int | None = None
        self._sending_generations: set[int] = set()

    @property
    def current_option(self) -> str | None:
        """The remembered preference, or unknown without valid evidence."""
        return self._desired_option

    async def async_added_to_hass(self) -> None:
        """Restore HA's preference, then schedule it only for a powered unit."""
        self._removed = False
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in PERSON_AIRFLOW_MODES:
            self._desired_option = last_state.state
        else:
            self._desired_option = self._actual_option()
        self._last_power = bool(self._device.get_attribute("power"))
        self._last_available = bool(self._device.available)
        if self._last_power and self._desired_option in self._ACTIVE_MODES:
            self._schedule_restore()
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Invalidate timers and queued workers before unregistering updates."""
        self._removed = True
        self._cancel_restore()
        await super().async_will_remove_from_hass()

    def select_option(self, option: str) -> None:
        """Remember the choice and apply it while powered and available."""
        generation = self._prepare_selection(option)
        if generation is None:
            return
        self._apply_user_option(generation)
        # The synchronous select API runs in HA's executor.
        if not self._removed and not self.hass.is_stopping:
            self.schedule_update_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Bind a user service request before it enters the executor queue.

        Raises:
            CancelledError: If HA cancels the service task.

        """
        generation = self._prepare_selection(option)
        if generation is None:
            return
        try:
            await self.hass.async_add_executor_job(self._apply_user_option, generation)
        except (Exception, CancelledError):
            # Cancelling the await cannot remove an already queued worker.
            with self._preference_lock:
                if generation == self._restore_generation:
                    self._cancel_restore_locked()
                    self._pending_until = 0.0
            raise
        finally:
            self._finish_manual_request(generation)
        if not self._removed and not self.hass.is_stopping:
            self.async_write_ha_state()

    def _prepare_selection(self, option: str) -> int | None:
        """Remember a live user request and invalidate older queued work.

        Returns:
            The bound request generation, or None for an unloaded/stopping entity.

        Raises:
            ValueError: If the requested option is invalid.

        """
        if option not in PERSON_AIRFLOW_MODES:
            raise ValueError(f"Unsupported person-airflow mode: {option}")
        with self._preference_lock:
            if self._removed or self.hass.is_stopping:
                return None
            self._cancel_restore()
            self._desired_option = option
            self._manual_pending_generation = self._restore_generation
            return self._restore_generation

    def _apply_user_option(self, generation: int) -> None:
        """Apply an eligible queued user choice, including explicit off."""
        try:
            self._apply_desired_option(generation, restoring=False)
        finally:
            self._finish_manual_request(generation)

    def _finish_manual_request(self, generation: int) -> None:
        """Release only this request's queue/send protection, never a newer one."""
        with self._preference_lock:
            if self._manual_pending_generation == generation:
                self._manual_pending_generation = None

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Observe reports without crossing an in-flight preference transition."""
        with self._preference_lock:
            self._update_preference_state(status)

    def _update_preference_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Observe external changes without forgetting a powered-off preference."""
        if self._removed or not self.hass or self.hass.is_stopping:
            return
        if not {"power", "wind_straight", "wind_avoid", "available"}.intersection(
            status,
        ):
            return
        power = bool(self._device.get_attribute("power"))
        available = bool(self._device.available)
        power_just_enabled = power and self._last_power is False
        available_just_enabled = available and self._last_available is False
        self._last_power = power
        self._last_available = available
        if (
            power_just_enabled or available_just_enabled
        ) and self._desired_option in self._ACTIVE_MODES:
            self._restore_requested = True
            self.hass.loop.call_soon_threadsafe(
                self._schedule_restore,
                self._restore_generation,
            )
        elif (
            power and available and {"wind_straight", "wind_avoid"}.intersection(status)
        ):
            actual = self._actual_option()
            request_pending = (
                self._restore_requested
                or self._manual_pending_generation is not None
                or bool(self._sending_generations)
            )
            if (
                actual is not None
                and not request_pending
                and (
                    actual == self._desired_option
                    or time.monotonic() >= self._pending_until
                )
            ):
                self._desired_option = actual
                self._pending_until = 0.0
        self.schedule_update_if_running()

    def _cancel_restore(self) -> None:
        """Invalidate queued work immediately, including from HA's executor."""
        with self._preference_lock:
            self._cancel_restore_locked()

    def _cancel_restore_locked(self) -> None:
        """Cancel scheduled work while holding the preference-state lock."""
        self._restore_generation += 1
        self._restore_requested = False
        self._manual_pending_generation = None
        handle, self._restore_handle = self._restore_handle, None
        task, self._restore_task = self._restore_task, None
        # select_option runs in an executor. Cancellation belongs on HA's loop;
        # the generation invalidates a worker even before cancellation runs.
        if handle is not None:
            self.hass.loop.call_soon_threadsafe(handle.cancel)
        if task is not None:
            self.hass.loop.call_soon_threadsafe(task.cancel)

    def _can_apply(self, generation: int) -> bool:
        """Check the current object and device immediately before a write.

        Returns:
            Whether this request can still act on the powered device.

        """
        return bool(
            not self._removed
            and generation == self._restore_generation
            and self.hass
            and not self.hass.is_stopping
            and self._device.available
            and self._device.get_attribute("power")
            and self._desired_option in PERSON_AIRFLOW_MODES,
        )

    def _can_restore(self, generation: int) -> bool:
        """Check a restore's lifecycle and active preference.

        Returns:
            Whether this restore may still apply an active person-airflow option.

        """
        return (
            self._can_apply(generation) and self._desired_option in self._ACTIVE_MODES
        )

    @callback
    def _schedule_restore(self, expected_generation: int | None = None) -> None:
        """Bind a delayed restore to the current object generation."""
        with self._preference_lock:
            self._schedule_restore_locked(expected_generation)

    def _schedule_restore_locked(self, expected_generation: int | None) -> None:
        """Keep request and timer transitions atomic to incoming reports."""
        if (
            expected_generation is not None
            and expected_generation != self._restore_generation
        ) or not self._can_restore(self._restore_generation):
            return
        self._cancel_restore()
        self._restore_requested = True
        self._restore_handle = self.hass.loop.call_later(
            self._RESTORE_DELAY_SECONDS,
            self._restore_after_power_on,
            self._restore_generation,
        )

    @callback
    def _restore_after_power_on(self, generation: int | None = None) -> None:
        """Queue the synchronous library call through HA's executor."""
        with self._preference_lock:
            self._queue_restore_locked(generation)

    def _queue_restore_locked(self, generation: int | None) -> None:
        """Keep the preference protected while its executor worker is queued."""
        if generation is None:
            generation = self._restore_generation
        if not self._can_restore(generation):
            return
        self._restore_handle = None
        self._restore_task = self.hass.async_create_task(
            self._async_restore_after_power_on(generation),
        )

    async def _async_restore_after_power_on(self, generation: int) -> None:
        """Recheck before queueing; cancellation alone cannot stop executor work."""
        try:
            if self._can_restore(generation):
                await self.hass.async_add_executor_job(
                    self._apply_desired_option,
                    generation,
                )
        finally:
            with self._preference_lock:
                if generation == self._restore_generation:
                    self._restore_task = None
                    self._restore_requested = False

    def _apply_desired_option(
        self,
        generation: int | None = None,
        *,
        restoring: bool = True,
    ) -> None:
        """Serialize worker writes, then recheck intent at the SDK boundary."""
        if generation is None:
            with self._preference_lock:
                generation = self._restore_generation
        # Only executor workers take this lock. The event loop never waits on it.
        with self._write_lock:
            self._write_preference(generation, restoring=restoring)

    def _write_preference(self, generation: int, *, restoring: bool) -> None:
        """Send with established write order but without holding the memory lock."""
        with self._preference_lock:
            eligible = (
                self._can_restore(generation)
                if restoring
                else self._can_apply(generation)
            )
            if not eligible:
                return
            send_generation = generation
            option = self._desired_option
            self._sending_generations.add(send_generation)
        try:
            # Never hold a preference lock during a synchronous network write.
            cast("MideaACDevice", self._device).set_person_airflow_mode(
                cast("str", option),
            )
        except Exception:
            with self._preference_lock:
                if send_generation == self._restore_generation:
                    self._pending_until = 0.0
            raise
        else:
            with self._preference_lock:
                if send_generation == self._restore_generation:
                    self._pending_until = time.monotonic() + self._WRITE_SETTLE_SECONDS
        finally:
            with self._preference_lock:
                self._sending_generations.discard(send_generation)

    def _actual_option(self) -> str | None:
        """Translate valid mutually exclusive device flags without guessing.

        Returns:
            The observed option, or None for unknown or conflicting flags.

        """
        toward = self._device.get_attribute("wind_straight")
        avoid = self._device.get_attribute("wind_avoid")
        if toward is None or avoid is None or (toward and avoid):
            return None
        if avoid:
            return PERSON_AIRFLOW_AVOID
        if toward:
            return PERSON_AIRFLOW_TOWARD
        return PERSON_AIRFLOW_OFF
