from block import Block
from tree_node import TreeNode
from transaction import Transaction
from typing import Dict,List
from params import *
import random
import treelib
from graphviz import Source
class BlockTree:
    """
    represents the block tree
    """
    genesis_block = None
    
    def __init__(self) -> None:
        self.root:TreeNode = TreeNode(BlockTree.genesis_block,0)
        TreeNode.calculate_balance(self.root)
        self.seen_txns:set[Transaction] = set()
        self.seen_blks:set[Block] = set()
        self.last_max_depth = -1
        self.last_blk_longest_chain_id = 0
        self.blk_cache:dict[int,List[Block]] = {}
        
    def draw_tree(self):
        def add_node(node:TreeNode):
            tree.create_node(node.block.id,node.block.id,parent=node.parent.block.id)
            for child in node.children:
                add_node(child)
        tree = treelib.Tree()
        tree.create_node(self.root.block.id,self.root.block.id)
        for child in self.root.children:
            add_node(child)
        # dot = Source(tree.to_graphviz())
        # dot.format = 'png'
        # dot.render('tree.png',view=False)
        tree.show()
    
    def add_blk(self,block:Block,timestamp:float) -> tuple[bool,bool]:
        # print("adding block: ",block.id)
        if block in self.seen_blks:
            return False,False
        self.seen_blks.add(block)
        parent_node = self.find_node(block.prev_blk_id)
        # print("trying to find parent node:",block.prev_blk_id)
        if parent_node is None:
            # print("parent node is none")
            if block.prev_blk_id not in self.blk_cache:
                self.blk_cache[block.prev_blk_id] = []
            self.blk_cache[block.prev_blk_id].append(block)
            return False,False
        if parent_node.add_child(TreeNode(block,timestamp)):
            # print("parent node is ",parent_node.block.id)
            if block.id in self.blk_cache:
                for blk in self.blk_cache[block.id]:
                    self.add_blk(blk,timestamp)
                self.blk_cache.pop(block.id)
            _, max_depth = self.longest_chain_node()
            if max_depth > self.last_max_depth:
                self.last_max_depth = max_depth
                return True,True
            return True,False
        else:
            if block.id in self.blk_cache:
                self.blk_cache.pop(block.id)
            return False,False
        
    def find_node(self,block_id:int)-> TreeNode:
        def dfs(node:TreeNode) -> TreeNode:
            if node.block.id == block_id:
                return node
            for child in node.children:
                temp = dfs(child)
                if temp is not None:
                    return temp
            return None
        
        return dfs(self.root)
    
    def longest_chain_node(self) -> tuple[TreeNode,int]:
        def dfs(node:TreeNode,depth:int) -> TreeNode:
            nonlocal max_depth_so_far,corresponding_node
            if len(node.children) == 0:
                if depth > max_depth_so_far:
                    max_depth_so_far = depth
                    corresponding_node = node
                    return
            for child in node.children:
                dfs(child,depth+1)
        max_depth_so_far = -1
        corresponding_node = None
        dfs(self.root,0)
        # print("max_depth_so_far",max_depth_so_far)
        return corresponding_node, max_depth_so_far
        
    def gen_blk(self) -> Block:
        longest_chain_node,max_depth = self.longest_chain_node()
        # print("mining on ",longest_chain_node.block.id)
        txns_in_longest_chain = set()
        node = longest_chain_node
        while node is not None:
            txns_in_longest_chain.update(node.block.transactions)
            node = node.parent
        remaining_txns = self.seen_txns - txns_in_longest_chain
        available_balance = longest_chain_node.peers_balance.copy()
        txns_added_to_blk = []
        for txn in remaining_txns:
            if txn.amount <= available_balance[txn.sender_id]:
                txns_added_to_blk.append(txn)
                available_balance[txn.sender_id] -= txn.amount
                available_balance[txn.receiver_id] += txn.amount
                if len(txns_added_to_blk) == MAX_TXNS_PER_BLK:
                    break
        # print("prev_blk_id",longest_chain_node.block.id)
        return Block(longest_chain_node.block.id,txns_added_to_blk)
        