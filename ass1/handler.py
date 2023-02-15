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
        i = 10000000
        while i>0:
            i-=1
            event = event_queue.get_next_event()
            if event is None:
                break
            self.network.process_event(event)
            # print(event)
        # self.network.nodes[0].block_tree.draw_tree()
        for event in event_queue.event_queue:
            if event.event_type == GENERATE_BLK:
                print("yay")
        print("done")
                

handler = Handler()
handler.run()