import pandas as pd
from web3 import Web3


if __name__ == '__main__':
    web3 = Web3(Web3.RPCProvider())
    bids = pd.DataFrame.from_csv('bids.csv')
    senders = bids['sender'].unique()
    codes = [web3.eth.getCode(sender) for sender in senders]
    n_external = codes.count('0x')
    print('Total bidders: {}'.format(len(senders)))
    print('External accounts: {}'.format(n_external))
