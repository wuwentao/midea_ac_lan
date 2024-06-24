"""Config flow for Midea LAN.

Setup current integration and add device entry via the web UI
enable by adding `config_flow: true` in `manifest.json`

`MideaLanConfigFlow`: add device entry
`MideaLanOptionsFlowHandler`: update the options of a config entry

job process:
1. run `async_step_user` when select `Add Device` from web UI
2. default auto discovery action run `async_step_discovery`
3. device available, run `async_step_auto` to show available device list in web UI
    3.1 check local device json with `_load_device_config`
        3.1.1 device exist with `_check_storage_device`,
              send json data to `async_step_manually`
        3.1.2 device NOT exist, get device data from cloud,
              send to `async_step_manually`
            - check login with `async_step_login`
4. add selected device detail with `async_step_manually`
5. run `_save_device_config` and `async_create_entry`
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_DEVICE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SENSORS,
    CONF_SWITCHES,
    CONF_TOKEN,
    CONF_TYPE,
    MAJOR_VERSION,
    MINOR_VERSION,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.json import save_json
from homeassistant.util.json import load_json
from midealocal.cloud import MideaCloud, get_midea_cloud
from midealocal.device import MideaDevice, ProtocolVersion
from midealocal.discover import discover

if TYPE_CHECKING:
    from aiohttp import ClientSession

if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 4):
    from homeassistant.config_entries import ConfigFlowResult
else:
    from homeassistant.data_entry_flow import (
        AbortFlow,
    )
    from homeassistant.data_entry_flow import (  # type: ignore[assignment]
        FlowResult as ConfigFlowResult,
    )

from .const import (
    CONF_ACCOUNT,
    CONF_KEY,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL,
    CONF_SERVER,
    CONF_SUBTYPE,
    DOMAIN,
    EXTRA_CONTROL,
    EXTRA_SENSOR,
)
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)

ADD_WAY = {
    "discovery": "Discover automatically",
    "manually": "Configure manually",
    "list": "List all appliances only",
}
PROTOCOLS = {1: "V1", 2: "V2", 3: "V3"}
STORAGE_PATH = f".storage/{DOMAIN}"

PRESET_ACCOUNT = [
    39182118275972017797890111985649342047468653967530949796945843010512,
    29406100301096535908214728322278519471982973450672552249652548883645,
    39182118275972017797890111985649342050088014265865102175083010656997,
]


class MideaLanConfigFlow(ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Define current integration setup steps.

    Use ConfigFlow handle to support config entries
    ConfigFlow will manage the creation of entries from user input, discovery
    """

    VERSION = 3
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """MideaLanConfigFlow class."""
        self.available_device: dict = {}
        self.devices: dict = {}
        self.found_device: dict[str, Any] = {}
        self.supports: dict = {}
        self.unsorted: dict[int, Any] = {}
        self.account: dict = {}
        self.cloud: MideaCloud | None = None
        self.session: ClientSession | None = None
        for device_type, device_info in MIDEA_DEVICES.items():
            self.unsorted[device_type] = device_info["name"]

        sorted_device_names = sorted(self.unsorted.items(), key=lambda x: x[1])
        for item in sorted_device_names:
            self.supports[item[0]] = item[1]

    def _save_device_config(self, data: dict[str, Any]) -> None:
        """Save device config to json file with device id."""
        storage_path = Path(self.hass.config.path(STORAGE_PATH))
        storage_path.mkdir(parents=True, exist_ok=True)
        record_file = storage_path.joinpath(f"{data[CONF_DEVICE_ID]!s}.json")
        save_json(record_file.name, data)

    def _load_device_config(self, device_id: str) -> Any:  # noqa: ANN401
        """Load device config from json file with device id."""
        record_file = self.hass.config.path(f"{STORAGE_PATH}/{device_id}.json")
        return load_json(record_file, default={})

    @staticmethod
    def _check_storage_device(device: dict, storage_device: dict) -> bool:
        """Check input device with storage_device."""
        if storage_device.get(CONF_SUBTYPE) is None:
            return False
        if device.get(CONF_PROTOCOL) == ProtocolVersion.V3 and (
            storage_device.get(CONF_TOKEN) is None
            or storage_device.get(CONF_KEY) is None
        ):
            return False
        return True

    def _already_configured(self, device_id: str, ip_address: str) -> bool:
        """Check device from json with device_id or ip address."""
        for entry in self._async_current_entries():
            if device_id == entry.data.get(
                CONF_DEVICE_ID,
            ) or ip_address == entry.data.get(CONF_IP_ADDRESS):
                return True
        return False

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """Define config flow steps.

        Using `async_step_<step_id>` and `async_step_user` will be the first step,
        then select discovery mode
        """
        # user select a device discovery mode
        if user_input is not None:
            # default is auto discovery mode
            if user_input["action"] == "discovery":
                return await self.async_step_discovery()
            # manual input device detail
            if user_input["action"] == "manually":
                self.found_device = {}
                return await self.async_step_manually()
            # only list all devices
            return await self.async_step_list()
        # user not input, show device discovery select form in UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("action", default="discovery"): vol.In(ADD_WAY)},
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_login(
        self,
        user_input: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """User login steps."""
        # login data exist
        cloud_servers = await MideaCloud.get_cloud_servers()
        if user_input is not None:
            cloud_server = cloud_servers[user_input[CONF_SERVER]]
            if self.session is None:
                self.session = async_create_clientsession(self.hass)
            if self.cloud is None:
                self.cloud = get_midea_cloud(
                    session=self.session,
                    cloud_name=cloud_server,
                    account=user_input[CONF_ACCOUNT],
                    password=user_input[CONF_PASSWORD],
                )
                if self.cloud is None:
                    # fmt: off
                    raise AbortFlow(
                        f"Can not get midea cloud: {cloud_server}",
                    )
                    # fmt: on
            if await self.cloud.login():
                self.account = {
                    CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_SERVER: cloud_server,
                }
                return await self.async_step_auto()
            return await self.async_step_login(error="login_failed")
        # user not login, show login form in UI
        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCOUNT): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_SERVER, default=1): vol.In(cloud_servers),
                },
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_list(
        self,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """List all devices and show device info in web UI."""
        # get all devices list
        all_devices = discover()
        # available devices exist
        if len(all_devices) > 0:
            table = (
                "Appliance code|Type|IP address|SN|Supported\n:--:|:--:|:--:|:--:|:--:"
            )
            green = "<font color=gree>YES</font>"
            red = "<font color=red>NO</font>"
            for device_id, device in all_devices.items():
                supported = device.get(CONF_TYPE) in self.supports
                table += (
                    f"\n{device_id}|{f'{device.get(CONF_TYPE):02X}'}|"
                    f"{device.get(CONF_IP_ADDRESS)}|"
                    f"{device.get('sn')}|"
                    f"{green if supported else red}"
                )
        # no available device
        else:
            table = "Not found"
        # show devices list result in UI
        return self.async_show_form(
            step_id="list",
            description_placeholders={"table": table},
            errors={"base": error} if error else None,
        )

    async def async_step_discovery(
        self,
        discovery_info: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """Discovery device with auto mode or ip address."""
        # input is not None, using ip_address to discovery device
        if discovery_info is not None:
            # auto mode, ip_address is None
            if discovery_info[CONF_IP_ADDRESS].lower() == "auto":
                ip_address = None
            # ip exist
            else:
                ip_address = discovery_info[CONF_IP_ADDRESS]
            # use midea-local discover() to get devices list with ip_address
            self.devices = discover(list(self.supports.keys()), ip_address=ip_address)
            self.available_device = {}
            for device_id, device in self.devices.items():
                # remove exist devices and only return new devices
                if not self._already_configured(
                    str(device_id),
                    device[CONF_IP_ADDRESS],
                ):
                    # fmt: off
                    self.available_device[device_id] = (
                        f"{device_id} ({self.supports.get(device.get(CONF_TYPE))})"
                    )
                    # fmt: on
            if len(self.available_device) > 0:
                return await self.async_step_auto()
            return await self.async_step_discovery(error="no_devices")
        # show discovery device input form with auto or ip address in web UI
        return self.async_show_form(
            step_id="discovery",
            data_schema=vol.Schema(
                {vol.Required(CONF_IP_ADDRESS, default="auto"): str},
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_auto(
        self,
        user_input: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """Discovery device detail info."""
        # discovery device
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device = self.devices[device_id]
            storage_device = self._load_device_config(device_id)
            # device already exist, load from json
            if self._check_storage_device(device, storage_device):
                self.found_device = {
                    CONF_DEVICE_ID: device_id,
                    CONF_TYPE: device.get(CONF_TYPE),
                    CONF_PROTOCOL: device.get(CONF_PROTOCOL),
                    CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
                    CONF_PORT: device.get(CONF_PORT),
                    CONF_MODEL: device.get(CONF_MODEL),
                    CONF_NAME: storage_device.get(CONF_NAME),
                    CONF_SUBTYPE: storage_device.get(CONF_SUBTYPE),
                    CONF_TOKEN: storage_device.get(CONF_TOKEN),
                    CONF_KEY: storage_device.get(CONF_KEY),
                }
                _LOGGER.debug(
                    "Loaded configuration for device %s from storage",
                    device_id,
                )
                return await self.async_step_manually()
            # device not exist, get device detail from cloud
            if CONF_ACCOUNT not in self.account:
                return await self.async_step_login()
            if self.session is None:
                self.session = async_create_clientsession(self.hass)
            if self.cloud is None:
                self.cloud = get_midea_cloud(
                    self.account[CONF_SERVER],
                    self.session,
                    self.account[CONF_ACCOUNT],
                    self.account[CONF_PASSWORD],
                )
                if self.cloud is None:
                    # fmt: off
                    raise AbortFlow(
                        f"Can not get midea cloud: {self.account[CONF_SERVER]}",
                    )
                    # fmt: on
            if not await self.cloud.login():
                return await self.async_step_login()
            self.found_device = {
                CONF_DEVICE_ID: device_id,
                CONF_TYPE: device.get(CONF_TYPE),
                CONF_PROTOCOL: device.get(CONF_PROTOCOL),
                CONF_IP_ADDRESS: device.get(CONF_IP_ADDRESS),
                CONF_PORT: device.get(CONF_PORT),
                CONF_MODEL: device.get(CONF_MODEL),
            }
            if device_info := await self.cloud.get_device_info(device_id):
                # set subtype with model_number
                self.found_device[CONF_NAME] = device_info.get("name")
                self.found_device[CONF_SUBTYPE] = device_info.get("model_number")
            # get token and key from cloud for v3 device
            if device.get(CONF_PROTOCOL) == ProtocolVersion.V3:
                if self.account[CONF_SERVER] == "美的美居":
                    _LOGGER.debug(
                        "Try to get Token and Key using preset MSmartHome account",
                    )
                    self.cloud = get_midea_cloud(
                        "MSmartHome",
                        self.session,
                        bytes.fromhex(
                            format((PRESET_ACCOUNT[0] ^ PRESET_ACCOUNT[1]), "X"),
                        ).decode("ASCII"),
                        bytes.fromhex(
                            format((PRESET_ACCOUNT[0] ^ PRESET_ACCOUNT[2]), "X"),
                        ).decode("ASCII"),
                    )
                    if self.cloud is None:
                        raise AbortFlow("Can not get midea cloud: MSmartHome")
                    if not await self.cloud.login():
                        return await self.async_step_auto(error="preset_account")
                keys = await self.cloud.get_keys(user_input[CONF_DEVICE])
                for value in keys.values():
                    dm = MideaDevice(
                        name="",
                        device_id=device_id,
                        device_type=device.get(CONF_TYPE),
                        ip_address=device.get(CONF_IP_ADDRESS),
                        port=device.get(CONF_PORT),
                        token=value["token"],
                        key=value["key"],
                        protocol=3,
                        model=device.get(CONF_MODEL),
                        subtype=0,
                        attributes={},
                    )
                    if dm.connect(refresh_status=False):
                        dm.close_socket()
                        self.found_device[CONF_TOKEN] = value["token"]
                        self.found_device[CONF_KEY] = value["key"]
                        return await self.async_step_manually()
                return await self.async_step_auto(error="connect_error")
            # v1/v2 device add without token/key
            return await self.async_step_manually()
        # show available device list in UI
        return self.async_show_form(
            step_id="auto",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE,
                        default=next(iter(self.available_device.keys())),
                    ): vol.In(self.available_device),
                },
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_manually(
        self,
        user_input: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ConfigFlowResult:
        """Add device with device detail info."""
        if user_input is not None:
            self.found_device = {
                CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                CONF_TYPE: user_input[CONF_TYPE],
                CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                CONF_PORT: user_input[CONF_PORT],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_TOKEN: user_input[CONF_TOKEN],
                CONF_KEY: user_input[CONF_KEY],
            }
            try:
                bytearray.fromhex(user_input[CONF_TOKEN])
                bytearray.fromhex(user_input[CONF_KEY])
            except ValueError:
                return await self.async_step_manually(error="invalid_token")
            if user_input[CONF_PROTOCOL] == ProtocolVersion.V3 and (
                len(user_input[CONF_TOKEN]) == 0 or len(user_input[CONF_KEY]) == 0
            ):
                return await self.async_step_manually(error="invalid_token")
            dm = MideaDevice(
                name="",
                device_id=user_input[CONF_DEVICE_ID],
                device_type=user_input[CONF_TYPE],
                ip_address=user_input[CONF_IP_ADDRESS],
                port=user_input[CONF_PORT],
                token=user_input[CONF_TOKEN],
                key=user_input[CONF_KEY],
                protocol=user_input[CONF_PROTOCOL],
                model=user_input[CONF_MODEL],
                subtype=0,
                attributes={},
            )
            if dm.connect(refresh_status=False):
                dm.close_socket()
                data = {
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                    CONF_TYPE: user_input[CONF_TYPE],
                    CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                    CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_MODEL: user_input[CONF_MODEL],
                    CONF_SUBTYPE: user_input[CONF_SUBTYPE],
                    CONF_TOKEN: user_input[CONF_TOKEN],
                    CONF_KEY: user_input[CONF_KEY],
                }
                # save device json config when adding new device
                self._save_device_config(data)
                # finish add device entry
                return self.async_create_entry(
                    title=f"{user_input[CONF_NAME]}",
                    data=data,
                )
            return await self.async_step_manually(error="config_incorrect")
        # show device detail manual add form in UI
        return self.async_show_form(
            step_id="manually",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(
                            self.found_device.get(CONF_NAME)
                            if self.found_device.get(CONF_NAME)
                            else self.supports.get(self.found_device.get(CONF_TYPE))
                        ),
                    ): str,
                    vol.Required(
                        CONF_DEVICE_ID,
                        default=self.found_device.get(CONF_DEVICE_ID),
                    ): int,
                    vol.Required(
                        CONF_TYPE,
                        default=(
                            self.found_device.get(CONF_TYPE)
                            if self.found_device.get(CONF_TYPE)
                            else 0xAC
                        ),
                    ): vol.In(self.supports),
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=self.found_device.get(CONF_IP_ADDRESS),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=(
                            self.found_device.get(CONF_PORT)
                            if self.found_device.get(CONF_PORT)
                            else 6444
                        ),
                    ): int,
                    vol.Required(
                        CONF_PROTOCOL,
                        default=(
                            self.found_device.get(CONF_PROTOCOL)
                            if self.found_device.get(CONF_PROTOCOL)
                            else 3
                        ),
                    ): vol.In(PROTOCOLS),
                    vol.Required(
                        CONF_MODEL,
                        default=(
                            self.found_device.get(CONF_MODEL)
                            if self.found_device.get(CONF_MODEL)
                            else "Unknown"
                        ),
                    ): str,
                    vol.Required(
                        CONF_SUBTYPE,
                        default=(
                            self.found_device.get(CONF_SUBTYPE)
                            if self.found_device.get(CONF_SUBTYPE)
                            else 0
                        ),
                    ): int,
                    vol.Optional(
                        CONF_TOKEN,
                        default=(
                            self.found_device.get(CONF_TOKEN)
                            if self.found_device.get(CONF_TOKEN)
                            else ""
                        ),
                    ): str,
                    vol.Optional(
                        CONF_KEY,
                        default=(
                            self.found_device.get(CONF_KEY)
                            if self.found_device.get(CONF_KEY)
                            else ""
                        ),
                    ): str,
                },
            ),
            errors={"base": error} if error else None,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow with MideaLanOptionsFlowHandler."""
        return MideaLanOptionsFlowHandler(config_entry)


class MideaLanOptionsFlowHandler(OptionsFlow):
    """define an Options Flow Handler to update the options of a config entry."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._device_type = config_entry.data.get(CONF_TYPE)
        if self._device_type is None:
            self._device_type = 0xAC
        if CONF_SENSORS in self._config_entry.options:
            for key in self._config_entry.options[CONF_SENSORS]:
                if key not in MIDEA_DEVICES[self._device_type]["entities"]:
                    self._config_entry.options[CONF_SENSORS].remove(key)
        if CONF_SWITCHES in self._config_entry.options:
            for key in self._config_entry.options[CONF_SWITCHES]:
                if key not in MIDEA_DEVICES[self._device_type]["entities"]:
                    self._config_entry.options[CONF_SWITCHES].remove(key)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if self._device_type == CONF_ACCOUNT:
            return self.async_abort(reason="account_option")
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        sensors = {}
        switches = {}
        for attribute, attribute_config in cast(
            dict,
            MIDEA_DEVICES[cast(int, self._device_type)]["entities"],
        ).items():
            attribute_name = (
                attribute if isinstance(attribute, str) else attribute.value
            )
            if attribute_config.get("type") in EXTRA_SENSOR:
                sensors[attribute_name] = attribute_config.get("name")
            elif attribute_config.get(
                "type",
            ) in EXTRA_CONTROL and not attribute_config.get("default"):
                switches[attribute_name] = attribute_config.get("name")
        ip_address = self._config_entry.options.get(CONF_IP_ADDRESS, None)
        if ip_address is None:
            ip_address = self._config_entry.data.get(CONF_IP_ADDRESS, None)
        refresh_interval = self._config_entry.options.get(CONF_REFRESH_INTERVAL, 30)
        extra_sensors = list(
            set(sensors.keys()) & set(self._config_entry.options.get(CONF_SENSORS, [])),
        )
        extra_switches = list(
            set(switches.keys())
            & set(self._config_entry.options.get(CONF_SWITCHES, [])),
        )
        customize = self._config_entry.options.get(CONF_CUSTOMIZE, "")
        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS, default=ip_address): str,
                vol.Required(CONF_REFRESH_INTERVAL, default=refresh_interval): int,
            },
        )
        if len(sensors) > 0:
            data_schema = data_schema.extend(
                {
                    vol.Required(
                        CONF_SENSORS,
                        default=extra_sensors,
                    ): cv.multi_select(sensors),
                },
            )
        if len(switches) > 0:
            data_schema = data_schema.extend(
                {
                    vol.Required(
                        CONF_SWITCHES,
                        default=extra_switches,
                    ): cv.multi_select(switches),
                },
            )
        data_schema = data_schema.extend(
            {
                vol.Optional(
                    CONF_CUSTOMIZE,
                    default=customize,
                ): str,
            },
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
