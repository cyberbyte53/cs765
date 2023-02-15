from params import *
class Event:
    """represents an event in the simulation
    """
    event_dict = {GENERATE_TXN:"Generate Txn",RECEIVE_TXN:"Receive Txn",GENERATE_BLK:"Generate Blk",RECEIVE_BLK:"Receive Blk"}
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
    
    def __lt__(self,other)->bool:
        """overloads the < operator

        Args:
            other (Event): event to be compared with

        Returns:
            bool: True if self is less than other, False otherwise
        """
        return self.trigger_time < other.trigger_time
    
    def __str__(self) -> str:
        """string representation of the event

        Returns:
            str: string representation of the event
        """
        return f"Event {Event.event_dict[self.event_type]} at {self.trigger_time} for node {self.node}\n"
    
    