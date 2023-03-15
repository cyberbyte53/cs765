n = 5 # number of nodes
z0 = 0.5 # fraction of slow nodes
z1 = 0.5 # fraction of low cpu nodes
zeta = 0.5 # fraction of honest nodes connected to the adversary node
adversary_hashing_power = 0.5 # fraction of hashing power of the adversary node
ITERATIONS = 1000000 # number of iterations to run the simulation
inter_txn_time = 20 # inter transaction time
inter_blk_time = 6000 # inter block time

# constants for the simulation
c_slow = 5 # link speed for slow internet (in Kbpms)
c_fast = 100 # link spped for fast internet (in Kbmps)
rho_lb = 10 # propagation delay lower bound (in ms)
rho_ub = 500 # propagation delay upper bound (in ms)
queuing_delay_constant = 96# (in kbits)
STARTING_BALANCE = 1000 # every node starts with this amount of coins
SIZE_TXN = 8 # in Kb
MAX_SIZE_BLK = 8*1024 # in Kb 
MAX_TXNS_PER_BLK = int(MAX_SIZE_BLK/SIZE_TXN) - 1 # maximum number of transactions per block
MINING_REWARD = 50 # mining reward for each block
TXN_COIN_LB = 1
TXN_COIN_UB = 10
GENERATE_TXN = 0
RECEIVE_TXN = 1
GENERATE_BLK = 2
RECEIVE_BLK = 3