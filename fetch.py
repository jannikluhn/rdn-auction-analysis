import os
import pandas as pd
from web3 import Web3
from eth_utils import from_wei, is_same_address
from abis import auction_abi, wallet_abi
from addresses import AUCTION_ADDRESS, WALLET_ADDRESS


BID_OUTPUT_FILENAME = 'bids.csv'
TX_OUTPUT_FILENAME = 'txs.csv'
RECEIPT_OUTPUT_FILENAME = 'receipts.csv'

CONTRACT_CREATION_BLOCK = 4383437


web3 = Web3(Web3.RPCProvider())

auction_contract = web3.eth.contract(AUCTION_ADDRESS, abi=auction_abi)
wallet_abi = web3.eth.contract(WALLET_ADDRESS, abi=wallet_abi)


def fetch_bids():
    """Get all bid events and return them as a dataframe."""
    block_range = {'fromBlock': CONTRACT_CREATION_BLOCK}
    # get bid events
    log_filter = auction_contract.on('BidSubmission', block_range)
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


# def fetch_txs(from_block, to_block):
#     block_range = {'fromBlock': from_block, 'toBlock': to_block}
#     block_numbers = range(from_block, to_block + 1)
#     txs = []
#     receipts = []
#     for block_number in block_numbers:
#         if (block_number - block_numbers[0]) % 10 == 0:
#             print('fetching blocks {} + 10'.format(block_number))
#         tx_count = web3.eth.getBlockTransactionCount(block_number)
#         for i in range(tx_count):
#             tx = dict(web3.eth.getTransactionFromBlock(block_number, i))
#             if not tx['to'] or not is_same_address(tx['to'], AUCTION_ADDRESS):
#                 continue
#             tx['value'] = from_wei(tx['value'], 'ether')
#             receipt = web3.eth.getTransactionReceipt(tx['hash'])
#             txs.append(tx)
#             receipts.append(receipt)
#     tx_df = pd.DataFrame({key: [tx[key] for tx in txs] for key in txs[0].keys()})
#     receipt_df = pd.DataFrame({key: [receipt[key]
#                                for receipt in receipts] for key in receipts[0].keys()})
#     return tx_df, receipt_df


if __name__ == '__main__':
    bids = fetch_bids()
    bids.to_csv(BID_OUTPUT_FILENAME)

    # to_block = web3.eth.blockNumber

    # if os.path.exists(BID_OUTPUT_FILENAME):
    #     old_bids = pd.DataFrame.from_csv(BID_OUTPUT_FILENAME)
    #     from_block = int(max(old_bids['block'] - 10))
    # else:
    #     old_bids = None
    #     from_block = CONTRACT_CREATION_BLOCK
    # print('fetching bids between {} and {}'.format(from_block, to_block))
    # bids = fetch_bids(from_block, to_block)
    # if old_bids is not None:
    #     bids = pd.concat([old_bids, bids], ignore_index=True)

    # if os.path.exists(TX_OUTPUT_FILENAME):
    #     old_txs = pd.DataFrame.from_csv(TX_OUTPUT_FILENAME)
    #     from_block = int(max(old_txs['blockNumber'] - 10))
    # else:
    #     old_txs = None
    #     from_block = CONTRACT_CREATION_BLOCK
    # if os.path.exists(RECEIPT_OUTPUT_FILENAME):
    #     old_receipts = pd.DataFrame.from_csv(RECEIPT_OUTPUT_FILENAME)
    #     from_block = min(from_block, int(max(old_receipts['blockNumber'] - 10)))
    # else:
    #     old_receipts = None
    #     from_block = CONTRACT_CREATION_BLOCK
    # print('fetching txs between {} and {}'.format(from_block, to_block))
    # txs, receipts = fetch_txs(from_block, to_block)
    # if old_txs is not None:
    #     txs = pd.concat([old_txs, txs], ignore_index=True)
    # if old_receipts is not None:
    #     receipts = pd.concat([old_receipts, receipts], ignore_index=True)
    # txs.to_csv(TX_OUTPUT_FILENAME)
    # receipts.to_csv(RECEIPT_OUTPUT_FILENAME)
    # print('done')
