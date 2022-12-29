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

# Define the format strings for each data type
TypeFormats = [
    "",  # null
    "d",  # double (float64)
    "?",  # bool
    "ddd"]  # Vector3d


class Packet:
    def __init__(self, data):
        """
              Initialize a Packet object with the given data.
              Parameters:
              - data (bytes): The raw data of the packet.
        """
        self.data = data
        self.pos = 0

    def get(self, num_bytes):
        """
               Get the next num_bytes bytes from the packet.
               Parameters:
               - num_bytes (int): The number of bytes to retrieve.
                Returns:
                - bytes: The requested bytes. If there are not enough bytes remaining in
                the packet, all remaining bytes will be returned.
        """
        self.pos += num_bytes
        return self.data[self.pos - num_bytes:self.pos]

    def read(self, fmt):
        """
        Read all formatted values from the packet.
        Parameters:
        - fmt (str): The format string to use for parsing the data.
        Returns:
        - Union[None, Any]: A single value if only one value is specified in the
          format string, or a tuple of values if multiple values are specified.
          Returns None if no values are read.
        """
        v = self.read_all(fmt)
        if len(v) == 0:
            return None
        if len(v) == 1:
            return v[0]
        return v

    def read_all(self, fmt):
        """
        Read formatted values from the packet.
        Parameters:
        - fmt (str): The format string to use for parsing the data.
        Returns:
        - Tuple[Any]: A tuple of the parsed values.
        """
        return struct.unpack(fmt, self.get(struct.calcsize(fmt)))

    @property
    def more(self):
        """
        Check if there is more data in the packet.
        Returns:
        - bool: True if there is more data, False otherwise.
        """
        return self.pos < len(self.data)


def read_packet(dat):
    """
    Parse and process a packet of data.
    Parameters:
    - dat (bytes): The raw data of the packet.
    Returns:
    - None: The function does not return a value.
    """
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
                """
                Open the file with the name 'name.txt' in append mode and write
                the value (and unit, if it has one) of the current data item to the file.
                """
                f.truncate(0)
                f.write("{0}: {1}{2}\n".format(name, val, unit))


sys.stderr.write("Starting Client...\n")
while 1:
    """
    Receive data packets from a server (up to a specified amount of bytes) and process them using the
    read_packet function.
    """
    d, a = s.recvfrom(2048)
    read_packet(d)
