"""Exercise the optional cloud filter sensor through Home Assistant."""

from asyncio import Event
from collections.abc import Generator
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SENSORS,
    CONF_TYPE,
    STATE_UNAVAILABLE,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util.dt import utcnow
from midealan.device import DeviceType
from midealan.exceptions import CloudAuthError, CloudError

from custom_components.midea_ac_lan.const import (
    CONF_ACCOUNT,
    CONF_MODEL,
    CONF_SERVER,
    CONF_SUBTYPE,
    DEFAULT_CLOUD,
)
from tests.conftest import TEST_DEVICE_ID, setup_integration
from tests.ha import MockConfigEntry, async_fire_time_changed

pytestmark = pytest.mark.usefixtures("enable_integration", "mock_device_selector")

KEY = "filter_wash_time"
ENTITY_ID = f"sensor.{TEST_DEVICE_ID}_{KEY}"
CLOUD_OPTIONS = {CONF_ACCOUNT: "tester@example.invalid", CONF_PASSWORD: "unused"}


@pytest.fixture
def filter_appliance(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> Generator[None]:
    """Load a supported dishwasher's real sensor platform without a LAN socket."""
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_TYPE: DeviceType.E1,
            CONF_MODEL: "7600644C",
            CONF_SUBTYPE: 3,
        },
    )
    mock_device.device_type = DeviceType.E1
    mock_device.model = "7600644C"
    mock_device.subtype = 3
    mock_device.attributes["temperature"] = 27.0
    mock_device.get_estimated_consumption = Mock(return_value={})
    with (
        patch("custom_components.midea_ac_lan.ALL_PLATFORM", [Platform.SENSOR]),
        patch("custom_components.midea_ac_lan.cloud.async_get_clientsession"),
    ):
        yield


@pytest.mark.usefixtures("filter_appliance")
async def test_filter_sensor_opt_in_and_configured_cloud(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Pass the selected cloud to the library client and follow its report."""
    ready = Event()
    readings = iter([817, 0])

    async def read_cloud(_appliance_id: int) -> int:
        await ready.wait()
        return next(readings)

    client = Mock(async_get_report=AsyncMock(side_effect=read_cloud))
    with patch(
        "custom_components.midea_ac_lan.cloud.E1CloudClient",
        return_value=client,
    ) as factory:
        await setup_integration(hass, config_entry)
        assert hass.states.get(ENTITY_ID) is None
        factory.assert_not_called()

        form = await hass.config_entries.options.async_init(config_entry.entry_id)
        assert form["type"] is FlowResultType.FORM
        assert CONF_SERVER in {str(key) for key in form["data_schema"].schema}
        result = await hass.config_entries.options.async_configure(
            form["flow_id"],
            {
                CONF_SENSORS: [KEY, "temperature"],
                CONF_SERVER: "SmartHome",
                **CLOUD_OPTIONS,
            },
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_SERVER] == "SmartHome"
        await hass.async_block_till_done()

        # The LAN entity is created while the cloud request is still pending.
        temperature = hass.states.get(f"sensor.{TEST_DEVICE_ID}_temperature")
        assert temperature is not None
        assert float(temperature.state) == pytest.approx(27.0)
        assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE

        ready.set()
        await hass.async_block_till_done(wait_background_tasks=True)
        state = hass.states.get(ENTITY_ID)
        assert state is not None
        assert float(state.state) == pytest.approx(817)

        async_fire_time_changed(hass, utcnow() + timedelta(hours=1, minutes=1))
        await hass.async_block_till_done(wait_background_tasks=True)

    args = factory.call_args.args
    assert args[0] == "SmartHome"
    assert args[2] == CLOUD_OPTIONS[CONF_ACCOUNT]
    assert args[3] == CLOUD_OPTIONS[CONF_PASSWORD]
    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert float(state.state) == pytest.approx(0)
    assert [call.args[0] for call in client.async_get_report.await_args_list] == [
        int(TEST_DEVICE_ID),
        int(TEST_DEVICE_ID),
    ]
    mock_device.set_attribute.assert_not_called()


@pytest.mark.usefixtures("filter_appliance")
async def test_filter_sensor_defaults_to_the_default_cloud(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Fall back to DEFAULT_CLOUD when no server is stored in the options."""
    client = Mock(async_get_report=AsyncMock(return_value=12))
    with patch(
        "custom_components.midea_ac_lan.cloud.E1CloudClient",
        return_value=client,
    ) as factory:
        hass.config_entries.async_update_entry(
            config_entry,
            options={CONF_SENSORS: [KEY], **CLOUD_OPTIONS},
        )
        await setup_integration(hass, config_entry)
        await hass.async_block_till_done(wait_background_tasks=True)

    assert factory.call_args.args[0] == DEFAULT_CLOUD
    assert client.async_get_report.await_args.args == (int(TEST_DEVICE_ID),)
    assert float(hass.states.get(ENTITY_ID).state) == pytest.approx(12)


@pytest.mark.parametrize(
    "failure",
    ["unconfigured", "unsupported_cloud", "denied", "offline", "missing"],
)
@pytest.mark.usefixtures("filter_appliance")
async def test_filter_sensor_never_reports_zero_for_missing_cloud_data(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    failure: str,
) -> None:
    """Keep local sensors working when cloud data or credentials are missing."""
    options: dict = {CONF_SENSORS: [KEY, "temperature"]}
    if failure != "unconfigured":
        options.update(CLOUD_OPTIONS)
    hass.config_entries.async_update_entry(config_entry, options=options)

    client = Mock()
    client.async_get_report = AsyncMock(
        side_effect={
            "denied": CloudAuthError("access denied"),
            "offline": CloudError("service offline"),
        }.get(failure),
        return_value=None,
    )
    factory_error = (
        CloudError("Cloud does not support E1 reports")
        if failure == "unsupported_cloud"
        else None
    )
    with patch(
        "custom_components.midea_ac_lan.cloud.E1CloudClient",
        return_value=client,
        side_effect=factory_error,
    ) as factory:
        await setup_integration(hass, config_entry)
        await hass.async_block_till_done(wait_background_tasks=True)

    state = hass.states.get(ENTITY_ID)
    if failure == "unconfigured":
        assert state is None
        factory.assert_not_called()
    elif failure == "unsupported_cloud":
        assert state is None
    else:
        assert state is not None
        assert state.state == STATE_UNAVAILABLE
    temperature = hass.states.get(f"sensor.{TEST_DEVICE_ID}_temperature")
    assert temperature is not None
    assert float(temperature.state) == pytest.approx(27.0)
