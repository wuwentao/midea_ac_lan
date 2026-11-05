"""Shared helpers for isolated entity unit tests."""

from types import SimpleNamespace
from typing import Any, Protocol
from unittest.mock import Mock

import pytest
from homeassistant.const import CONF_DEVICE_ID

from custom_components.midea_ac_lan.const import DEVICES, DOMAIN
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TEST_DEVICE_TYPE = 0xFFFF


class DeviceFactory(Protocol):
    """Type the keyword arguments accepted by the device fixture."""

    def __call__(
        self,
        *,
        device_type: int = TEST_DEVICE_TYPE,
        attributes: dict[Any, Any] | None = None,
        model: str = "TEST-MODEL",
        subtype: int = 1,
        available: bool = True,
    ) -> tuple[Mock, dict[Any, Any]]:
        """Build a device mock."""


class InstallConfig(Protocol):
    """Type the optional device type accepted by the registry fixture."""

    def __call__(
        self,
        entities: dict[str, dict[str, Any]],
        device_type: int = TEST_DEVICE_TYPE,
    ) -> None:
        """Install a temporary registry entry."""


@pytest.fixture
def device_factory() -> DeviceFactory:
    """Build an offline device mock and its mutable attribute store."""

    def _factory(
        *,
        device_type: int = TEST_DEVICE_TYPE,
        attributes: dict[Any, Any] | None = None,
        model: str = "TEST-MODEL",
        subtype: int = 1,
        available: bool = True,
    ) -> tuple[Mock, dict[Any, Any]]:
        values = dict(attributes or {})
        device = Mock()
        device.device_type = device_type
        device.device_id = 123456
        device.name = "Test appliance"
        device.model = model
        device.subtype = subtype
        device.available = available
        device.attributes = values
        device.mac = "AABBCCDDEEFF"
        device.serial_number = "00000000000000000000000000000000"

        def get_attribute(
            attribute: object = None,
            *,
            attr: object = None,
        ) -> object:
            return values.get(attr if attr is not None else attribute)

        device.get_attribute.side_effect = get_attribute
        return device, values

    return _factory


@pytest.fixture
def install_config(monkeypatch: pytest.MonkeyPatch) -> InstallConfig:
    """Install a temporary device registry entry for one test."""

    def _install(
        entities: dict[str, dict[str, Any]],
        device_type: int = TEST_DEVICE_TYPE,
    ) -> None:
        monkeypatch.setitem(
            MIDEA_DEVICES,
            device_type,
            {"name": "Test appliance", "entities": entities},
        )

    return _install


def setup_context(
    device: Mock,
    *,
    sensors: list[str] | None = None,
    switches: list[str] | None = None,
) -> tuple[SimpleNamespace, SimpleNamespace, Mock]:
    """Return lightweight HA, config entry, and add callback mocks."""
    hass = SimpleNamespace(data={DOMAIN: {DEVICES: {device.device_id: device}}})
    entry = SimpleNamespace(
        data={CONF_DEVICE_ID: device.device_id},
        options={"sensors": sensors or [], "switches": switches or []},
    )
    return hass, entry, Mock()
