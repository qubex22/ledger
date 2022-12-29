import csv
import hashlib

# Initialize a dictionary to store the balance of each participant
balances = {
    "A": 100,
    "B": 50
}

# Initialize a list to store the blocks of transactions
blocks = []

def calculate_merkle_root(transactions):
    # If the block has no transactions, return 0 as the merkle root
    if not transactions:
        return 0

    # Initialize a list to store the hashes of the transactions
    transaction_hashes = []

    # Iterate over the transactions in the block
    for transaction in transactions:
        # Calculate the hash of the transaction
        transaction_hash = hashlib.sha256(str(transaction).encode()).hexdigest()

        # Add the hash to the list
        transaction_hashes.append(transaction_hash)

    # If the list has an odd number of elements, duplicate the last element to make it even
    if len(transaction_hashes) % 2 != 0:
        transaction_hashes.append(transaction_hashes[-1])

    # Initialize a list to store the hashes of the pairs of transactions
    pair_hashes = []

    # Iterate over the transaction hashes in pairs
    for i in range(0, len(transaction_hashes), 2):
        # Calculate the hash of the pair of transaction hashes
        pair_hash = hashlib.sha256(str(transaction_hashes[i] + transaction_hashes[i+1]).encode()).hexdigest()

        # Add the hash to the list
        pair_hashes.append(pair_hash)

    # If the list has more than one element, repeat the process with the pairs of transaction hashes
    if len(pair_hashes) > 1:
        return calculate_merkle_root(pair_hashes)
    # Otherwise, return the single element in the list as the merkle root
    else:
        return pair_hashes[0]

# Open the transaction_notifications.csv file in read mode
with open("transaction_notifications.csv", "r") as file:
    # Read the file as a CSV
    reader = csv.DictReader(file)

    # Initialize a list to store the current block of transactions
    current_block = []

    # Iterate over the rows in the CSV
    for row in reader:
        # Extract the values from the row
        transaction_id = row["ID"]
        sender = row["From"]
        receiver = row["To"]
        value = int(row["Value"])
        fee = float(value) * 0.002
        amount = value+fee
        
        # Initialize the balance of the sender and receiver to 0 if it does not exist in the dictionary
        if sender not in balances:
            balances[sender] = 0
        if receiver not in balances:
            balances[receiver] = 0
        print(f"Transaction {row['ID']}: From {row['From']} to {row['To']}, value {amount} {row['What']}")
        print("Sender: "+str(balances[sender]))
        print("Receiver: "+str(balances[receiver]))
        # Check if the sender has sufficient balance for the transaction
        if balances[sender] >= amount:
            # Update the balances of the sender and receiver
            balances[sender] -= amount
            balances[receiver] += value

            # Add the transaction to the current block
            current_block.append(row)

            # If the current block has reached the maximum size, add it to the list of blocks and start a new block
            if len(current_block) == 5:
                blocks.append(current_block)
                current_block = []
        else:
            print(f"Error in Transaction {row['ID']} Sender {row['From']} does not have sufficient balance to make transaction")
        # Print the balance of each participant
        #print(" Balances:")
        #for participant, balance in balances.items():
        #    print(f"   {participant}: {balance} EUR")
    # Add the remaining transactions in the current block to the list of blocks
    if current_block:
        blocks.append(current_block)
    # Print final balances
    print(" Balances:")
    for participant, balance in balances.items():
        print(f"   {participant}: {balance} EUR")

# Print the list of blocks
print ("----------------------------------------------------------------------------")
print ("BLOCKS")
print ("----------------------------------------------------------------------------")
for i, block in enumerate(blocks):
    print(f"Block {i+1}:")
    for transaction in block:
        print(f"  Transaction {transaction['ID']}: From {transaction['From']} to {transaction['To']}, value {transaction['Value']} {transaction['What']}")

# Open the ledger.csv file in write mode
with open("ledger.csv", "w") as file:
    # Write the header row
    file.write("Block Height,Block Hash,Previous Block Hash,Transaction ID,Transaction Hash,Sender,Receiver,Amount,Fee,What\n")

    # Iterate over the blocks
    for i, block in enumerate(blocks):
        # Initialize the previous block hash to 0 if it is the first block
        if i == 0:
            previous_block_hash = 0
        # Otherwise, calculate the hash of the previous block
        else:
            previous_block_hash = block_hash

        # Calculate the merkle root for the current block
        merkle_root = calculate_merkle_root(block)

        # Calculate the block hash by hashing the previous block hash and the merkle root
        block_hash = hashlib.sha256(str(str(previous_block_hash) + str(merkle_root)).encode()).hexdigest()

        # Iterate over the transactions in the block
        for transaction in block:
            # Extract the transaction information
            transaction_id = transaction["ID"]
            transaction_hash = transaction["SHA-256"]
            sender = transaction["From"]
            receiver = transaction["To"]
            amount = transaction["Value"]
            fee = float(amount) * 0.002
            what = transaction["What"]

            # Write the transaction information to the file
            file.write(f"{i},{block_hash},{previous_block_hash},{transaction_id},{transaction_hash},{sender},{receiver},{amount},{fee},{what}\n")
