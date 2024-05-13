import datetime

from .security import LocalSecurity


class PacketBuilder:
    def __init__(self, device_id: int, command):
        self.command = None
        self.security = LocalSecurity()
        # aa20ac00000000000003418100ff03ff000200000000000000000000000006f274
        # Init the packet with the header data.
        self.packet = bytearray(
            [
                # 2 bytes - StaicHeader
                0x5A,
                0x5A,
                # 2 bytes - mMessageType
                0x01,
                0x11,
                # 2 bytes - PacketLenght
                0x00,
                0x00,
                # 2 bytes
                0x20,
                0x00,
                # 4 bytes - MessageId
                0x00,
                0x00,
                0x00,
                0x00,
                # 8 bytes - Date&Time
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                # 6 bytes - mDeviceID
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                # 12 bytes
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
            ]
        )
        self.packet[12:20] = self.packet_time()
        self.packet[20:28] = device_id.to_bytes(8, "little")
        self.command = command

    def finalize(self, msg_type=1):
        if msg_type != 1:
            self.packet[3] = 0x10
            self.packet[6] = 0x7B
        else:
            self.packet.extend(self.security.aes_encrypt(self.command))
        # PacketLenght
        self.packet[4:6] = (len(self.packet) + 16).to_bytes(2, "little")
        # Append a basic checksum data(16 bytes) to the packet
        self.packet.extend(self.encode32(self.packet))
        return self.packet

    def encode32(self, data: bytearray):
        return self.security.encode32_data(data)

    @staticmethod
    def checksum(data):
        return (~sum(data) + 1) & 0xFF

    @staticmethod
    def packet_time():
        t = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]
        b = bytearray()
        for i in range(0, len(t), 2):
            d = int(t[i : i + 2])
            b.insert(0, d)
        return b
