import pandas as pd

if __name__ == '__main__':
    bids = pd.DataFrame.from_csv('bids.csv')
    bidders = bids.groupby('sender')['amount'].sum()

    total_raised = bids['amount'].sum()
    unique_participants = len(bids['sender'].unique())
    above_kyc_limit = len(bidders[bidders > 2.5])
    newest_bid = pd.to_datetime(1508341187 + max(bids['time']), unit='s')

    print('total raised: {} ETH'.format(total_raised))
    print('unique participants: {}'.format(unique_participants))
    print('bid > 2.5: {}'.format(above_kyc_limit))
    print('newest analyzed bid: {}'.format(newest_bid))
