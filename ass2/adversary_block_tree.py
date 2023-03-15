from block import Block
from tree_node import TreeNode
from transaction import Transaction
from typing import Dict,List
from params import *
from block_tree import BlockTree

class AdversaryBlockTree(BlockTree):
    def __init__(self):
        super().__init__()
        self.forked_blk:TreeNode = self.root
       
    def max_len_chain(node:TreeNode):
        if len(node.children) == 0:
            return 0
        max_len = -1
        for child in node.children:
            max_len = max(max_len,1 + AdversaryBlockTree.max_len_chain(child))
        return max_len
        
    def len_private_chain(self):
        for node in self.forked_blk.children:
            if node.block.mined_by == 0:
                return AdversaryBlockTree.max_len_chain(node) + 1
        return 0
    
    def len_public_chain(self):
        max_len = 0
        for node in self.forked_blk.children:
            if node.block.mined_by != 0:
                max_len = max(max_len, AdversaryBlockTree.max_len_chain(node)+1)
        return max_len
    
    def update_forked_node(self):
        treenode = self.longest_chain_node()[0]
        self.forked_blk = treenode
    # def add_blk(self,block:Block) -> bool:
    #     return super().add_blk(block)
    
    # def gen_blk(self) -> Block:
    #     return super().gen_blk()
    
    