import random
from transaction import Transaction
from event_queue import event_queue
from params import *
from event import Event
from packet import Packet
from adversary_block_tree import AdversaryBlockTree
from block import Block
from node import Node
from typing import List

class AdversaryNode(Node):
    
    def __init__(self, id: int, slow: bool, low_cpu: bool, peers: list, hashing_power: float) -> None:
        super().__init__(id, slow, low_cpu, peers, hashing_power)
        self.private_chain = [] # private chain of the adversary
        self.block_tree:AdversaryBlockTree = AdversaryBlockTree() 
        self.private_branch_len = 0
        
    def generate_blk(self,longest_chain_blk_id:int,trigger_time:float) -> None:
        if longest_chain_blk_id != self.block_tree.longest_chain_node()[0].block.id:
            return
        blk = self.block_tree.gen_blk()
        blk.transactions.append(Transaction(-1,self.id,MINING_REWARD))
        blk.mined_by = self.id
        with open(f"./output/node_{self.id}_log.txt","a") as f:
            f.write(f"{trigger_time}: Mined Event == {blk}\n")
        delta_prev = self.block_tree.len_private_chain() - self.block_tree.len_public_chain()
        self.private_chain.append(blk)
        self.private_branch_len += 1
        self.block_tree.add_blk(blk,trigger_time)
        if delta_prev == 0 and self.private_branch_len == 2:
            self.publish_private_chain(trigger_time)
            self.block_tree.update_forked_node()
            self.private_branch_len = 0
        # event_queue.add_event(Event(trigger_time,RECEIVE_BLK,self.id,Packet(-1,self.id,blk)))
        next_blk_gen_time = trigger_time + random.expovariate(self.hashing_power/inter_blk_time)
        event_queue.add_event(Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id))
    
    def publish_private_chain(self,trigger_time:float) -> None:
        for blk in self.private_chain:
            event_queue.add_event(Event(trigger_time,RECEIVE_BLK,self.id,Packet(-1,self.id,blk)))    
        self.private_chain = []
        
    
    def receive_blk(self,packet:Packet,received_time:float,transmission_delay:list,internet_speed:list) -> None:
        delta_prev = self.block_tree.len_private_chain() - self.block_tree.len_public_chain()
        print("len private chain",self.block_tree.len_private_chain())
        print("len public chain",self.block_tree.len_public_chain())
        sender_id = packet.source
        blk:Block = packet.data
        is_added, is_new_longest_chain = self.block_tree.add_blk(blk,received_time)
        if sender_id == -1:
            size_blk = (1+len(blk.transactions))*SIZE_TXN
            for peer in self.peers:
                if peer != sender_id:
                    time_to_send = transmission_delay[self.id][peer]
                    if internet_speed[self.id][peer]:
                        time_to_send += size_blk/c_fast
                        time_to_send += random.expovariate(c_fast/queuing_delay_constant)
                    else:
                        time_to_send += size_blk/c_slow
                        time_to_send += random.expovariate(c_slow/queuing_delay_constant)
                    event_queue.add_event(Event(received_time+time_to_send,RECEIVE_BLK,peer,Packet(self.id,peer,blk)))
            return
    
        if not is_added:
            return
        if is_added and sender_id != -1:
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{received_time}: Received Event == Recieved {blk} from Node {sender_id}\n")
        print(delta_prev,self.private_chain)
        delta = self.block_tree.len_private_chain() - self.block_tree.len_public_chain()
        if is_new_longest_chain and blk.mined_by != self.id:
            next_blk_gen_time = received_time + random.expovariate(self.hashing_power/inter_blk_time)
            blk_gen_event = Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id)
            event_queue.add_event(blk_gen_event)
            # update the forked_node
            self.block_tree.update_forked_node()
            self.private_chain = []
        if delta < delta_prev:    
            if delta_prev == 0:
                self.private_branch_len = 0
            if delta_prev == 1:
                self.publish_private_chain(received_time)
            elif delta_prev == 2:
                self.publish_private_chain(received_time)
                self.block_tree.update_forked_node()
                self.private_branch_len = 0
            elif delta_prev >= 3:
                event_queue.add_event(Event(received_time,RECEIVE_BLK,-1,Packet(self.id,-1,self.private_chain[0])))
                self.private_chain = self.private_chain[1:]                
        # don't forward other nodes blocks
        if blk.mined_by != 0:
            return
        
        size_blk = (1+len(blk.transactions))*SIZE_TXN
        for peer in self.peers:
            if peer != sender_id:
                time_to_send = transmission_delay[self.id][peer]
                if internet_speed[self.id][peer]:
                    time_to_send += size_blk/c_fast
                    time_to_send += random.expovariate(c_fast/queuing_delay_constant)
                else:
                    time_to_send += size_blk/c_slow
                    time_to_send += random.expovariate(c_slow/queuing_delay_constant)
                event_queue.add_event(Event(received_time+time_to_send,RECEIVE_BLK,peer,Packet(self.id,peer,blk)))
    
    