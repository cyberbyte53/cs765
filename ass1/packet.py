class Packet:
    """describes a packet of data circulating in the network"""
    
    def __init__(self,source_id:int,destination_id:int,size:int,content:list) -> None:
        """initilizes a new packet

        Args:
            source_id (int): id of the node that generated the packet
            destination_id (int): id of the node that the packet is destined for
            size (int): size of the packet
            content (list): content of the packet
        """
        self.source_id = source_id
        self.destination_id = destination_id
        self.size = size
        self.content = content 
        