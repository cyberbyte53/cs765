import random
from transaction import Transaction
from event_queue import event_queue
from params import *
from event import Event
from packet import Packet
from block_tree import BlockTree
from block import Block

class Node:
    """
    Represents a node in the network
    """ 
    
    def __init__(self,id:int,slow:bool,low_cpu:bool,peers:list,hashing_power:float) -> None:
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
        self.hashing_power = hashing_power
        self.block_tree:BlockTree = BlockTree()
        with open(f"./output/node_{self.id}_log.txt","w") as f:
            f.write(self.__str__())
            f.write("========================================\n")
        self.generate_txn(0)
        event_queue.add_event(Event(random.expovariate(self.hashing_power/inter_blk_time),GENERATE_BLK,self.id,0))
        
     
    def __str__(self) -> str:
        """
        prints the node's id, peers, slow and low_cpu
        Returns:
            str: string representation of the node
        """
        return f"Node:{self.id}\nPeers:{self.peers}\nSlow:{self.slow}\nLow cpu:{self.low_cpu}\n"
      
    def generate_txn(self,trigger_time:float) -> None:
        """
        generates a transaction for the node

        Returns:
            Transaction: transaction generated by the node
        """

        # generate a random receiver
        receiver_id = random.randint(0,n-1)
        # avoid self transactions
        if receiver_id == self.id:
            receiver_id = (receiver_id+1)%n
        # generate a random amount
        amount = random.randint(TXN_COIN_LB,TXN_COIN_UB)
        # create a new transaction
        txn = Transaction(self.id,receiver_id,amount)
        # print(f"Node {self.id} generated transaction {txn}")
        # find the time at which the transaction is generated
        gen_time = trigger_time + random.expovariate(1/inter_txn_time)
        # creat a fake receive event from -1 to self.id
        txn_receive_event = Event(gen_time,RECEIVE_TXN,self.id,Packet(-1,self.id,txn))
        # create next transaction generation event
        next_txn_gen_event = Event(gen_time,GENERATE_TXN,self.id,None)
        # add the events to the event queue
        event_queue.add_event(txn_receive_event)
        event_queue.add_event(next_txn_gen_event)
    
    def receive_txn(self,packet:Packet,received_time:float,transmission_delay:list,internet_speed:list) -> None:
        """Receives a transaction from a peer

        Args:
            packet (Packet): packet containing the transaction
            received_time (float): time at which the packet is received
            transmission_delay (list): list of transmission delays between nodes
            internet_speed (list): list of internet speeds between nodes
        """
        # get the sender id and the transaction
        sender_id = packet.source
        txn = packet.data
        
        # if the transaction has already been seen, return do nothing
        if txn in self.block_tree.seen_txns:
            return
        # else add the transaction to the list of transactions and the set of seen transactions
        self.block_tree.seen_txns.add(txn)
        # loop over all peers and send the transaction to them
        for peer in self.peers:
            # if the peer is the sender, do not send the transaction back
            if peer != sender_id:
                # time_to_send = transmission_delay + propagation_delay + queuing_delay
                time_to_send = transmission_delay[self.id][peer]
                if internet_speed[self.id][peer]:
                    time_to_send += SIZE_TXN/c_fast
                    time_to_send += random.expovariate(c_fast/queuing_delay_constant)
                else:
                    time_to_send += SIZE_TXN/c_slow
                    time_to_send += random.expovariate(c_slow/queuing_delay_constant)
                # add the event to the recieve event queue
                event_queue.add_event(Event(received_time+time_to_send,RECEIVE_TXN,peer,Packet(self.id,peer,txn)))

    def generate_blk(self,longest_chain_blk_id:int,trigger_time:float) -> None:
        if longest_chain_blk_id != self.block_tree.longest_chain_node()[0].block.id:
            return
        blk = self.block_tree.gen_blk()
        blk.transactions.append(Transaction(-1,self.id,MINING_REWARD))
        blk.mined_by = self.id
        with open(f"./output/node_{self.id}_log.txt","a") as f:
            f.write(f"{trigger_time}: Mined Event == {blk}\n")
        event_queue.add_event(Event(trigger_time,RECEIVE_BLK,self.id,Packet(-1,self.id,blk)))
        next_blk_gen_time = trigger_time + random.expovariate(self.hashing_power/inter_blk_time)
        event_queue.add_event(Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id))
        
    def receive_blk(self,packet:Packet,received_time:float,transmission_delay:list,internet_speed:list) -> None:
        sender_id = packet.source
        blk = packet.data
        is_added, is_new_longest_chain = self.block_tree.add_blk(blk,received_time)
        if not is_added:
            return
        if is_added and sender_id != -1:
            with open(f"./output/node_{self.id}_log.txt","a") as f:
                f.write(f"{received_time}: Received Event == Recieved {blk} from Node {sender_id}\n")
        if is_new_longest_chain and sender_id != -1:
            next_blk_gen_time = received_time + random.expovariate(self.hashing_power/inter_blk_time)
            blk_gen_event = Event(next_blk_gen_time,GENERATE_BLK,self.id,blk.id)
            event_queue.add_event(blk_gen_event)
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
                
    def analyze(self) -> None:
        self.block_tree.draw_tree("./output/node_"+str(self.id)+"_tree.png")

    def get_freq_blks_main(self) -> None:
        return self.block_tree.get_freq_blks_main()
    
    def get_freq_blks_all(self) -> None:
        return self.block_tree.get_freq_blks_all()