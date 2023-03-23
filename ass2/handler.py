from event_queue import event_queue
from network import Network
from params import *
from block import Block
class Handler:
    """initializes a network and runs the simulation
    """
    def __init__(self) -> None:
        """initializes a network
        """
        self.network = Network(n,z0,z1)
        self.blk_count = BLK_THRESHOLD
    def run(self):
        """function to run the simulation
        """
        while Block.available_id < self.blk_count:
            event = event_queue.get_next_event()
            if event is None:
                break
            self.network.process_event(event)
        while True:
            event = event_queue.get_next_event()
            if event.event_type == GENERATE_BLK:
                break
            self.network.process_event(event)
            
        self.analyze()
    def analyze(self):
        """function to analyze the simulation
        """
        self.network.analyze()
        
                

handler = Handler()
handler.run()