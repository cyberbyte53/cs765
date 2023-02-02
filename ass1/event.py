# from node import Node
class Event:
    """represents an event in the simulation
    """
    
    event_dict = {0:"Generate Txn",1:"Send Txn",2:"Receive Txn",3:"Generate Blk",4:"Send Blk",5:"Receive Blk"}
    def __init__(self,trigger_time:float,event_type:int, node:int,object=None) -> None:
        """initializes an event

        Args:
            trigger_time (float): time at which the event is triggered
            event_type (int): type of event
            node (int): node on which the event is triggered
            object (_type_, optional): object associated with the event. Defaults to None.
        """
        self.trigger_time = trigger_time
        self.event_type = event_type 
        self.node = node
        self.object = object
    
    def __lt__(self,other):
        return self.trigger_time < other.trigger_time
    
    def __str__(self) -> str:
        return f"Event {Event.event_dict[self.event_type]} at {self.trigger_time} for node {self.node}\n"
    
    def process(self,node)->None:
        if self.event_type == 0:
           node.generate_txn()
        elif self.event_type == 1:
            node.send_txn(self.object)
        elif self.event_type == 2:
            node.receive_txn(self.object,self.trigger_time)
    