from event import Event
import heapq

class EventQueue:
    """event queue for the simulation
    """
    def __init__(self)->None:
        """initializes the event queue
        """
        self.event_queue = []
        
    def add_event(self,event:Event)->None:
        """adds an event to the event queue

        Args:
            event (Event): event to be added
        """
        heapq.heappush(self.event_queue,event)
        
    def get_next_event(self) -> Event:
        """gets the next event from the event queue

        Returns:
            Event: most imminent event
        """
        if len(self.event_queue) == 0:
            return None
        return heapq.heappop(self.event_queue)
    
    def __str__(self) -> str:
        """string representation of the event queue

        Returns:
            str: string representation of the event queue
        """
        return "".join([str(event) for event in self.event_queue])
    
event_queue = EventQueue()
