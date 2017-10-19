import pandas as pd
from web3 import Web3
from eth_utils import from_wei
from abis import auction_abi, wallet_abi



BID_OUTPUT_FILENAME = 'bids.csv'
TX_OUTPUT_FILENAME = 'txs.csv'

CONTRACT_CREATION_BLOCK = 4383437


web3 = Web3(Web3.RPCProvider())

auction_contract = web3.eth.contract(AUCTION_ADDRESS, abi=auction_abi)
wallet_abi = web3.eth.contract(WALLET_ADDRESS, abi=wallet_abi)


def fetch_bids():
    """Get all bid events and return them as a dataframe."""
    # get bid events
    log_filter = auction_contract.on('BidSubmission', {'fromBlock': CONTRACT_CREATION_BLOCK})
    events = log_filter.get(only_changes=False)
    df = pd.DataFrame({
        'amount': [from_wei(event['args']['_amount'], 'ether') for event in events],
        'missing': [from_wei(event['args']['_missing_funds'], 'ether') for event in events],
        'sender': [event['args']['_sender'] for event in events],
        'block': [event['blockNumber'] for event in events],
        'txhash': [event['transactionHash'] for event in events]
    })

    # get start time of auction
    log_filter = auction_contract.on('AuctionStarted', {'fromBlock': CONTRACT_CREATION_BLOCK})
    start_events = log_filter.get(only_changes=False)
    assert len(start_events) == 1
    start_time = start_events[0]['args']['_start_time']

    # get bid times
    blocks = df['block'].unique()
    timestamps = []
    for block_number in blocks:
        block = web3.eth.getBlock(int(block_number))
        timestamps.append(block['timestamp'] - start_time)
    timestamp_df = pd.DataFrame({'block': blocks, 'time': timestamps})
    merged = pd.merge(df, timestamp_df, on='block')

    # sort by time and return
    sorted = merged.sort_values('time')
    return sorted


def fetch_transactions(bids):
    txs = []
    hashes = bids['txhash'].unique()
    for hash_ in hashes:
        tx = dict(web3.eth.getTransaction(hash_))
        tx['value'] = from_wei(tx['value'], 'ether')
        txs.append(tx)
    keys = txs[0].keys()
    d = {key: [tx[key] for tx in txs] for key in txs[0].keys()}
    return pd.DataFrame(d)


if __name__ == '__main__':
    bids = fetch_bids()
    txs = fetch_transactions(bids)
    bids.to_csv(BID_OUTPUT_FILENAME)
    txs.to_csv(TX_OUTPUT_FILENAME)
