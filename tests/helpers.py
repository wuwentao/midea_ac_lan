"""Shared helpers for isolated entity unit tests."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Protocol
from unittest.mock import Mock

import pytest
from homeassistant.const import CONF_DEVICE_ID

from custom_components.midea_ac_lan.const import DEVICES, DOMAIN
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TEST_DEVICE_TYPE = 0xFFFF
INTEGRATION_ROOT = Path(__file__).parent.parent / "custom_components" / "midea_ac_lan"


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


def load_integration_module(module_name: str, alias: str) -> ModuleType:
    """Load an integration module under a temporary package-qualified name.

    Raises:
        ImportError: If Python cannot create a loader for the module path.

    """
    qualified_name = f"custom_components.midea_ac_lan._test_{alias}"
    spec = importlib.util.spec_from_file_location(
        qualified_name,
        INTEGRATION_ROOT / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        msg = f"Unable to load integration module: {module_name}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(qualified_name, None)
    return module
