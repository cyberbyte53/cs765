from block import Block
from typing import Dict,List

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
        """calculates the balance of the child node

        Args:
            child (TreeNode): child node:
            parent_node (TreeNode, optional):parent node . Defaults to None.
        """
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
        child.peers_balance = peers_balance
    
    def calculate_balance_for_blocks(self,blks:List[Block]) -> Dict[int,float]:
        balance:Dict[int,float] = self.peers_balance.copy()
        txns = []
        for blk in blks:
            txns.extend(blk.transactions)
        for txn in txns:
            if txn.sender_id not in balance:
                balance[txn.sender_id] = 0
            if txn.receiver_id not in balance:
                balance[txn.receiver_id] = 0
            balance[txn.sender_id] -= txn.amount
            balance[txn.receiver_id] += txn.amount
        return balance
        
        
        
    def add_child(self,child) -> bool:
        """add a child to the node if the child is valid

        Args:
            child (TreeNode): child node

        Returns:
            bool: True if the child is valid, False otherwise
        """
        TreeNode.calculate_balance(child,self)
        for peer,bal in child.peers_balance.items():
            if peer != -1 and bal < 0:
                return False
        self.children.append(child)
        child.parent = self
        return True
    
    def __str__(self) -> str:
        """str representation of the node

        Returns:
            str: str representation of the node
        """
        return f"Block {self.block.id} with prev block {self.block.prev_blk_id} and transactions:\n" + "".join([str(txn) for txn in self.block.transactions])
