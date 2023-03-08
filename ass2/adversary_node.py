from node import Node
from block import Block

class AdversaryNode(Node):
    
    def __init__(self, id: int, slow: bool, low_cpu: bool, peers: list, hashing_power: float) -> None:
        super().__init__(id, slow, low_cpu, peers, hashing_power)

    def generate_blk(self, longest_chain_blk_id: int, trigger_time: float) -> None:
        return super().generate_blk(longest_chain_blk_id, trigger_time)
    
    def receive_blk(self, blk: Block, trigger_time: float) -> None:
        return super().receive_blk(blk, trigger_time)
    