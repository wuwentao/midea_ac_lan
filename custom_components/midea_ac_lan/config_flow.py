"""
setup current integration and add device entry via the web UI
enable by adding `config_flow: true` in `manifest.json`

`MideaLanConfigFlow`: add device entry
`MideaLanOptionsFlowHandler`: update the options of a config entry

job process:
1. run `async_step_user` when select `Add Device` from web UI
2. default auto discovery action run `async_step_discovery`
3. device available, run `async_step_auto` to show available device list in web UI
    3.1 check local device json with `_load_device_config`
        3.1.1 device exist with `_check_storage_device`, send json data to `async_step_manually`
        3.1.2 device NOT exist, get device data from cloud and send to `async_step_manually`
            - check login with `async_step_login`
4. add selected device detail with `async_step_manually`
5. run `_save_device_config` and `async_create_entry`
"""

import logging
import os
import shutil
from typing import Any, cast

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
from midealocal.device import MideaDevice
from midealocal.discover import discover

if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 4):
    from homeassistant.config_entries import ConfigFlowResult
else:
    from homeassistant.data_entry_flow import FlowResult as ConfigFlowResult  # type: ignore

from .const import (
    CONF_ACCOUNT,
    CONF_KEY,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL,
    CONF_SERVER,
    CONF_SUBTYPE,
    DOMAIN,
    OLD_DOMAIN,
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
OLD_STORAGE_PATH = f".storage/{OLD_DOMAIN}"
MIGRATED = f"{STORAGE_PATH}/.migrated"

SERVERS = {
    1: "MSmartHome",
    2: "美的美居",
    3: "Midea Air",
    4: "NetHome Plus",
    5: "Ariston Clima",
}

PRESET_ACCOUNT = [
    39182118275972017797890111985649342047468653967530949796945843010512,
    29406100301096535908214728322278519471982973450672552249652548883645,
    39182118275972017797890111985649342050088014265865102175083010656997,
]


class MideaLanConfigFlow(ConfigFlow, domain=DOMAIN):
    """
    define current integration setup steps
    use ConfigFlow handle to support config entries
    ConfigFlow will manage the creation of entries from user input, discovery
    """

    available_device: dict = {}
    devices: dict = {}
    found_device: dict = {}
    supports: dict = {}
    unsorted: dict[int, Any] = {}
    account: dict = {}
    cloud: MideaCloud | None = None
    session = None
    for device_type, device_info in MIDEA_DEVICES.items():
        unsorted[device_type] = device_info["name"]

    sorted_device_names = sorted(unsorted.items(), key=lambda x: x[1])
    for item in sorted_device_names:
        supports[item[0]] = item[1]

    def _save_device_config(self, data: dict[str, Any]) -> None:
        """save device config to json file with device id"""
        os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
        record_file = self.hass.config.path(
            f"{STORAGE_PATH}/{data[CONF_DEVICE_ID]}.json",
        )
        save_json(record_file, data)

    def _load_device_config(self, device_id: str) -> Any:
        """load device config from json file with device id"""
        record_file = self.hass.config.path(f"{STORAGE_PATH}/{device_id}.json")
        json_data = load_json(record_file, default={})
        return json_data

    @staticmethod
    def _check_storage_device(device: dict, storage_device: dict) -> bool:
        """
        check input device with storage_device
        """
        if storage_device.get(CONF_SUBTYPE) is None:
            return False
        if device.get(CONF_PROTOCOL) == 3 and (
            storage_device.get(CONF_TOKEN) is None
            or storage_device.get(CONF_KEY) is None
        ):
            return False
        return True

    def _already_configured(self, device_id: str, ip_address: str) -> bool:
        """check device from json with device_id or ip address"""
        for entry in self._async_current_entries():
            if device_id == entry.data.get(
                CONF_DEVICE_ID,
            ) or ip_address == entry.data.get(CONF_IP_ADDRESS):
                return True
        return False

    def _check_old_domain(self) -> bool:
        """check midea_ac_lan domain configs"""
        # user skip, migrated flag exist
        if os.path.isfile(self.hass.config.path(MIGRATED)):
            _LOGGER.debug("user disabled migrate, return false")
            return False
        # new user with old domain data
        if os.path.exists(self.hass.config.path(OLD_STORAGE_PATH)):
            _LOGGER.debug("midea_ac_lan exist, return true")
            return True
        _LOGGER.debug("midea_ac_lan NOT exist, return false")
        return False

    async def _disable_migrate(self) -> bool:
        """disable midea_ac_lan configs migrate"""

        def write_file() -> bool:
            # user skip, migrated flag exist
            if not os.path.exists(self.hass.config.path(STORAGE_PATH)):
                os.makedirs(STORAGE_PATH)
            # write to file
            try:
                with open(MIGRATED, "w") as file:
                    file.write("true")
                    _LOGGER.debug("migrate done, return true")
                    return True
            except OSError as e:
                _LOGGER.error(f"File operation failed: {e}")
                _LOGGER.debug("disable migrate failed, return false")
                return False

        # run write_file job
        return await self.hass.async_add_executor_job(write_file)

    async def _do_migrate(self) -> bool:
        """migrate midea_ac_lan domain configs"""

        def move_configs() -> bool:
            try:
                _LOGGER.debug("Checking if old storage path exists.")
                # old domain exist
                if os.path.exists(self.hass.config.path(OLD_STORAGE_PATH)):
                    _LOGGER.debug("Old storage path exists.")
                    # new domain not exist, rename old domain to new domain
                    if not os.path.exists(self.hass.config.path(STORAGE_PATH)):
                        _LOGGER.debug(
                            "New storage path does not exist. Renaming old domain to new domain."
                        )
                        shutil.move(
                            self.hass.config.path(OLD_STORAGE_PATH),
                            self.hass.config.path(STORAGE_PATH),
                        )
                        return True
                    # new domain dir exist, move old configs to new domain dir
                    for item in os.listdir(self.hass.config.path(OLD_STORAGE_PATH)):
                        s = os.path.join(self.hass.config.path(OLD_STORAGE_PATH), item)
                        d = os.path.join(self.hass.config.path(STORAGE_PATH), item)
                        # confirm destination does not exist in new domain
                        if not os.path.exists(d):
                            _LOGGER.debug(f"Moving {s} to {d}")
                            shutil.move(s, d)
                    # remove old domain dir
                    os.rmdir(self.hass.config.path(OLD_STORAGE_PATH))
                    return True
                # old domain not exist
                _LOGGER.debug("Old storage path does not exist.")
                return False
            except Exception as e:
                _LOGGER.error(f"Error during migration: {e}")
                return False

        # run move_configs job
        return await self.hass.async_add_executor_job(move_configs)

    def _get_migrate_devices(self) -> list:
        """get migrate midea_ac_lan domain devices"""
        # old domain exist
        migrate = []
        if os.path.exists(self.hass.config.path(OLD_STORAGE_PATH)):
            # new domain dir exist, mv old configs to new domain dir
            for item in os.listdir(OLD_STORAGE_PATH):
                # read file content
                record_file = self.hass.config.path(f"{STORAGE_PATH}/item")
                json_data = load_json(record_file, default={})
                migrate.append(json_data)
        return migrate

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """
        define config flow steps, using `async_step_<step_id>`
        `async_step_user` will be the first step, then select discovery mode"""
        # user select a device discovery mode
        if user_input is not None:
            # default is auto discovery mode
            if user_input["action"] == "discovery":
                return await self.async_step_discovery()
            # manual input device detail
            elif user_input["action"] == "manually":
                self.found_device = {}
                return await self.async_step_manually()
            # migrate midea_ac_lan device
            elif user_input["action"] == "migrate":
                return await self.async_step_migrate()
            # only list all devices
            else:
                return await self.async_step_list()
        # user not input, show device discovery select form in UI
        # migrate data exist, show migrate option in WEB UI
        if self._check_old_domain():
            ADD_WAY["migrate"] = "Migrate [midea_ac_lan] configs"
            default_option = "migrate"
        else:
            default_option = "discovery"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("action", default=default_option): vol.In(ADD_WAY)},
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_login(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """user login steps"""
        # login data exist
        if user_input is not None:
            if self.session is None:
                self.session = async_create_clientsession(self.hass)
            if self.cloud is None:
                self.cloud = get_midea_cloud(
                    session=self.session,
                    cloud_name=SERVERS[user_input[CONF_SERVER]],
                    account=user_input[CONF_ACCOUNT],
                    password=user_input[CONF_PASSWORD],
                )
            if await self.cloud.login():
                self.account = {
                    CONF_ACCOUNT: user_input[CONF_ACCOUNT],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_SERVER: SERVERS[user_input[CONF_SERVER]],
                }
                return await self.async_step_auto()
            else:
                return await self.async_step_login(error="login_failed")
        # user not login, show login form in UI
        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCOUNT): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_SERVER, default=1): vol.In(SERVERS),
                },
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_migrate(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """migrate old domain device info in web UI"""

        # user select a device discovery mode
        if user_input is not None:
            # user select 'migrate'
            _LOGGER.debug(f"user_input: {user_input}")
            if user_input["action"] == "Migrate":
                _LOGGER.debug("start do migrate")
                # migrated = self._get_migrate_devices()
                result = await self._do_migrate()
                if result:
                    await self._disable_migrate()
                    # remove migrate option
                    ADD_WAY.pop("migrate", None)
                    # show migrate result in Web UI
                    return self.async_abort(reason="Migrate successfully!")
                _LOGGER.debug(f"migrate result {result}")
            elif user_input["action"] == "Disable":
                _LOGGER.debug("user select disable")
                await self._disable_migrate()
                # remove migrate option
                ADD_WAY.pop("migrate", None)
                return self.async_abort(reason="Disabled migrate successfully!")
            # no action, not use
            else:
                return self.async_abort(reason="User canceled")
        # show migrate option in web UI
        _LOGGER.debug("no input, show web form to user")
        return self.async_show_form(
            step_id="migrate",
            data_schema=vol.Schema(
                {
                    vol.Required("action", default="Migrate"): vol.In(
                        ["Migrate", "Disable"]
                    ),
                }
            ),
            description_placeholders={
                "desc": "Do you want to migrate from midea_ac_lan?",
            },
        )

    async def async_step_list(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """list all devices and show device info in web UI"""
        # get all devices list
        all_devices = discover()
        # available devices exist
        if len(all_devices) > 0:
            table = (
                "Appliance code|Type|IP address|SN|Supported\n:--:|:--:|:--:|:--:|:--:"
            )
            for device_id, device in all_devices.items():
                supported = device.get(CONF_TYPE) in self.supports.keys()
                table += (
                    f"\n{device_id}|{'%02X' % device.get(CONF_TYPE)}|"
                    f"{device.get(CONF_IP_ADDRESS)}|"
                    f"{device.get('sn')}|"
                    f"{'<font color=gree>YES</font>' if supported else '<font color=red>NO</font>'}"
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
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """discovery device with auto mode or ip address"""
        # input is not None, using ip_address to discovery device
        if user_input is not None:
            # auto mode, ip_address is None
            if user_input[CONF_IP_ADDRESS].lower() == "auto":
                ip_address = None
            # ip exist
            else:
                ip_address = user_input[CONF_IP_ADDRESS]
            # use midea-local discover() to get devices list with ip_address
            self.devices = discover(self.supports.keys(), ip_address=ip_address)
            self.available_device = {}
            for device_id, device in self.devices.items():
                # remove exist devices and only return new devices
                if not self._already_configured(device_id, device.get(CONF_IP_ADDRESS)):
                    self.available_device[
                        device_id
                    ] = f"{device_id} ({self.supports.get(
                        device.get(CONF_TYPE))})"
            if len(self.available_device) > 0:
                return await self.async_step_auto()
            else:
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
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """discovery device detail info"""
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
            else:
                if CONF_ACCOUNT not in self.account.keys():
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
                if device.get(CONF_PROTOCOL) == 3:
                    if self.account[CONF_SERVER] == "美的美居":
                        _LOGGER.debug(
                            "Try to get the Token and the Key use the preset MSmartHome account",
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
                        if not await self.cloud.login():
                            return await self.async_step_auto(error="preset_account")
                    keys = await self.cloud.get_keys(user_input[CONF_DEVICE])
                    for method, key in keys.items():
                        dm = MideaDevice(
                            name="",
                            device_id=device_id,
                            device_type=device.get(CONF_TYPE),
                            ip_address=device.get(CONF_IP_ADDRESS),
                            port=device.get(CONF_PORT),
                            token=key["token"],
                            key=key["key"],
                            protocol=3,
                            model=device.get(CONF_MODEL),
                            subtype=0,
                            attributes={},
                        )
                        if dm.connect(refresh_status=False):
                            dm.close_socket()
                            self.found_device[CONF_TOKEN] = key["token"]
                            self.found_device[CONF_KEY] = key["key"]
                            return await self.async_step_manually()
                    return await self.async_step_auto(error="connect_error")
                # v1/v2 device add without token/key
                else:
                    return await self.async_step_manually()
        # show available device list in UI
        return self.async_show_form(
            step_id="auto",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE,
                        default=list(self.available_device.keys())[0],
                    ): vol.In(self.available_device),
                },
            ),
            errors={"base": error} if error else None,
        )

    async def async_step_manually(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> ConfigFlowResult:
        """add device with device detail info"""
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
            if user_input[CONF_PROTOCOL] == 3 and (
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
            else:
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
        """Create the options flow with MideaLanOptionsFlowHandler"""
        return MideaLanOptionsFlowHandler(config_entry)


class MideaLanOptionsFlowHandler(OptionsFlow):
    """define an Options Flow Handler to update the options of a config entry"""

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
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if self._device_type == CONF_ACCOUNT:
            return self.async_abort(reason="account_option")
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        sensors = {}
        switches = {}
        for attribute, attribute_config in cast(
            dict, MIDEA_DEVICES[cast(int, self._device_type)]["entities"]
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
