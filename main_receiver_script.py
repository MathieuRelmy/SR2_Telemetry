import socket
import struct
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("localhost", 2837))

TypeFormats = [
    "",  # null
    "d",  # double (float64)
    "?",  # bool
    "ddd"]  # Vector3d


class Packet:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def get(self, num_bytes):  # get num_bytes bytes
        self.pos += num_bytes
        return self.data[self.pos - num_bytes:self.pos]

    def read(self, fmt):  # read all formatted values
        v = self.read_all(fmt)
        if len(v) == 0:
            return None
        if len(v) == 1:
            return v[0]
        return v

    def read_all(self, fmt):  # read multiple formatted values
        return struct.unpack(fmt, self.get(struct.calcsize(fmt)))

    @property
    def more(self):  # is there more data?
        return self.pos < len(self.data)


def read_packet(dat):
    p = Packet(dat)

    message_type = p.read("B")

    if message_type == 1:
        while p.more:
            name_len = p.read("I")
            name = p.get(name_len).decode('utf-8')

            tp = p.read("B")
            if tp == 4:
                # Text
                text_len = p.read("I")
                val = "'{0}'".format(p.get(text_len).decode('utf-8').replace("\\", "\\\\").replace("'", "\\'"))
            else:
                struct_format = TypeFormats[tp]
                val = p.read(struct_format)

            if name == "Altitude":
                unit = " M"
            elif name == "Speed":
                unit = " M/S"
            else:
                unit = ""

            with open(name + ".txt", "a") as f:
                f.truncate(0)
                f.write("{0}: {1}{2}\n".format(name, val, unit))


sys.stderr.write("Starting Client...\n")
while 1:
    d, a = s.recvfrom(2048)
    read_packet(d)
