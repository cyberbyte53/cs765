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
        self.block_tree:AdversaryBlockTree = AdversaryBlockTree() 
        self.is_zero_ = False
        
    def generate_blk(self,longest_chain_blk_id:int,trigger_time:float,transmission_delay:list,internet_speed:list) -> None:
        if ATTACK_TYPE == SELFISH_MINE_ATTACK:
            depth,chain = self.block_tree.len_private_chain()
            if longest_chain_blk_id != chain[-1]:
                return
            blk = self.block_tree.gen_blk()
            blk.transactions.append(Transaction(-1,self.id,MINING_REWARD))
            blk.mined_by = self.id
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{trigger_time}: Mined Event == {blk}\n")
            self.block_tree.add_pvt_blk(blk)
            if self.is_zero_:
                self.publish_private_chain(trigger_time,transmission_delay,internet_speed)
                self.is_zero_ = False
            # check 
            next_blk_gen_time = trigger_time + random.expovariate(self.hashing_power/inter_blk_time)
            event_queue.add_event(Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id))
        elif ATTACK_TYPE == STUBBORN_MINE_ATTACK:
            depth,chain = self.block_tree.len_private_chain()
            if longest_chain_blk_id != chain[-1]:
                return
            blk = self.block_tree.gen_blk()
            blk.transactions.append(Transaction(-1,self.id,MINING_REWARD))
            blk.mined_by = self.id
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{trigger_time}: Mined Event == {blk}\n")
            self.block_tree.add_pvt_blk(blk)
            # check 
            next_blk_gen_time = trigger_time + random.expovariate(self.hashing_power/inter_blk_time)
            event_queue.add_event(Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id))
        
    def publish_private_chain(self,trigger_time:float,transmission_delay:list,internet_speed:list,all:bool=True) -> None:
        def send_blk(blk:Block):
            if blk is None:
                return
            size_blk = (1+len(blk.transactions))*SIZE_TXN
            for peer in self.peers:
                time_to_send = transmission_delay[self.id][peer]
                if internet_speed[self.id][peer]:
                    time_to_send += size_blk/c_fast
                    time_to_send += random.expovariate(c_fast/queuing_delay_constant)
                else:
                    time_to_send += size_blk/c_slow
                    time_to_send += random.expovariate(c_slow/queuing_delay_constant)
                event_queue.add_event(Event(trigger_time+time_to_send,RECEIVE_BLK,peer,Packet(self.id,peer,blk)))    
        if all:
            for i in range(len(self.block_tree.private_chain)):
                blk = self.block_tree.update_head_private_chain(trigger_time)
                send_blk(blk) 
        else:
            blk = self.block_tree.update_head_private_chain(trigger_time)
            send_blk(blk)
           
                
    def receive_blk(self,packet:Packet,received_time:float,transmission_delay:list,internet_speed:list) -> None:
        if ATTACK_TYPE == SELFISH_MINE_ATTACK:
            prev_private_chain_len,_ = self.block_tree.len_private_chain()
            prev_public_chain_len = self.block_tree.len_public_chain()
            sender_id = packet.source
            blk:Block = packet.data
            is_added, is_new_longest_chain = self.block_tree.add_blk(blk,received_time)
            if not is_added:
                return
            curr_private_chain_len,_ = self.block_tree.len_private_chain()
            curr_public_chain_len = self.block_tree.len_public_chain()
            prev_lead = prev_private_chain_len - prev_public_chain_len
            lead = curr_private_chain_len - curr_public_chain_len
            
        
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{received_time}: Received Event == Recieved {blk} from Node {sender_id}\n")
                
            if prev_lead == lead:
                return
            if lead < 0:
                assert len(self.block_tree.private_chain) == 0
                self.block_tree.update_head_private_chain(received_time,False)
                self.is_zero_ = False
            
            elif lead == 0:
                assert len(self.block_tree.private_chain) == 1
                self.is_zero_ = True
                self.publish_private_chain(received_time,transmission_delay,internet_speed)
            elif lead == 1:
                self.publish_private_chain(received_time,transmission_delay,internet_speed)
            else:
                self.publish_private_chain(received_time,transmission_delay,internet_speed,False)
            if lead < 0:  
                next_blk_gen_time = received_time + random.expovariate(self.hashing_power/inter_blk_time)
                blk_gen_event = Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id)
                event_queue.add_event(blk_gen_event)
        elif ATTACK_TYPE == STUBBORN_MINE_ATTACK:
            prev_private_chain_len,_ = self.block_tree.len_private_chain()
            prev_public_chain_len = self.block_tree.len_public_chain()
            sender_id = packet.source
            blk:Block = packet.data
            is_added, is_new_longest_chain = self.block_tree.add_blk(blk,received_time)
            if not is_added:
                return
            curr_private_chain_len,_ = self.block_tree.len_private_chain()
            curr_public_chain_len = self.block_tree.len_public_chain()
            prev_lead = prev_private_chain_len - prev_public_chain_len
            lead = curr_private_chain_len - curr_public_chain_len
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{received_time}: Received Event == Recieved {blk} from Node {sender_id}\n")
            if prev_lead == lead:
                return
            if lead < 0:
                self.block_tree.update_head_private_chain(received_time,False)
            else:
                self.publish_private_chain(received_time,transmission_delay,internet_speed,False)
            if lead < 0:  
                next_blk_gen_time = received_time + random.expovariate(self.hashing_power/inter_blk_time)
                blk_gen_event = Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id)
                event_queue.add_event(blk_gen_event)
            
            

    
        
   
    