import networkx as nx
import matplotlib.pyplot as plt
from params import *
import random
import json
from web3 import Web3
import re
import subprocess
import os
class Network:
    def __init__(self,contract,w3,debug=False) -> None:
        self.debug = debug
        self.contract = contract
        self.w3 = w3
        self.G = self.create_network()
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.draw_network()
    
    def create_network(self):
        # register n nodes 
        event = self.contract.events.UserRegistered()
        for i in range(n):
            txn_receipt = contract.functions.registerUser(i, f"user{i}").transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
            txn_receipt_json = json.loads(w3.to_json(txn_receipt))
            w3.eth.wait_for_transaction_receipt(txn_receipt)
            logs = event.get_logs()
            logs = json.loads(w3.to_json(logs))
            for log in logs:
                if log['event'] == 'UserRegistered':
                    print(f"{log['args']['name']} Registered Successfully")
        G = nx.powerlaw_cluster_graph(n, m, p)
        event = self.contract.events.AccountCreated()
        for u,v in G.edges():
            init_balance = int(random.expovariate(1/mean_starting_balance))
            G[u][v]['weight'] = {u: init_balance, v: init_balance}
            #------------------------------------------------------------------
            txn_receipt = contract.functions.createAcc(u,v,init_balance).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
            txn_receipt_json = json.loads(w3.to_json(txn_receipt))
            w3.eth.wait_for_transaction_receipt(txn_receipt)
            logs = event.get_logs()
            logs = json.loads(w3.to_json(logs))
            for log in logs:
                if log['event'] == 'AccountCreated':
                    print(f"Account Created Successfully: (user{log['args']['id']},user{log['args']['partner_id']},{log['args']['balance']})")
            #------------------------------------------------------------------
        return G


    def fire_transaction(self, u, v, amount=1):
        event = self.contract.events.TransactionStatus()
        txn_receipt = contract.functions.sendAmount(u,v,amount).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
        txn_receipt_json = json.loads(w3.to_json(txn_receipt))
        w3.eth.wait_for_transaction_receipt(txn_receipt)
        logs = event.get_logs()
        logs = json.loads(w3.to_json(logs))
        for log in logs:
            if log['event'] == 'TransactionStatus':
                if log['args']['success'] == True:
                    self.successful_transactions += 1
                    self.update_network(log['args']['path'],log['args']['amount'])
                    self.draw_network(log['args']['path'],f"Successful Transaction: (user{log['args']['id1']},user{log['args']['id2']},{log['args']['amount']})")
                    print(f"{self.failed_transactions+self.successful_transactions}:Transaction Successful: (user{log['args']['id1']},user{log['args']['id2']},{log['args']['amount']}) sent along path {log['args']['path']}")
                    return True
                    
                else:
                    self.failed_transactions += 1
                    self.draw_network(log['args']['path'],f"Failed Transaction: (user{log['args']['id1']},user{log['args']['id2']},{log['args']['amount']})")
                    print(f"{self.failed_transactions+self.successful_transactions}:Transaction Failed: (user{log['args']['id1']},user{log['args']['id2']},{log['args']['amount']})")
                    return False
    
    def fire_random_transactions(self, num_transactions):
        # open new file
        with open("results.txt", "w") as f:
            f.write(f"n={n} m={m} p={p} mean_starting_balance={mean_starting_balance} num_transactions={num_transactions}\n")
        succ = 0
        fail = 0
        for i in range(num_transactions):
            u,v = random.sample(range(n), 2)
            if(self.fire_transaction(u, v)):
                succ += 1
            else:
                fail += 1
            if((i+1)%print_freq==0):
                # write to file
                with open("results.txt", "a") as f:
                    f.write(f"{i+1}: success rate: {succ/(succ+fail)}\n")
                succ = 0
                fail = 0
                
    
    def update_network(self,path,amount):
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            self.G[u][v]['weight'][u] -= amount
            self.G[u][v]['weight'][v] += amount
        
    def draw_network(self,path=[],heading="Network"): 
        if not self.debug:   
            return
        G = self.G
        pos = nx.circular_layout(G)
        node_colors =  ['red' if node in path else 'blue' for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edge_labels(G, pos,edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True)},font_size=10)
        plt.title(heading)
        plt.savefig(f"./plots/{self.successful_transactions+self.failed_transactions}.png")
    
def empty_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
        
if __name__ == "__main__":
    #connect to the local ethereum blockchain
    provider = Web3.HTTPProvider('http://127.0.0.1:7545')
    w3 = Web3(provider)
    #check if ethereum is connected
    print(w3.is_connected())

    #replace the address with your contract address (!very important)
    output = subprocess.check_output(["truffle", "migrate",]).decode("utf-8")

    # Find the contract address using a regular expression
    pattern = r"contract address:\s+(\w+)"
    match = re.search(pattern, output)

    if match:
        contract_address = match.group(1)
    else:
        print("Contract address not found in output.")
    
    deployed_contract_address = contract_address

    #path of the contract json file. edit it with your contract json file
    compiled_contract_path ="build/contracts/Payment.json"
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']
    contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)
    
    # empty plots directory
    empty_dir("./plots")
    
    network = Network(contract,w3,True)
    network.fire_random_transactions(num_transactions)



