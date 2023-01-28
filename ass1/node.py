class Node:
    """
    Represents a node in the network
    """ 
    
    def __init__(self,id:int,slow:bool,low_cpu:bool,peers:list) -> None:
        """Initializes a new node in the network 

        Args:
            id (int): Unique descriptor of the node
            slow (bool): relative measure of the node's network speed
            low_cpu (bool): relative measure of the node's CPU speed
            peers (list): list of peers of the node
        """
        self.id = id
        self.slow = slow
        self.low_cpu = low_cpu
        self.peers = peers
     
    def __str__(self) -> str:
        """
        prints the node's id, peers, slow and low_cpu
        Returns:
            str: string representation of the node
        """
        return f"Node {self.id} has peers {self.peers} and is slow: {self.slow} and has low cpu: {self.low_cpu}\n"