from event_queue import event_queue
from network import Network
from params import *

class Handler:
    
    def __init__(self) -> None:
        self.network = Network(n,z0,z1)
    
    def run(self):
        while True:
            event = event_queue.get_next_event()
            if event is None:
                break
            ass_node = self.network.nodes[event.node]
            event.process(ass_node)

handler = Handler()
print(handler.network)
handler.run()