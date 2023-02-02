from transaction import Transaction
class Packet:
    def __init__(self, source, destination, data: Transaction):
        self.source = source
        self.destination = destination
        self.data = data

    def __str__(self):
        return "Packet from {} to {} with data {}".format(
            self.source, self.destination, self.data
        )