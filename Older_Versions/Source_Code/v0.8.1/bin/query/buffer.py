import io
import struct


class SteamPacketBuffer(io.BytesIO):
    """In-memory byte buffer."""

    def __len__(self):
        return len(self.getvalue())

    def __repr__(self):
        return '<PacketBuffer: {}: {}>'.format(len(self), self.getvalue())

    def __str__(self):
        return str(self.getvalue())

    def read_byte(self):
        return struct.unpack('<B', self.read(1))[0]

    def write_byte(self, value):
        self.write(struct.pack('<B', value))

    def read_short(self):
        return struct.unpack('<h', self.read(2))[0]

    def write_short(self, value):
        self.write(struct.pack('<h', value))

    def read_float(self):
        return struct.unpack('<f', self.read(4))[0]

    def write_float(self, value):
        self.write(struct.pack('<f', value))

    def read_long(self):
        return struct.unpack('<l', self.read(4))[0]

    def write_long(self, value):
        self.write(struct.pack('<l', value))

    def read_long_long(self):
        return struct.unpack('<Q', self.read(8))[0]

    def write_long_long(self, value):
        self.write(struct.pack('<Q', value))

    def read_string(self):
        value = []
        while True:
            char = self.read(1)
            if char == b'\x00':
                break
            else:
                value.append(char)
        return ''.join(map(lambda char: chr(ord(char)), value))

    def write_string(self, value):
        self.write(bytearray('{0}\x00'.format(value), 'utf-8'))
