from block import Block
from tree_node import TreeNode
from transaction import Transaction
from typing import Dict,List
from params import *
from block_tree import BlockTree

class AdversaryBlockTree(BlockTree):
    def __init__(self):
        super().__init__()
        self.private_chain:List[Block] = [] # private chain of the adversary
        self.head_private_chain:TreeNode = self.root # forked block is head of the private chain and is public
     
    def add_pvt_blk(self,blk:Block):
        self.private_chain.append(blk)
        print(f"block {blk.id} added to private chain")
        
    def print_chain(node:TreeNode,leaf:TreeNode):
        if leaf is None:
            return [node.block.id]
        stk = [leaf.block.id]
        while node != leaf:
            leaf = leaf.parent
            stk.append(leaf.block.id)
        return stk[::-1]
    
    def len_private_chain(self):
        chain = AdversaryBlockTree.print_chain(self.root,self.head_private_chain)
        chain.extend(list(map(lambda x:x.id,self.private_chain)))
        # print("private chain: ",chain)
        return len(chain) - 1,chain
    
    def len_public_chain(self):
        node,depth = self.longest_chain_node()
        print("public chain: ",AdversaryBlockTree.print_chain(self.root,node))
        return depth
    
    def update_head_private_chain(self,add_from_private_chain:bool=True):
        blk = None
        if add_from_private_chain:
            if len(self.private_chain) == 0:
                print("private chain is empty")
                return None
            blk = self.private_chain.pop(0)
            #todo timestamp update
            is_added,is_new_longest = self.add_blk(blk,0)
            if not is_added:
                print("block not added from private chain to public chain")
                return None
            treenode = self.find_node(blk.id)
            self.head_private_chain = treenode
        else:
            treenode = self.longest_chain_node()[0]
            self.head_private_chain = treenode
        print("fork updated to blk id:",treenode.block.id)
        return blk
    
    def gen_blk(self) -> Block:
    
        txns_in_pvt_chain = set()
        for blk in self.private_chain:
            txns_in_pvt_chain.update(blk.transactions)
        node = self.head_private_chain
        while node is not None:
            txns_in_pvt_chain.update(node.block.transactions)
            node = node.parent
        # find the remaining transactions
        remaining_txns = self.seen_txns - txns_in_pvt_chain
        # find the balance of the peers in the longest chain
        available_balance = self.head_private_chain.calculate_balance_for_blocks(self.private_chain)
        txns_added_to_blk = []
        for txn in remaining_txns:
            # add the transaction to the block if the sender has enough balance 
            if txn.amount <= available_balance[txn.sender_id]:
                txns_added_to_blk.append(txn)
                available_balance[txn.sender_id] -= txn.amount
                available_balance[txn.receiver_id] += txn.amount
                if len(txns_added_to_blk) == MAX_TXNS_PER_BLK:
                    break
        if len(self.private_chain) == 0:
            gen_blk = Block(self.head_private_chain.block.id,txns_added_to_blk)
        else:    
            gen_blk = Block(self.private_chain[-1].id,txns_added_to_blk)     
        return gen_blk
