import threading
try:
    from enum import StrEnum
except ImportError:
    from ..backports.enum import StrEnum
from enum import IntEnum
from .security import LocalSecurity, MSGTYPE_HANDSHAKE_REQUEST, MSGTYPE_ENCRYPTED_REQUEST
from .packet_builder import PacketBuilder
from .message import (
    MessageType,
    MessageQuestCustom,
    MessageQueryAppliance,
    MessageApplianceResponse
)
import socket
import logging
import time

_LOGGER = logging.getLogger(__name__)


class AuthException(Exception):
    pass


class ResponseException(Exception):
    pass


class RefreshFailed(Exception):
    pass


class DeviceAttributes(StrEnum):
    pass


class ParseMessageResult(IntEnum):
    SUCCESS = 0
    PADDING = 1
    ERROR = 99


class MideaDevice(threading.Thread):
    def __init__(self,
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
                 attributes: dict):
        threading.Thread.__init__(self)
        self._attributes = attributes if attributes else {}
        self._socket = None
        self._ip_address = ip_address
        self._port = port
        self._security = LocalSecurity()
        self._token = bytes.fromhex(token) if token else None
        self._key = bytes.fromhex(key) if key else None
        self._buffer = b""
        self._device_name = name
        self._device_id = device_id
        self._device_type = device_type
        self._protocol = protocol
        self._model = model
        self._subtype = subtype
        self._protocol_version = 0
        self._updates = []
        self._unsupported_protocol = []
        self._is_run = False
        self._available = True
        self._appliance_query = True
        self._refresh_interval = 30
        self._heartbeat_interval = 10
        self._default_refresh_interval = 30

    @property
    def name(self):
        return self._device_name

    @property
    def available(self):
        return self._available

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_type(self):
        return self._device_type

    @property
    def model(self):
        return self._model

    @property
    def subtype(self):
        return self._subtype

    @staticmethod
    def fetch_v2_message(msg):
        result = []
        while len(msg) > 0:
            factual_msg_len = len(msg)
            if factual_msg_len < 6:
                break
            alleged_msg_len = msg[4] + (msg[5] << 8)
            if factual_msg_len >= alleged_msg_len:
                result.append(msg[:alleged_msg_len])
                msg = msg[alleged_msg_len:]
            else:
                break
        return result, msg

    def connect(self, refresh_status=True):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10)
            _LOGGER.debug(f"[{self._device_id}] Connecting to {self._ip_address}:{self._port}")
            self._socket.connect((self._ip_address, self._port))
            _LOGGER.debug(f"[{self._device_id}] Connected")
            if self._protocol == 3:
                self.authenticate()
            _LOGGER.debug(f"[{self._device_id}] Authentication success")
            if refresh_status:
                self.refresh_status(wait_response=True)
            self.enable_device(True)
            return True
        except socket.timeout:
            _LOGGER.debug(f"[{self._device_id}] Connection timed out")
        except socket.error:
            _LOGGER.debug(f"[{self._device_id}] Connection error")
        except AuthException:
            _LOGGER.debug(f"[{self._device_id}] Authentication failed")
        except ResponseException:
            _LOGGER.debug(f"[{self._device_id}] Unexpected response received")
        except RefreshFailed:
            _LOGGER.debug(f"[{self._device_id}] Refresh status is timed out")
        except Exception as e:
            _LOGGER.error(f"[{self._device_id}] Unknown error: {e.__traceback__.tb_frame.f_globals['__file__']}, "
                          f"{e.__traceback__.tb_lineno}, {repr(e)}")
        self.enable_device(False)
        return False

    def authenticate(self):
        request = self._security.encode_8370(
            self._token, MSGTYPE_HANDSHAKE_REQUEST)
        _LOGGER.debug(f"[{self._device_id}] Handshaking")
        self._socket.send(request)
        response = self._socket.recv(512)
        if len(response) < 20:
            raise AuthException()
        response = response[8: 72]
        self._security.tcp_key(response, self._key)

    def send_message(self, data):
        if self._protocol == 3:
            self.send_message_v3(data, msg_type=MSGTYPE_ENCRYPTED_REQUEST)
        else:
            self.send_message_v2(data)

    def send_message_v2(self, data):
        if self._socket is not None:
            self._socket.send(data)
        else:
            _LOGGER.debug(f"[{self._device_id}] Send failure, device disconnected, data: {data.hex()}")

    def send_message_v3(self, data, msg_type=MSGTYPE_ENCRYPTED_REQUEST):
        data = self._security.encode_8370(data, msg_type)
        self.send_message_v2(data)

    def build_send(self, cmd):
        data = cmd.serialize()
        _LOGGER.debug(f"[{self._device_id}] Sending: {cmd}")
        msg = PacketBuilder(self._device_id, data).finalize()
        self.send_message(msg)

    def refresh_status(self, wait_response=False):
        cmds: list = self.build_query()
        if self._appliance_query:
            cmds = [MessageQueryAppliance(self.device_type)] + cmds
        error_count = 0
        for cmd in cmds:
            if cmd.__class__.__name__ not in self._unsupported_protocol:
                self.build_send(cmd)
                if wait_response:
                    try:
                        while True:
                            msg = self._socket.recv(512)
                            if len(msg) == 0:
                                raise socket.error
                            result = self.parse_message(msg)
                            if result == ParseMessageResult.SUCCESS:
                                break
                            elif result == ParseMessageResult.PADDING:
                                continue
                            else:
                                raise ResponseException
                    except socket.timeout:
                        error_count += 1
                        self._unsupported_protocol.append(cmd.__class__.__name__)
                        _LOGGER.debug(f"[{self._device_id}] Does not supports "
                                      f"the protocol {cmd.__class__.__name__}, ignored")
                    except ResponseException:
                        error_count += 1
            else:
                error_count += 1
        if error_count == len(cmds):
            raise RefreshFailed

    def pre_process_message(self, msg):
        if msg[9] == MessageType.query_appliance:
            message = MessageApplianceResponse(msg)
            self._appliance_query = False
            _LOGGER.debug(f"[{self.device_id}] Received: {message}")
            self._protocol_version = message.protocol_version
            _LOGGER.debug(f"[{self._device_id}] Device protocol version: {self._protocol_version}")
            return False
        return True

    def parse_message(self, msg):
        if self._protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + msg)
        else:
            messages, self._buffer = self.fetch_v2_message(self._buffer + msg)
        if len(messages) == 0:
            return ParseMessageResult.PADDING
        for message in messages:
            if message == b"ERROR":
                return ParseMessageResult.ERROR
            payload_len = message[4] + (message[5] << 8) - 56
            payload_type = message[2] + (message[3] << 8)
            if payload_type in [0x1001, 0x0001]:
                # Heartbeat detected
                pass
            elif len(message) > 56:
                cryptographic = message[40:-16]
                if payload_len % 16 == 0:
                    decrypted = self._security.aes_decrypt(cryptographic)
                    try:
                        cont = True
                        if self._appliance_query:
                            cont = self.pre_process_message(decrypted)
                        if cont:
                            status = self.process_message(decrypted)
                            if len(status) > 0:
                                self.update_all(status)
                            else:
                                _LOGGER.debug(f"[{self._device_id}] Unidentified protocol")
                    except Exception as e:
                        _LOGGER.error(f"[{self._device_id}] Error in process message, msg = {decrypted.hex()}")
                else:
                    _LOGGER.warning(
                        f"[{self._device_id}] Illegal payload, "
                        f"original message = {msg.hex()}, buffer = {self._buffer.hex()}, "
                        f"8370 decoded = {message.hex()}, payload type = {payload_type}, "
                        f"alleged payload length = {payload_len}, factual payload length = {len(cryptographic)}"
                    )
            else:
                _LOGGER.warning(
                    f"[{self._device_id}] Illegal message, "
                    f"original message = {msg.hex()}, buffer = {self._buffer.hex()}, "
                    f"8370 decoded = {message.hex()}, payload type = {payload_type}, "
                    f"alleged payload length = {payload_len}, message length = {len(message)}, "
                )
        return ParseMessageResult.SUCCESS

    def build_query(self):
        raise NotImplementedError

    def process_message(self, msg):
        raise NotImplementedError

    def send_command(self, cmd_type, cmd_body: bytearray):
        cmd = MessageQuestCustom(self._device_type, self._protocol_version, cmd_type, cmd_body)
        try:
            self.build_send(cmd)
        except socket.error as e:
            _LOGGER.debug(f"[{self._device_id}] Interface send_command failure, {repr(e)}, "
                          f"cmd_type: {cmd_type}, cmd_body: {cmd_body.hex()}")

    def send_heartbeat(self):
        msg = PacketBuilder(self._device_id, bytearray([0x00])).finalize(msg_type=0)
        self.send_message(msg)

    def register_update(self, update):
        self._updates.append(update)

    def update_all(self, status):
        _LOGGER.debug(f"[{self._device_id}] Status update: {status}")
        for update in self._updates:
            update(status)

    def enable_device(self, available=True):
        self._available = available
        status = {"available": available}
        self.update_all(status)

    def open(self):
        if not self._is_run:
            self._is_run = True
            threading.Thread.start(self)

    def close(self):
        if self._is_run:
            self._is_run = False
            self.close_socket()

    def close_socket(self):
        self._unsupported_protocol = []
        self._buffer = b""
        if self._socket:
            self._socket.close()
            self._socket = None

    def set_ip_address(self, ip_address):
        if self._ip_address != ip_address:
            _LOGGER.debug(f"[{self._device_id}] Update IP address to {ip_address}")
            self._ip_address = ip_address
            self.close_socket()

    def set_refresh_interval(self, refresh_interval):
        self._refresh_interval = refresh_interval

    def run(self):
        while self._is_run:
            while self._socket is None:
                if self.connect(refresh_status=True) is False:
                    if not self._is_run:
                        return
                    self.close_socket()
                    time.sleep(5)
            timeout_counter = 0
            start = time.time()
            previous_refresh = start
            previous_heartbeat = start
            self._socket.settimeout(1)
            while True:
                try:
                    now = time.time()
                    if 0 < self._refresh_interval <= now - previous_refresh:
                        self.refresh_status()
                        previous_refresh = now
                    if now - previous_heartbeat >= self._heartbeat_interval:
                        self.send_heartbeat()
                        previous_heartbeat = now
                    msg = self._socket.recv(512)
                    msg_len = len(msg)
                    if msg_len == 0:
                        raise socket.error("Connection closed by peer")
                    result = self.parse_message(msg)
                    if result == ParseMessageResult.ERROR:
                        _LOGGER.debug(f"[{self._device_id}] Message 'ERROR' received")
                        self.close_socket()
                        break
                    elif result == ParseMessageResult.SUCCESS:
                        timeout_counter = 0
                except socket.timeout:
                    timeout_counter = timeout_counter + 1
                    if timeout_counter >= 120:
                        _LOGGER.debug(f"[{self._device_id}] Heartbeat timed out")
                        self.close_socket()
                        break
                except socket.error as e:
                    if self._is_run:
                        _LOGGER.debug(f"[{self._device_id}] Socket error {repr(e)}")
                        self.close_socket()
                    break
                except Exception as e:
                    _LOGGER.error(f"[{self._device_id}] Unknown error :{e.__traceback__.tb_frame.f_globals['__file__']}, "
                                  f"{e.__traceback__.tb_lineno}, {repr(e)}")
                    self.close_socket()
                    break

    def set_attribute(self, attr, value):
        raise NotImplementedError

    def get_attribute(self, attr):
        return self._attributes.get(attr)

    def set_customize(self, customize):
        pass

    @property
    def attributes(self):
        ret = {}
        for status in self._attributes.keys():
            ret[str(status)] = self._attributes[status]
        return ret
