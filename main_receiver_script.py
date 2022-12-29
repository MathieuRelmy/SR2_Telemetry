import socket
import struct
import sys
from datetime import timedelta

# Create a socket using the UDP protocol
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to an IP on a specified port number
s.bind(("localhost", 2837))

print("Do you want units appended to the values of the variables? (y/n)")
unit_choice = input()
print("Do you want the name of the variable included in front of the value? (y/n)")
name_choice = input()


# Define the format strings for each data type
TypeFormats = [
    "",  # null
    "d",  # double (float64)
    "?",  # bool
    "ddd"]  # Vector3d


class Packet:
    def __init__(self, data):

        self.data = data
        self.pos = 0

    def get(self, num_bytes):

        self.pos += num_bytes
        return self.data[self.pos - num_bytes:self.pos]

    def read(self, fmt):

        v = self.read_all(fmt)
        if len(v) == 0:
            return None
        if len(v) == 1:
            return v[0]
        return v

    def read_all(self, fmt):

        return struct.unpack(fmt, self.get(struct.calcsize(fmt)))

    @property
    def more(self):

        return self.pos < len(self.data)


def read_packet(dat):

    p = Packet(dat)

    message_type = p.read("B")

    print("---")
    if message_type == 1:
        print("packet:")
        timestamp = p.read("Q")
        print("  timestamp: {0}".format(timedelta(milliseconds=timestamp)))
        print("  variables:")

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
                print("    {0}: {1}".format(name, val))

            # Set the unit to an empty string
            unit = ""

            # Set the unit based on the user's choice
            if unit_choice == 'y':
                if name == "Altitude":
                    unit = " M"
                elif name == "Speed":
                    unit = " M/S"
                elif name == "Heading":
                    unit = " DEG"
            else:
                unit = ""

            with open(name + ".txt", "a") as f:
                if name_choice == 'y':
                    f.write("{0}: {1}{2}\n".format(name, val, unit))
                    f.truncate(0)
                else:
                    f.write("{0}{1}\n".format(val, unit))
                    f.truncate(0)


sys.stderr.write("Starting Client...\n")
while 1:

    d, a = s.recvfrom(2048)
    read_packet(d)
