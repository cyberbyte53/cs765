class Transaction:
    def __init__(self, id:int, sender_id:int, receiver_id:int, amount:float) -> None:
        """
        Initializes a new transaction

        Args:
            id (int): Unique descriptor of the transaction
            sender_id (int): Unique descriptor of the sender
            receiver_id (float): Unique descriptor of the receiver
            amount (int): Amount of money transferred
        """
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
    
    def __str__(self) -> str:
        """
        prints the transaction's id, sender_id, receiver_id and amount
        Returns:
            str: string representation of the transaction
        """
        return f"{self.id}:{self.sender_id} pays {self.receiver_id} {self.amount} coins\n"
    