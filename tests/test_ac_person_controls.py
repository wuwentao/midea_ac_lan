"""Offline contracts for exact-model controls and preserved entity records."""

import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, Mock, patch

import midea_ac_lan
import pytest
from homeassistant.const import CONF_SWITCHES
from homeassistant.helpers.entity_registry import RegistryEntryDisabler
from midea_ac_lan.binary_sensor import MideaBinarySensor
from midea_ac_lan.climate import MideaACClimate
from midea_ac_lan.const import (
    DOMAIN,
    LIGHT_SENSITIVE_CONTROL,
    PERSON_AIRFLOW_MODE,
    supports_device,
)
from midea_ac_lan.midea_devices import MIDEA_DEVICES
from midea_ac_lan.select import MideaPersonAirflowSelect, MideaSelect
from midea_ac_lan.switch import MideaSwitch
from midealan.devices.ac import DeviceAttributes as ACAttributes


def make_device() -> tuple[Mock, dict[str, bool | None]]:
    """Build an inert device without discovery, threads or appliance sockets."""
    attributes: dict[str, bool | None] = {
        "power": False,
        "light_sensitive": True,
        "wind_straight": False,
        "wind_avoid": False,
    }
    device = Mock()
    device.device_type = 172
    device.device_id = 1
    device.model = "220F4047"
    device.subtype = 8
    device.name = "Offline AC"
    device.available = True
    device.attributes = attributes
    device.get_attribute.side_effect = attributes.get
    return (device, attributes)


def make_select() -> tuple[MideaPersonAirflowSelect, Mock, dict[str, bool | None]]:
    """Bind a select to an inert scheduler so timers never wait in real time."""
    device, attributes = make_device()
    entity = MideaPersonAirflowSelect(device, PERSON_AIRFLOW_MODE)
    entity.hass = Mock()
    entity.hass.is_stopping = False
    entity.hass.loop.call_soon_threadsafe.side_effect = lambda callback, *args: (
        callback(*args)
    )
    entity.hass.async_create_task.side_effect = lambda coroutine: (
        asyncio.get_running_loop().create_task(coroutine)
    )
    entity.hass.async_add_executor_job = AsyncMock(
        side_effect=lambda function, *args: function(*args),
    )
    entity.schedule_update_ha_state = Mock()
    entity.schedule_update_if_running = Mock()
    entity.async_write_ha_state = Mock()
    return (entity, device, attributes)


class TestACControlMappings(TestCase):
    """Exercise generic attribute routing and exact-model exposure."""

    @staticmethod
    def test_light_uses_existing_boolean_switch_and_report_mapping() -> None:
        """Route boolean light state and writes through the generic switch."""
        device, attributes = make_device()
        entity = MideaSwitch(device, LIGHT_SENSITIVE_CONTROL)
        entity.hass = Mock()
        entity.hass.is_stopping = False
        assert entity.is_on is True
        entity.turn_off()
        device.set_attribute.assert_called_once_with(
            attr=ACAttributes.light_sensitive,
            value=False,
        )
        attributes["light_sensitive"] = False
        with patch.object(entity, "schedule_update_if_running") as refresh:
            entity.update_state({"light_sensitive": False})
        refresh.assert_called_once_with()
        assert entity.is_on is False
        assert entity.unique_id == f"{DOMAIN}.1_{LIGHT_SENSITIVE_CONTROL}"

    @staticmethod
    def test_raw_status_entities_follow_library_booleans() -> None:
        """Preserve unknown and boolean status values from the library."""
        device, attributes = make_device()
        for key in (
            ACAttributes.light_sensitive,
            ACAttributes.wind_straight,
            ACAttributes.wind_avoid,
        ):
            entity = MideaBinarySensor(device, key)
            for value in (None, False, True):
                attributes[key] = value
                assert entity.is_on is value

    @staticmethod
    def test_new_entities_are_exact_model_and_subtype_only() -> None:
        """Expose new entities only for the verified exact model and subtype."""
        entities = cast("dict[str, dict[str, Any]]", MIDEA_DEVICES[172]["entities"])
        for key in (
            LIGHT_SENSITIVE_CONTROL,
            PERSON_AIRFLOW_MODE,
            ACAttributes.light_sensitive,
            ACAttributes.wind_straight,
            ACAttributes.wind_avoid,
        ):
            config = entities[key]
            assert supports_device("220F4047", 8, config)
            assert not supports_device("220F4047", 9, config)
            assert not supports_device("OTHER", 8, config)
            assert config["preserve_registry"]

    @staticmethod
    def test_only_the_failed_swing_control_path_is_excluded() -> None:
        """Restrict only the failed swing path without hiding untested controls."""
        device, _ = make_device()
        climate = object.__new__(MideaACClimate)
        climate._device = device
        climate._customize_swing = True
        assert not climate._capability_swing()
        device.subtype = 9
        assert climate._capability_swing()
        device.subtype = 8
        device.model = "OTHER"
        assert climate._capability_swing()
        entities = cast("dict[str, dict[str, Any]]", MIDEA_DEVICES[172]["entities"])
        for key in (ACAttributes.swing_horizontal, ACAttributes.swing_vertical):
            config = entities[key]
            assert not supports_device("220F4047", 8, config)
            assert supports_device("220F4047", 9, config)
            assert supports_device("OTHER", 8, config)
        for key in (
            ACAttributes.dry,
            ACAttributes.comfort_mode,
            ACAttributes.sleep_mode,
            ACAttributes.smart_eye,
            ACAttributes.eco_mode,
            ACAttributes.self_clean,
        ):
            assert supports_device("220F4047", 8, entities[key])


class TestPreservedACRegistry(TestCase):
    """Preserve old identities and user disablement through applicability changes."""

    @staticmethod
    def test_disable_preserves_record_and_user_choice() -> None:
        """Keep user entity identities and existing user disablement."""
        device, _ = make_device()
        key = ACAttributes.swing_horizontal
        entity_id = "switch.original_user_name"
        entry = SimpleNamespace(
            disabled_by=None,
            platform=DOMAIN,
            unique_id=f"{DOMAIN}.1_{key}",
            config_entry_id="owned_entry",
        )
        registry = Mock()
        registry.async_get_entity_id.side_effect = (
            lambda _domain, _integration, unique_id: (
                entity_id if unique_id == f"{DOMAIN}.1_{key}" else None
            )
        )
        registry.async_get.side_effect = lambda lookup: (
            entry if lookup == entity_id else None
        )
        with patch("midea_ac_lan.er.async_get", return_value=registry):
            midea_ac_lan._remove_unsupported_entities(
                Mock(),
                device,
                preserved_only=True,
            )
            registry.async_update_entity.assert_called_once_with(
                entity_id,
                disabled_by=RegistryEntryDisabler.INTEGRATION,
            )
            registry.async_remove.assert_not_called()
            registry.async_update_entity.reset_mock()
            entry.disabled_by = RegistryEntryDisabler.USER
            midea_ac_lan._remove_unsupported_entities(
                Mock(),
                device,
                preserved_only=True,
            )
            registry.async_update_entity.assert_not_called()
            registry.async_remove.assert_not_called()

    @staticmethod
    def test_supported_selected_record_can_be_reenabled_without_recreation() -> None:
        """Reenable an integration-disabled selected record without replacing it."""
        device, _ = make_device()
        key = ACAttributes.swing_horizontal
        entities = cast("dict[str, dict[str, Any]]", MIDEA_DEVICES[172]["entities"])
        config = entities[key]
        entry = SimpleNamespace(
            disabled_by=RegistryEntryDisabler.INTEGRATION,
            platform=DOMAIN,
            unique_id=f"{DOMAIN}.1_{key}",
            config_entry_id="owned_entry",
        )
        registry = Mock()
        registry.async_get_entity_id.side_effect = (
            lambda _domain, _integration, unique_id: (
                "switch.original_user_name"
                if unique_id == f"{DOMAIN}.1_{key}"
                else None
            )
        )
        registry.async_get.side_effect = lambda lookup: (
            entry if lookup == "switch.original_user_name" else None
        )
        config_entry = SimpleNamespace(
            options={CONF_SWITCHES: [key]},
            entry_id="owned_entry",
        )
        with (
            patch.dict(config, {"excluded_devices": []}),
            patch("midea_ac_lan.er.async_get", return_value=registry),
        ):
            midea_ac_lan._remove_unsupported_entities(
                Mock(),
                device,
                config_entry=config_entry,
                preserved_only=True,
            )
        registry.async_update_entity.assert_called_once_with(
            "switch.original_user_name",
            disabled_by=None,
        )
        registry.async_remove.assert_not_called()


class TestPersonAirflowPreference(IsolatedAsyncioTestCase):
    """Verify preference restoration separately from real appliance acceptance."""

    @staticmethod
    async def test_restore_valid_history_and_cancel_on_unload() -> None:
        """Restore a valid preference and cancel its timer on unload."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        with (
            patch.object(MideaSelect, "async_added_to_hass", new=AsyncMock()),
            patch.object(
                entity,
                "async_get_last_state",
                new=AsyncMock(return_value=SimpleNamespace(state="toward")),
            ),
        ):
            await entity.async_added_to_hass()
        assert entity.current_option == "toward"
        entity.hass.loop.call_later.assert_called_once_with(
            2.0,
            entity._restore_after_power_on,
            entity._restore_generation,
        )
        device.set_person_airflow_mode.assert_not_called()
        handle = cast("Mock", entity._restore_handle)
        with patch.object(MideaSelect, "async_will_remove_from_hass", new=AsyncMock()):
            await entity.async_will_remove_from_hass()
        handle.cancel.assert_called_once_with()
        assert entity._restore_handle is None

    @staticmethod
    async def test_missing_history_does_not_invent_unknown_device_state() -> None:
        """Keep missing device reports unknown when no history is available."""
        entity, device, attributes = make_select()
        attributes["wind_straight"] = None
        attributes["wind_avoid"] = None
        with (
            patch.object(MideaSelect, "async_added_to_hass", new=AsyncMock()),
            patch.object(
                entity,
                "async_get_last_state",
                new=AsyncMock(return_value=None),
            ),
        ):
            await entity.async_added_to_hass()
        assert entity.current_option is None
        device.set_person_airflow_mode.assert_not_called()
        entity.hass.loop.call_later.assert_not_called()

    @staticmethod
    async def test_offline_choice_waits_for_power_and_ignores_boot_reset() -> None:
        """Retain the offline choice through power-on and transient resets."""
        entity, device, attributes = make_select()
        entity._last_power = False
        entity._last_available = True
        entity.select_option("toward")
        device.set_person_airflow_mode.assert_not_called()
        attributes["power"] = True
        entity.update_state({"power": True})
        assert entity._restore_handle is not None
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "toward"
        with patch("midea_ac_lan.select.time.monotonic", return_value=100.0):
            entity._restore_after_power_on()
            await asyncio.sleep(0)
        device.set_person_airflow_mode.assert_called_once_with("toward")
        with patch("midea_ac_lan.select.time.monotonic", return_value=110.0):
            entity.update_state({"wind_straight": False})
        assert entity.current_option == "toward"
        with patch("midea_ac_lan.select.time.monotonic", return_value=116.0):
            entity.update_state({"wind_straight": False})
        assert entity.current_option == "off"

    @staticmethod
    async def test_reconnect_restores_and_external_changes_are_observed() -> None:
        """Restore after reconnect and accept later external mode changes."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "avoid"
        entity._last_power = True
        entity._last_available = False
        entity.update_state({"available": True})
        entity._restore_after_power_on()
        await asyncio.sleep(0)
        device.set_person_airflow_mode.assert_called_once_with("avoid")
        attributes["wind_avoid"] = True
        entity.update_state({"wind_avoid": True})
        assert entity.current_option == "avoid"
        attributes["wind_avoid"] = False
        attributes["wind_straight"] = True
        entity.update_state({"wind_straight": True})
        assert entity.current_option == "toward"
        attributes["wind_avoid"] = True
        assert entity._actual_option() is None
        entity.update_state({"wind_avoid": True})
        assert entity.current_option == "toward"

    @staticmethod
    async def test_shutdown_power_and_unavailability_stop_delayed_write() -> None:
        """Reject delayed writes after shutdown, power-off or disconnection."""
        for stop_reason in ("shutdown", "power", "available"):
            entity, device, attributes = make_select()
            attributes["power"] = True
            entity._desired_option = "toward"
            if stop_reason == "shutdown":
                entity.hass.is_stopping = True
            elif stop_reason == "power":
                attributes["power"] = False
            else:
                device.available = False
            entity._restore_after_power_on()
            device.set_person_airflow_mode.assert_not_called()

    @staticmethod
    async def test_user_change_cancels_restore_and_invalid_mode_never_sends() -> None:
        """Cancel the old timer on selection and reject invalid modes."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "toward"
        entity._schedule_restore()
        handle = cast("Mock", entity._restore_handle)
        entity.select_option("off")
        handle.cancel.assert_called_once_with()
        device.set_person_airflow_mode.assert_called_once_with("off")
        assert entity._restore_handle is None
        with pytest.raises(ValueError, match="Unsupported person-airflow mode"):
            entity.select_option("sideways")
        assert device.set_person_airflow_mode.call_count == 1

    @staticmethod
    async def test_send_failure_does_not_start_a_success_settle_window() -> None:
        """Preserve failure without starting a successful write window."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        device.set_person_airflow_mode.side_effect = OSError("offline send failed")
        with pytest.raises(OSError, match="offline send failed"):
            entity.select_option("toward")
        assert entity._pending_until == pytest.approx(0.0, rel=0.0, abs=0.0)
        assert entity._restore_handle is None
        assert entity._manual_pending_generation is None

    @staticmethod
    async def test_queued_executor_restore_cannot_send_after_unload() -> None:
        """Cancellation may leave an executor callable queued; its token rejects it."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "toward"
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        entity._schedule_restore()
        entity._restore_after_power_on(entity._restore_generation)
        await entered.wait()
        assert len(queued) == 1
        device.set_person_airflow_mode.assert_not_called()
        with patch.object(MideaSelect, "async_will_remove_from_hass", new=AsyncMock()):
            await entity.async_will_remove_from_hass()
        function, args, _future = queued[0]
        function(*args)
        await asyncio.sleep(0)
        device.set_person_airflow_mode.assert_not_called()
        assert entity._removed
        assert entity._restore_task is None

    @staticmethod
    async def test_new_schedule_invalidates_queued_restore() -> None:
        """A new timer generation supersedes the previous queued worker."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "toward"
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        entity._schedule_restore()
        old_generation = entity._restore_generation
        entity._restore_after_power_on(old_generation)
        await entered.wait()
        entity._schedule_restore()
        assert entity._restore_generation > old_generation
        function, args, _future = queued[0]
        function(*args)
        await asyncio.sleep(0)
        device.set_person_airflow_mode.assert_not_called()
        assert entity._restore_handle is not None
        entity._cancel_restore()

    @staticmethod
    async def test_worker_rechecks_power_availability_and_shutdown() -> None:
        """Queue-time eligibility does not authorize a later ineligible worker."""
        for changed in ("power", "available", "shutdown", "generation"):
            entity, device, attributes = make_select()
            attributes["power"] = True
            entity._desired_option = "toward"
            generation = entity._restore_generation
            if changed == "power":
                attributes["power"] = False
            elif changed == "available":
                device.available = False
            elif changed == "shutdown":
                entity.hass.is_stopping = True
            else:
                entity._cancel_restore()
            entity._apply_desired_option(generation)
            device.set_person_airflow_mode.assert_not_called()

    @staticmethod
    async def test_cancelled_loop_request_cannot_create_a_new_timer() -> None:
        """A stale call_soon request cannot override a subsequent user choice."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "toward"
        old_generation = entity._restore_generation
        entity.select_option("avoid")
        entity._schedule_restore(old_generation)
        entity.hass.loop.call_later.assert_not_called()
        device.set_person_airflow_mode.assert_called_once_with("avoid")

    @staticmethod
    async def test_queued_restore_keeps_preference_until_worker_and_settle() -> None:
        """Old reports cannot erase preference during an executor queue window."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True
        entity._desired_option = "toward"
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        entity._schedule_restore()
        entity._restore_after_power_on(entity._restore_generation)
        await entered.wait()
        task = entity._restore_task
        assert task is not None
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "toward"
        function, args, future = queued[0]
        function(*args)
        future.set_result(None)
        await task
        device.set_person_airflow_mode.assert_called_once_with("toward")
        assert entity.current_option == "toward"
        assert not entity._restore_requested
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "toward"
        entity._pending_until = 0.0
        attributes["wind_avoid"] = True
        entity.update_state({"wind_avoid": True})
        assert entity.current_option == "avoid"

    @staticmethod
    async def test_reports_during_synchronous_send_do_not_erase_user_choice() -> None:
        """A callback during send observes in-flight intent rather than old flags."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True

        def report_during_send(_option: str) -> None:
            """Deliver the old report while the real apply path is sending."""
            entity.update_state({"wind_straight": False, "wind_avoid": False})

        device.set_person_airflow_mode.side_effect = report_during_send
        entity.select_option("toward")
        device.set_person_airflow_mode.assert_called_once_with("toward")
        assert entity.current_option == "toward"
        assert entity._pending_until > 0
        assert not entity._sending_generations

    @staticmethod
    async def test_call_soon_restore_request_protects_preference_before_timer() -> None:
        """Reports between a power callback and loop scheduling keep the intent."""
        entity, _device, attributes = make_select()
        entity._desired_option = "toward"
        entity._last_power = False
        entity._last_available = True
        attributes["power"] = True
        entity.hass.loop.call_soon_threadsafe.side_effect = None
        entity.update_state({"power": True})
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "toward"
        assert entity._restore_requested
        entity._cancel_restore()
        assert not entity._restore_requested


class TestManualPersonAirflowRequests(IsolatedAsyncioTestCase):
    """Exercise service queue identity, cancellation and actual worker order."""

    @staticmethod
    async def test_manual_executor_queue_rechecks_lifecycle_before_send() -> None:
        """Real async service requests cannot write after unload, reload or stop."""

        async def check_lifecycle(lifecycle: str) -> None:
            """Exercise the real async entry with one independently bound queue."""
            entity, device, attributes = make_select()
            attributes["power"] = True
            queued = []
            entered = asyncio.Event()

            async def queue_executor(function: Callable[..., None], *args: int) -> None:
                future: asyncio.Future[None] = (
                    asyncio.get_running_loop().create_future()
                )
                queued.append((function, args, future))
                entered.set()
                return await future

            entity.hass.async_add_executor_job = queue_executor
            request = asyncio.create_task(entity.async_select_option("toward"))
            await entered.wait()
            if lifecycle == "stopping":
                entity.hass.is_stopping = True
            else:
                with patch.object(
                    MideaSelect,
                    "async_will_remove_from_hass",
                    new=AsyncMock(),
                ):
                    await entity.async_will_remove_from_hass()
                if lifecycle == "reload":
                    entity._removed = False
            function, args, future = queued[0]
            function(*args)
            future.set_result(None)
            await request
            device.set_person_airflow_mode.assert_not_called()

        for lifecycle in ("unload", "reload", "stopping"):
            await check_lifecycle(lifecycle)

    @staticmethod
    async def test_latest_manual_request_supersedes_an_older_executor_job() -> None:
        """A queued user request is bound before executor scheduling can reorder it."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        first = asyncio.create_task(entity.async_select_option("toward"))
        await entered.wait()
        entered.clear()
        second = asyncio.create_task(entity.async_select_option("avoid"))
        await entered.wait()
        for function, args, future in reversed(queued):
            function(*args)
            future.set_result(None)
        await asyncio.gather(first, second)
        device.set_person_airflow_mode.assert_called_once_with("avoid")

    @staticmethod
    async def test_write_order_keeps_new_choice_after_a_preempted_restore() -> None:
        """The loop stays responsive while ordered workers preserve the last choice."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._desired_option = "toward"
        loop = asyncio.get_running_loop()
        entered = asyncio.Event()
        release = threading.Event()
        writes: list[str] = []

        def record_sdk_call(option: str) -> None:
            """Pause the old SDK call without modifying the production function."""
            if option == "toward":
                loop.call_soon_threadsafe(entered.set)
                assert release.wait(5.0)
            writes.append(option)

        device.set_person_airflow_mode.side_effect = record_sdk_call
        with ThreadPoolExecutor(max_workers=2) as pool:

            async def real_executor(function: Callable[..., None], *args: int) -> None:
                await loop.run_in_executor(pool, function, *args)

            entity.hass.async_add_executor_job = real_executor
            old = loop.run_in_executor(
                pool,
                entity._apply_desired_option,
                entity._restore_generation,
            )
            try:
                await asyncio.wait_for(entered.wait(), 2.0)
                new = asyncio.create_task(entity.async_select_option("avoid"))
                await asyncio.sleep(0)
                assert entity.current_option == "avoid"
                assert not new.done()
            finally:
                release.set()
            await asyncio.wait_for(asyncio.gather(old, new), 5.0)
        assert writes == ["toward", "avoid"]
        assert entity.current_option == "avoid"

    @staticmethod
    async def test_async_manual_choice_while_powered_off_is_only_remembered() -> None:
        """The real async entry preserves an off-unit preference without a send."""
        entity, device, _attributes = make_select()
        await entity.async_select_option("avoid")
        assert entity.current_option == "avoid"
        device.set_person_airflow_mode.assert_not_called()

    @staticmethod
    async def test_manual_queue_preserves_choice_against_old_reports() -> None:
        """The real async entry protects intent before the SDK worker starts."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        request = asyncio.create_task(entity.async_select_option("toward"))
        await entered.wait()
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "toward"
        function, args, future = queued[0]
        function(*args)
        future.set_result(None)
        await request
        device.set_person_airflow_mode.assert_called_once_with("toward")
        assert entity._manual_pending_generation is None

    @staticmethod
    async def test_cancelled_manual_queue_invalidates_its_late_worker() -> None:
        """Cancelling the service task rejects its leftover executor callable."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        request = asyncio.create_task(entity.async_select_option("toward"))
        await entered.wait()
        request.cancel()
        with pytest.raises(asyncio.CancelledError):
            await request
        function, args = queued[0]
        function(*args)
        device.set_person_airflow_mode.assert_not_called()
        assert entity._manual_pending_generation is None
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "off"

    @staticmethod
    async def test_executor_failure_releases_manual_request_protection() -> None:
        """A scheduling failure cannot leave intent protected or a late job live."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True
        queued = []

        async def fail_executor(function: Callable[..., None], *args: int) -> None:
            queued.append((function, args))
            raise RuntimeError("executor unavailable")

        entity.hass.async_add_executor_job = fail_executor
        with pytest.raises(RuntimeError, match="executor unavailable"):
            await entity.async_select_option("toward")
        function, args = queued[0]
        function(*args)
        device.set_person_airflow_mode.assert_not_called()
        assert entity._manual_pending_generation is None
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "off"

    @staticmethod
    async def test_old_completion_keeps_new_queue_protected() -> None:
        """A superseded job's finally cannot expose the newer choice to reports."""
        entity, device, attributes = make_select()
        attributes["power"] = True
        entity._last_power = True
        entity._last_available = True
        queued = []
        entered = asyncio.Event()

        async def queue_executor(function: Callable[..., None], *args: int) -> None:
            future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            queued.append((function, args, future))
            entered.set()
            return await future

        entity.hass.async_add_executor_job = queue_executor
        first = asyncio.create_task(entity.async_select_option("toward"))
        await entered.wait()
        entered.clear()
        second = asyncio.create_task(entity.async_select_option("avoid"))
        await entered.wait()
        new_generation = entity._manual_pending_generation
        function, args, future = queued[0]
        function(*args)
        future.set_result(None)
        await first
        assert entity._manual_pending_generation == new_generation
        assert new_generation is not None
        entity.update_state({"wind_straight": False, "wind_avoid": False})
        assert entity.current_option == "avoid"
        function, args, future = queued[1]
        function(*args)
        future.set_result(None)
        await second
        device.set_person_airflow_mode.assert_called_once_with("avoid")
        assert entity._manual_pending_generation is None


class TestProtectedRegistryOwnership(TestCase):
    """A legacy display name cannot establish registry-record ownership."""

    @staticmethod
    def test_foreign_legacy_records_are_neither_enabled_nor_deleted() -> None:
        """Reject foreign platform, unique-id and config-entry identities."""
        for mismatch in ("platform", "unique_id", "config_entry_id"):
            device, _ = make_device()
            device.model = "OTHER"
            key = ACAttributes.swing_horizontal
            entry = SimpleNamespace(
                disabled_by=RegistryEntryDisabler.INTEGRATION,
                platform=DOMAIN,
                unique_id=f"{DOMAIN}.1_{key}",
                config_entry_id="owned_entry",
            )
            setattr(entry, mismatch, "foreign")
            legacy_name = f"switch.1_{key}"
            registry = Mock()
            registry.async_get_entity_id.return_value = None
            registry.async_get.side_effect = {legacy_name: entry}.get
            config_entry = SimpleNamespace(
                entry_id="owned_entry",
                options={CONF_SWITCHES: [key]},
            )
            with patch("midea_ac_lan.er.async_get", return_value=registry):
                midea_ac_lan._remove_unsupported_entities(
                    Mock(),
                    device,
                    config_entry=config_entry,
                    preserved_only=True,
                )
            registry.async_update_entity.assert_not_called()
            registry.async_remove.assert_not_called()
