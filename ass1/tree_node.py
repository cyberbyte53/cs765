from block import Block
from typing import Dict

class TreeNode:
    """
    represents a node in the block tree
    """
    def __init__(self,block:Block,timestamp:float) -> None:
        self.block:Block = block
        self.timestamp = timestamp
        self.parent = None
        self.children = []
        self.peers_balance = {}

    def calculate_balance(child,parent_node=None) -> None:
        peers_balance:Dict[int,float] = {}
        if parent_node is not None:
            peers_balance = parent_node.peers_balance.copy()
        for txn in child.block.transactions:
            if txn.sender_id not in peers_balance:
                peers_balance[txn.sender_id] = 0
            if txn.receiver_id not in peers_balance:
                peers_balance[txn.receiver_id] = 0
            peers_balance[txn.sender_id] -= txn.amount
            peers_balance[txn.receiver_id] += txn.amount
        # print("peers_balance: ",peers_balance)
        child.peers_balance = peers_balance
            
    def add_child(self,child) -> bool:
        TreeNode.calculate_balance(child,self)
        for peer,bal in child.peers_balance.items():
            if peer != -1 and bal < 0:
                return False
        self.children.append(child)
        child.parent = self
        # print("parent child: ",self.block.id,child.block.id)
        return True
    
    def __str__(self) -> str:
        return f"Block {self.block.id} with prev block {self.block.prev_blk_id} and transactions:\n" + "".join([str(txn) for txn in self.block.transactions])
