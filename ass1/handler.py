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
    
    def run(self):
        """function to run the simulation
        """
        while True:
            event = event_queue.get_next_event()
            print(event)
            
            if event is None:
                break
            self.network.process_event(event)

handler = Handler()
handler.run()