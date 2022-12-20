import socket, struct, sys
from datetime import timedelta

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("localhost", 2837))

TypeFormats = [
    "",     # null
    "d",    # double (float64)
    "?",    # bool
    "ddd"]  # Vector3d

class Packet:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def get(self, l):  # get l bytes
        self.pos += l
        return self.data[self.pos - l:self.pos]

    def read(self, fmt):  # read all formatted values
        v = self.readAll(fmt)
        if len(v) == 0: return None
        if len(v) == 1: return v[0]
        return v

    def readAll(self, fmt):  # read multiple formatted values
        return struct.unpack(fmt, self.get(struct.calcsize(fmt)))

    @property
    def more(self):  # is there more data?
        return self.pos < len(self.data)

def readPacket(dat):
    p = Packet(dat)

    messageType = p.read("B")

    if messageType == 1:
        timestamp = p.read("Q")
        while p.more:
            nameLen = p.read("I")
            name = p.get(nameLen).decode('utf-8')

            tp = p.read("B")
            if tp == 4:
                # Text
                textLen = p.read("I")
                val = "'{0}'".format(p.get(textLen).decode('utf-8').replace("\\", "\\\\").replace("'", "\\'"))
            else:
                structFormat = TypeFormats[tp]
                val = p.read(structFormat)

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
    readPacket(d)