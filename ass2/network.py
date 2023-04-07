from node import Node
from adversary_node import AdversaryNode
import random
from event_queue import event_queue
from event import Event
from typing import List
from params import *
from block import Block
from block_tree import BlockTree
from transaction import Transaction

class Network:
    """
    Simulates a network of nodes
    """
    
    transmission_delay = None
    internet_speed = None 
    def __init__(self,n:int,z0:float,z1:float) -> None:
        """initializes a network with n nodes and z0 fraction of slow nodes and z1 fraction of low cpu nodes

        Args:
            n (int): no. of nodes in the network
            z0 (float): fraction of slow nodes
            z1 (float): fraction of low cpu nodes
        """
        
        self.n = n
        self.z0 = z0
        self.z1 = z1
        self.nodes:List[Node] = []
        self.set_genesis_block()
        self.init_nodes(LB_DEG,UB_DEG)
        self.set_transmission_delay()
        self.set_internet_speed()
    
    def __str__(self) -> str:
        """
        prints the network
        Returns:
            str: string representation of the network
        """
        return "".join([str(node) for node in self.nodes])
  
    def generate_random_graph(self,lb_degree:int=4,ub_degree:int=8) -> list:
        """generate a random graph with degree of adversary node = adversary_degree and rest nodes between lb_degree and ub_degree

        Args:
            lb_degree (int, optional): lower bound on degree of other nodes. Defaults to 4.
            ub_degree (int, optional): upper bound on degree of other nodes. Defaults to 8.

        Returns:
            list: adj list of the random graph
        """
        
        # initialize adjacency list
        adj_list = [[] for _ in range(self.n)]
        # for adversary node
        adversary_degree = int(zeta * (self.n - 1))
        peers = random.sample(range(1,self.n),k=adversary_degree)
        for peer in peers:
            adj_list[0].append(peer)
            adj_list[peer].append(0)
        # iterate over all nodes
        for node in range(1,self.n):
            # random degree of the node
            degree = random.randint(lb_degree,ub_degree)
            # if the node has less than the required degree, then add more peers
            if len(adj_list[node]) < degree:
                for _ in range(degree - len(adj_list[node])):
                    # randomly select a peer
                    peer = random.randint(1,self.n-1)  
                    # set to store peers already tried
                    peers_tried = set()
                    # flag to check if the peer is valid
                    valid_peer = True   
                    peers_tried.add(peer)
                    # peer is valid if it is not the same node, not already a peer and has degree less than upper bound
                    while peer == node or peer in adj_list[node] or len(adj_list[peer]) >= ub_degree:
                        # if all peers have been tried, then the node is not connected to the network
                        if len(peers_tried) == self.n - 1:
                            valid_peer = False
                            break
                        # try a new peer
                        peer = random.randint(1,self.n-1)
                        peers_tried.add(peer)
                    # if the peer is valid, then add it to the adjacency list
                    if valid_peer:
                        adj_list[node].append(peer)
                        adj_list[peer].append(node)
        return adj_list
    
    def generate_connected_graph(self,lb_degree:int=4,ub_degree:int=8) -> list:
        """
        generates a connected graph with n nodes and degree of each node between lb_degree and ub_degree

        Args:
            lb_degree (int, optional): lower bound on degree of each node. Defaults to 4.
            ub_degree (int, optional): upper bound on degree of each node. Defaults to 8.

        Returns:
            list: adjacency list of the graph
        """
        def dfs(node:int,visited:list) -> None:
            """
            performs a depth first search on the graph

            Args:
                node (int): node to start the search from
                visited (list): list of nodes already visited
            """
            visited[node] = True
            for peer in adj_list[node]:
                if not visited[peer]:
                    dfs(peer,visited)
        # generate a random graph
        adj_list = self.generate_random_graph(lb_degree,ub_degree)
        # array to keep track of visited nodes
        visited = [False for _ in range(self.n)]
        # perform a depth first search on the graph
        dfs(0,visited)
        # if all nodes are not visited, then the graph is not connected and we need to generate a new graph
        while False in visited:
            adj_list = self.generate_random_graph(lb_degree,ub_degree)
            visited = [False for _ in range(self.n)]
            dfs(0,visited)
        return adj_list
        
    def init_nodes(self,lb_degree:int=4,ub_degree:int=8) -> None:
        """
            initializes the nodes in the network
        """
        # generate a connected graph
        adj_list = self.generate_connected_graph(lb_degree,ub_degree)
        # randomly select slow and low cpu nodes
        slow_nodes = random.sample(range(1,self.n),int(self.z0*(self.n-1)))
        low_cpu_nodes = random.sample(range(1,self.n),int(self.z1*(self.n-1)))
        # create nodes
        hashing_power = [1 if i in low_cpu_nodes else 10 for i in range(self.n)]
        hashing_power[0] = 0
        total_hashing_power = sum(hashing_power)
        hashing_power = [(1-adversary_hashing_power)*hp/total_hashing_power for hp in hashing_power]
        hashing_power[0] = adversary_hashing_power
        self.nodes.append(AdversaryNode(0,0,0,adj_list[0],hashing_power[0]))
        # self.nodes.append(Node(0,0,0,adj_list[0],hashing_power[0]))
        for id in range(1,self.n):
            self.nodes.append(Node(id,id in slow_nodes,id in low_cpu_nodes,adj_list[id],hashing_power[id]))
    
    def set_transmission_delay(self) -> None:
        """sets the transmission delay between each pair of nodes
        """
        Network.transmission_delay = [[random.uniform(rho_lb,rho_ub) for _ in range(self.n)] for _ in range(self.n)]
    
    def set_internet_speed(self) -> None:
        """sets the internet speed between each pair of nodes
        """
        Network.internet_speed = [[not (self.nodes[i].slow or self.nodes[j].slow) for i in range(self.n)] for j in range(self.n)]

        
    def set_genesis_block(self) -> None:
        """sets the genesis block for each node
        """
        # Policy: all nodes will receive STARTING_BALANCE coins from node -1 
        transactions = [Transaction(-1,i,STARTING_BALANCE) for i in range(self.n)]
        BlockTree.genesis_block = Block(-1,transactions,is_genesis_block=True)
        
    def process_event(self,event:Event)->None:
        """processes an event 
        Args:
            event (Event): receive/generated event for block or transaction
        """
        if event.event_type == GENERATE_TXN:
            self.nodes[event.node].generate_txn(event.trigger_time)
        elif event.event_type == RECEIVE_TXN:
            self.nodes[event.node].receive_txn(event.object,event.trigger_time,Network.transmission_delay,Network.internet_speed)
        elif event.event_type == GENERATE_BLK:
            if event.node == 0:
                self.nodes[event.node].generate_blk(event.object,event.trigger_time,Network.transmission_delay,Network.internet_speed)
            else:
                self.nodes[event.node].generate_blk(event.object,event.trigger_time)
        elif event.event_type == RECEIVE_BLK:
            self.nodes[event.node].receive_blk(event.object,event.trigger_time,Network.transmission_delay,Network.internet_speed)
    
    def analyze(self) -> None:
        """analyzes the network and writes the results to a file
        """
        for node in self.nodes:
            node.analyze()
        freq_blks_main = self.nodes[0].get_freq_blks_main()
        freq_blks_all = self.nodes[0].get_freq_blks_all()
        with open("./output/network.txt","w") as f:
            f.write(self.__str__())
            for a in freq_blks_all:
                if a in freq_blks_main:
                    f.write(f'Node {a}: total mined:{freq_blks_all[a]} In main chain:{freq_blks_main[a]} Ratio:{freq_blks_main[a]/freq_blks_all[a]}\n')
                else:
                    f.write(f'Node {a}: total mined:{freq_blks_all[a]} In main chain:0 Ratio:0\n')
            if 0 not in freq_blks_all:
                freq_blks_all[0] = 0
            if 0 not in freq_blks_main:
                freq_blks_main[0] = 0
            if freq_blks_all[0] == 0:
                f.write(f"MPU Adv: 0\n")
            else:
                f.write(f"MPU Adv: {freq_blks_main[0]/freq_blks_all[0]}\n")
            f.write(f"MPU All: {sum(freq_blks_main.values())/sum(freq_blks_all.values())}")
        with open("./graphs/network.txt","a") as f:
            f.write(f"n: {n} ATTACK_TYPE: {ATTACK_TYPE} ZETA: {zeta} HASHING POWER: {adversary_hashing_power}\n")
            if freq_blks_all[0] == 0:
                f.write(f"MPU Adv: 0\n")
            else:
                f.write(f"MPU Adv: {freq_blks_main[0]/freq_blks_all[0]}\n")
            f.write(f"MPU All: {sum(freq_blks_main.values())/sum(freq_blks_all.values())}\n")    
        