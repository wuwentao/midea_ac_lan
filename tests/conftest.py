"""Home Assistant fixtures with only the external Midea device mocked."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_TYPE,
    Platform,
)
from homeassistant.core import HomeAssistant
from midealan.device import DeviceType, MideaDevice, ProtocolVersion

from custom_components.midea_ac_lan.const import (
    CONF_MAC,
    CONF_MODEL,
    CONF_SN,
    CONF_SUBTYPE,
    DOMAIN,
)

from .ha import MockConfigEntry

TEST_DEVICE_ID = 123456
TEST_MAC = "02:00:00:00:00:01"
TEST_SN = "00000000000000000000000000000000"


@pytest.fixture
def enable_integration(enable_custom_integrations: None) -> None:
    """Allow the integration loader to discover custom_components."""


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a fictional device entry at the current config schema version."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test appliance",
        unique_id=str(TEST_DEVICE_ID),
        version=2,
        minor_version=2,
        data={
            CONF_DEVICE_ID: TEST_DEVICE_ID,
            CONF_NAME: "Test appliance",
            CONF_TYPE: DeviceType.AC,
            CONF_IP_ADDRESS: "192.0.2.10",
            CONF_PORT: 6444,
            CONF_PROTOCOL: ProtocolVersion.V2,
            CONF_MODEL: "TEST-MODEL",
            CONF_SUBTYPE: 1,
            CONF_MAC: TEST_MAC,
            CONF_SN: TEST_SN,
        },
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_device() -> Mock:
    """Provide an offline device that delivers real entity update callbacks."""
    device = Mock(spec=MideaDevice)
    device.device_type = DeviceType.AC
    device.device_id = TEST_DEVICE_ID
    device.name = "Test appliance"
    device.model = "TEST-MODEL"
    device.subtype = 1
    device.mac = TEST_MAC
    device.serial_number = TEST_SN
    device.available = True
    device.attributes = {"eco_mode": False}
    callbacks: list[Callable] = []
    device.register_update.side_effect = callbacks.append
    device.unregister_update.side_effect = callbacks.remove
    device.get_attribute.side_effect = device.attributes.get

    def notify(status: dict[str, Any]) -> None:
        """Deliver a report, including any availability transition."""
        for key, value in status.items():
            if key == "available":
                device.available = value
            else:
                device.attributes[key] = value
        for callback in callbacks.copy():
            callback(status)

    def set_attribute(attr: str, value: object) -> None:
        """Mirror an acknowledged device command back as a push update."""
        notify({attr: value})

    device.set_attribute.side_effect = set_attribute
    # This test-only helper keeps callback ownership outside the integration.
    device.notify_update = notify
    return device


@pytest.fixture
def mock_device_selector(mock_device: Mock) -> Generator[Mock]:
    """Patch the device constructor, leaving HA setup intact.

    Yields
    ------
    Mock
        The constructor that returns the offline device.

    """
    with patch(
        "custom_components.midea_ac_lan.device_selector",
        return_value=mock_device,
    ) as selector:
        yield selector


@pytest.fixture
def switch_platform() -> Generator[None]:
    """Load only the platform under test, using HA's real entity platform."""
    with patch("custom_components.midea_ac_lan.ALL_PLATFORM", [Platform.SWITCH]):
        yield


async def setup_integration(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Load an entry through HA's integration and config entry managers."""
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
