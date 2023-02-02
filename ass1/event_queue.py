from event import Event
import heapq

class EventQueue:
    
    def __init__(self):
        self.event_queue = []
        
    def add_event(self,event:Event):
        heapq.heappush(self.event_queue,event)
        
    def get_next_event(self) -> Event:
        if len(self.event_queue) == 0:
            return None
        return heapq.heappop(self.event_queue)
    
    def __str__(self) -> str:
        return "".join([str(event) for event in self.event_queue])
event_queue = EventQueue()
