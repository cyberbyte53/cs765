from transaction import Transaction
from typing import List

class Block:
    """represent a block in the blockchain
    """
    available_id = 0
    def __init__(self,prev_blk_id:int,transactions:list[Transaction],is_genesis_block:bool=False,mined_by:int=-1) -> None:
        """initialize a block

        Args:
            prev_blk_id (int): id of the previous block
            transactions (list[Transaction]): transactions in the block
            is_genesis_block (bool, optional): if this is the genesis block, set the id to 0.Defaults to False.
            mined_by (int, optional): id of the miner. Defaults to -1.
        """
        if is_genesis_block:
            self.id = 0
        else:
            Block.available_id += 1
            self.id = Block.available_id
        self.prev_blk_id = prev_blk_id
        self.transactions = transactions
        self.mined_by = mined_by
    
    def __str__(self) -> str:
        """print the block
        Returns:
            str: string representation of the block
        """
        return f"Block:{self.id} Prev block:{self.prev_blk_id} Miner Node:{self.mined_by}"