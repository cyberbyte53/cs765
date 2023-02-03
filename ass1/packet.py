from transaction import Transaction
class Packet:
    """Represents a packet in the network
    """
    def __init__(self, source:int, destination:int, data:Transaction):
        """Initializes a new packet in the network

        Args:
            source (int): id of the sender node
            destination (int): id of the receiver node
            data (Transaction): content of the packet
        """
        self.source = source
        self.destination = destination
        self.data = data
        

    def __str__(self):
        return "Packet from {} to {} with data {}".format(
            self.source, self.destination, self.data
        )