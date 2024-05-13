from importlib import import_module
from types import ModuleType

from homeassistant.core import HomeAssistant


async def async_device_selector(
    hass: HomeAssistant,
    name: str,
    device_id: int,
    device_type: int,
    ip_address: str,
    port: int,
    token: str,
    key: str,
    protocol: int,
    model: str,
    subtype: int,
    customize: str,
):
    try:

        if device_type < 0xA0:
            device_path = f".{'x%02x' % device_type}.device"
        else:
            device_path = f".{'%02x' % device_type}.device"

        modules: list[ModuleType] = []

        def _load_device_module() -> None:
            """Load all service modules."""
            modules.append(import_module(device_path, __package__))

        await hass.async_add_import_executor_job(_load_device_module)

        device = modules[0].MideaAppliance(
            name=name,
            device_id=device_id,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            customize=customize,
        )
    except ModuleNotFoundError:
        device = None
    return device
