"""
discover.py
"""
import logging
import socket
from ipaddress import IPv4Network

import ifaddr

from .security import LocalSecurity

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)

BROADCAST_MSG = bytearray(
    [
        0x5A,
        0x5A,
        0x01,
        0x11,
        0x48,
        0x00,
        0x92,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x7F,
        0x75,
        0xBD,
        0x6B,
        0x3E,
        0x4F,
        0x8B,
        0x76,
        0x2E,
        0x84,
        0x9C,
        0x6E,
        0x57,
        0x8D,
        0x65,
        0x90,
        0x03,
        0x6E,
        0x9D,
        0x43,
        0x42,
        0xA5,
        0x0F,
        0x1F,
        0x56,
        0x9E,
        0xB8,
        0xEC,
        0x91,
        0x8E,
        0x92,
        0xE5,
    ]
)

DEVICE_INFO_MSG = bytearray(
    [
        0x5A,
        0x5A,
        0x15,
        0x00,
        0x00,
        0x38,
        0x00,
        0x04,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x27,
        0x33,
        0x05,
        0x13,
        0x06,
        0x14,
        0x14,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x03,
        0xE8,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0xCA,
        0x8D,
        0x9B,
        0xF9,
        0xA0,
        0x30,
        0x1A,
        0xE3,
        0xB7,
        0xE4,
        0x2D,
        0x53,
        0x49,
        0x47,
        0x62,
        0xBE,
    ]
)


def discover(discover_type=None, ip_address=None):
    """
    discover
    """
    if discover_type is None:
        discover_type = []
    security = LocalSecurity()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    found_devices = {}
    if ip_address is None:
        addrs = enum_all_broadcast()
    else:
        addrs = [ip_address]
    _LOGGER.debug(f"All addresses for broadcast: {addrs}")
    for addr in addrs:
        try:
            sock.sendto(BROADCAST_MSG, (addr, 6445))
            sock.sendto(BROADCAST_MSG, (addr, 20086))
        except Exception:
            _LOGGER.warning(f"Can't access network {addr}")
    while True:
        try:
            data, addr = sock.recvfrom(512)
            ip = addr[0]
            _LOGGER.debug(f"Received response from {addr}: {data.hex()}")
            if len(data) >= 104 and (
                data[:2].hex() == "5a5a" or data[8:10].hex() == "5a5a"
            ):
                if data[:2].hex() == "5a5a":
                    protocol = 2
                elif data[:2].hex() == "8370":
                    protocol = 3
                    if data[8:10].hex() == "5a5a":
                        data = data[8:-16]
                else:
                    continue
                device_id = int.from_bytes(
                    bytearray.fromhex(data[20:26].hex()), "little"
                )
                if device_id in found_devices:
                    continue
                encrypt_data = data[40:-16]
                reply = security.aes_decrypt(encrypt_data)
                _LOGGER.debug(f"Declassified reply: {reply.hex()}")
                ssid = reply[41 : 41 + reply[40]].decode("utf-8")
                device_type = ssid.split("_")[1]
                port = bytes2port(reply[4:8])
                model = reply[17:25].decode("utf-8")
                sn = reply[8:40].decode("utf-8")
            elif data[:6].hex() == "3c3f786d6c20":
                protocol = 1
                root = ET.fromstring(data.decode(encoding="utf-8", errors="replace"))
                child = root.find("body/device")
                m = child.attrib
                port, sn, device_type = (
                    int(m["port"]),
                    m["apc_sn"],
                    str(hex(int(m["apc_type"])))[2:],
                )
                response = get_device_info(ip, int(port))
                device_id = get_id_from_response(response)
                if len(sn) == 32:
                    model = sn[9:17]
                elif len(sn) == 22:
                    model = sn[3:11]
                else:
                    model = ""
            else:
                continue
            device = {
                "device_id": device_id,
                "type": int(device_type, 16),
                "ip_address": ip,
                "port": port,
                "model": model,
                "sn": sn,
                "protocol": protocol,
            }
            if len(discover_type) == 0 or device.get("type") in discover_type:
                found_devices[device_id] = device
                _LOGGER.debug(f"Found a supported device: {device}")
            else:
                _LOGGER.debug(f"Found a unsupported device: {device}")
        except socket.timeout:
            break
        except socket.error as e:
            _LOGGER.error(f"Socket error: {repr(e)}")
    return found_devices


def get_id_from_response(response):
    """
    get_id_from_response
    """
    if response[64:-16][:6].hex() == "3c3f786d6c20":
        xml = response[64:-16]
        root = ET.fromstring(xml.decode(encoding="utf-8", errors="replace"))
        child = root.find("smartDevice")
        m = child.attrib
        return int.from_bytes(bytearray.fromhex(m["devId"]), "little")
    return 0


def bytes2port(paramArrayOfbyte):
    """
    bytes2port
    """
    if paramArrayOfbyte is None:
        return 0
    b, i = 0, 0
    while b < 4:
        if b < len(paramArrayOfbyte):
            b1 = paramArrayOfbyte[b] & 0xFF
        else:
            b1 = 0
        i |= b1 << b * 8
        b += 1
    return i


def get_device_info(device_ip, device_port: int):
    """
    get_device_info
    """
    response = bytearray(0)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(8)
            device_address = (device_ip, device_port)
            sock.connect(device_address)
            _LOGGER.debug(
                f"Sending to {device_ip}:{device_port} {DEVICE_INFO_MSG.hex()}"
            )
            sock.sendall(DEVICE_INFO_MSG)
            response = sock.recv(512)
    except socket.timeout:
        _LOGGER.warning(
            f"Connect the device {device_ip}:{device_port} timed out for 8s. "
            f"Don't care about a small amount of this. if many maybe not support."
        )
    except socket.error:
        _LOGGER.warning(f"Can't connect to Device {device_ip}:{device_port}")
    return response


def enum_all_broadcast():
    """
    enum_all_broadcast
    """
    nets = []
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            if ip.is_IPv4 and ip.network_prefix < 32:
                local_network = IPv4Network(
                    f"{ip.ip}/{ip.network_prefix}", strict=False
                )
                if (
                    local_network.is_private
                    and not local_network.is_loopback
                    and not local_network.is_link_local
                ):
                    addr = str(local_network.broadcast_address)
                    if addr not in nets:
                        nets.append(addr)
    return nets
