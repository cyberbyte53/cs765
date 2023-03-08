from block import Block
from tree_node import TreeNode
from transaction import Transaction
from typing import Dict,List
from params import *
import treelib
import subprocess

class BlockTree:
    
    """
    represents the block tree
    """
    genesis_block:Block = None 
    
    def __init__(self) -> None:
        """initialize the block tree
        """
        self.root:TreeNode = TreeNode(BlockTree.genesis_block,0)
        TreeNode.calculate_balance(self.root)
        self.seen_txns:set[Transaction] = set()
        self.seen_blks:set[Block] = set()
        self.last_max_depth = -1
        self.blk_cache:dict[int,List[Block]] = {}
    
    def draw_tree(self,filename:str):
        """draws the block tree
        """
        def add_node(node:TreeNode):
            """helper function to add a node to the tree
            Args:
                node (TreeNode): node to add
            """
            tree.create_node(tag=f'{node.block.id} ({node.block.mined_by})',identifier=node.block.id,parent=node.parent.block.id)
            for child in node.children:
                add_node(child)
        tree = treelib.Tree()
        tree.create_node(self.root.block.id,self.root.block.id)
        for child in self.root.children:
            add_node(child)
        tree.to_graphviz("temp.dot")
        subprocess.call(["dot", "-Tpng", "temp.dot", "-o",filename])
        subprocess.call(["rm","temp.dot"])
    
    def add_blk(self,block:Block,timestamp:float) -> tuple[bool,bool]:
        """checks if the block is valid and adds it to the tree

        Args:
            block (Block): incoming block
            timestamp (float): received time of the block

        Returns:
            tuple[bool,bool]: is_block_added, is_new_longest_chain_formed
        """
        # if block already exists in the tree return False, False
        if block in self.seen_blks:
            return False,False
        # add the block to the tree
        self.seen_blks.add(block)
        # find the parent node
        parent_node = self.find_node(block.prev_blk_id)
        # if parent node is None, add the block to the cache
        if parent_node is None:
            if block.prev_blk_id not in self.blk_cache:
                self.blk_cache[block.prev_blk_id] = []
            self.blk_cache[block.prev_blk_id].append(block)
            return False,False
        # add the block to the parent node
        if parent_node.add_child(TreeNode(block,timestamp)):
            # if the block is added to the parent node
            # check if any of its children are in the cache
            # if yes add them to the tree
            if block.id in self.blk_cache:
                for blk in self.blk_cache[block.id]:
                    self.add_blk(blk,timestamp)
                self.blk_cache.pop(block.id)
            # check if the longest chain has changed
            _, max_depth = self.longest_chain_node()
            if max_depth > self.last_max_depth:
                # update the last max depth and indicate that a new longest chain has been formed
                self.last_max_depth = max_depth
                return True,True
            return True,False
        else:
            # the block was invalid 
            # and hence any children of the block are invalid
            if block.id in self.blk_cache:
                self.blk_cache.pop(block.id)
            return False,False
        
    def find_node(self,block_id:int)-> TreeNode:
        """finds the node with the given block id

        Args:
            block_id (int): id of the block

        Returns:
            TreeNode: TreeNode with the given block id
        """
        def dfs(node:TreeNode) -> TreeNode:
            """helper function to find the node using dfs

            Args:
                node (TreeNode): current node

            Returns:
                TreeNode: TreeNode with the given block id in the subtree rooted at node else None
            """
            if node.block.id == block_id:
                return node
            for child in node.children:
                temp = dfs(child)
                if temp is not None:
                    return temp
            return None
        return dfs(self.root)
    
    def longest_chain_node(self) -> tuple[TreeNode,int]:
        """finds the node with the longest chain
        Returns:
            tuple[TreeNode,int]: node with the longest chain, length of the longest chain
        """
        def dfs(node:TreeNode,depth:int) -> TreeNode:
            """uses dfs to find the node with the longest chain

            Args:
                node (TreeNode): current node
                depth (int): depth of the current node

            Returns:
                TreeNode: the node with the longest chain rooted at node
            """
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
        return corresponding_node, max_depth_so_far
        
    def gen_blk(self) -> Block:
        """generates a block from the transactions in the tree

        Returns:
            Block: returns a block with the transactions in the tree
        """
        # find the node with the longest chain
        longest_chain_node,max_depth = self.longest_chain_node()
        # find the transactions in the longest chain
        txns_in_longest_chain = set()
        node = longest_chain_node
        while node is not None:
            txns_in_longest_chain.update(node.block.transactions)
            node = node.parent
        # find the remaining transactions
        remaining_txns = self.seen_txns - txns_in_longest_chain
        # find the balance of the peers in the longest chain
        available_balance = longest_chain_node.peers_balance.copy()
        txns_added_to_blk = []
        for txn in remaining_txns:
            # add the transaction to the block if the sender has enough balance 
            if txn.amount <= available_balance[txn.sender_id]:
                txns_added_to_blk.append(txn)
                available_balance[txn.sender_id] -= txn.amount
                available_balance[txn.receiver_id] += txn.amount
                if len(txns_added_to_blk) == MAX_TXNS_PER_BLK:
                    break
        return Block(longest_chain_node.block.id,txns_added_to_blk)
    
    def get_freq_blks_main(self) -> dict:
        """finds the frequency of the miners in the longest chain

        Returns:
            dict: frequency of the miners in the longest chain
        """
        freq = {}
        longst_chain_node,_ = self.longest_chain_node()
        node = longst_chain_node
        while node is not None:
            if node.block.mined_by not in freq:
                freq[node.block.mined_by] = 0
            freq[node.block.mined_by] += 1
            node = node.parent
        freq.pop(-1)
        return freq
    
    def get_freq_blks_all(self) -> dict:
        """finds the frequency of the miners in the tree

        Returns:
            dict: frequency of the miners in the tree
        """
        freq = {}
        def dfs(node:TreeNode) -> None:
            if node.block.mined_by not in freq:
                freq[node.block.mined_by] = 0
            freq[node.block.mined_by] += 1
            for child in node.children:
                dfs(child)
        dfs(self.root)
        freq.pop(-1)
        return freq