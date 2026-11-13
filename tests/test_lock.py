"""Tests for Midea lock entities."""

from unittest.mock import call

from homeassistant.const import Platform

from custom_components.midea_ac_lan.lock import MideaLock, async_setup_entry

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry_supports_all_enable_paths(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Add default, model-default, and explicitly selected lock entities."""
    entities = {
        "default": {"type": Platform.LOCK, "default": True},
        "model_default": {
            "type": Platform.LOCK,
            "default_subtypes": [1],
            "default_models": ["TEST-MODEL"],
        },
        "selected": {"type": Platform.LOCK},
        "not_selected": {"type": Platform.LOCK},
        "wrong_model": {
            "type": Platform.LOCK,
            "default": True,
            "models": ["OTHER"],
        },
    }
    install_config(entities)
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, switches=["selected"])

    await async_setup_entry(hass, entry, add_entities)

    added = add_entities.call_args.args[0]
    assert [entity._entity_key for entity in added] == [
        "default",
        "model_default",
        "selected",
    ]


def test_lock_commands_and_state(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Read lock state and forward lock, unlock, and open commands."""
    install_config({"child_lock": {"type": Platform.LOCK}})
    device, values = device_factory(attributes={"child_lock": True})
    entity = MideaLock(device, "child_lock")

    assert entity.is_locked
    values["child_lock"] = False
    assert not entity.is_locked
    entity.lock(code="ignored")
    entity.unlock(code="ignored")
    entity.open(code="ignored")
    assert device.set_attribute.call_args_list == [
        call(attr="child_lock", value=True),
        call(attr="child_lock", value=False),
        call(attr="child_lock", value=False),
    ]
