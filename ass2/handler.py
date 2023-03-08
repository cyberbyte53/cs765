from event_queue import event_queue
from network import Network
from params import *

class Handler:
    """initializes a network and runs the simulation
    """
    def __init__(self) -> None:
        """initializes a network
        """
        self.network = Network(n,z0,z1)
        self.iterations = ITERATIONS
    def run(self):
        """function to run the simulation
        """
        for i in range(self.iterations):
            event = event_queue.get_next_event()
            if event is None:
                break
            self.network.process_event(event)
        self.analyze()
    def analyze(self):
        """function to analyze the simulation
        """
        self.network.analyze()
        
                

handler = Handler()
handler.run()