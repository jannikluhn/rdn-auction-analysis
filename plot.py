import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

mpl.rcParams.update({'font.size': 14})


BID_FILENAME = 'bids.csv'
TX_FILENAME = 'txs.csv'
RECEIPT_FILENAME = 'receipts.csv'


def plot_cum_bids(ax, bids):
    time = bids['time']
    bid_amount = bids['amount']
    cum_bid_amount = np.cumsum(bid_amount)
    cum_bid_number = np.arange(len(bids))

    time_scale = 1 / (60 * 60)
    bid_scale = 1 / 1000
    ax.fill_between(time * time_scale, 0, cum_bid_amount * bid_scale, step='pre')
    ax2 = ax.twinx()
    ax2.plot(time * time_scale, cum_bid_number, color='C1')

    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Bid amount [kETH]')
    ax.set_xlim(0, time.iloc[-1] * time_scale)
    ax.set_ylim(0, cum_bid_amount.iloc[-1] * bid_scale)

    ax2.set_ylim(0, len(bids))
    ax2.set_ylabel('Number of bids')


def plot_bid_dist(ax, bids):
    """Number of bids in bid value range."""
    amount_by_sender = bids[['sender', 'amount']].groupby('sender').sum()
    bins = np.concatenate([[0], 10.**np.arange(-2, 4) * 2.5, [np.inf]])
    bid_amount_groups = amount_by_sender.groupby(pd.cut(amount_by_sender['amount'], bins))
    bidders_per_bin = bid_amount_groups.size()
    contribution_per_bin = bid_amount_groups['amount'].sum() / bids['amount'].sum() * 100

    spacing = 0.2
    center = 0.5 + (1 + spacing) * np.arange(len(bins) - 1)
    ax.bar(center - 0.5, bidders_per_bin, width=0.5, align='edge', color='C0')
    ax2 = ax.twinx()
    ax2.bar(center, contribution_per_bin, width=0.5, align='edge', color='C1')

    ax.set_xticks(center)
    ax.set_xticklabels(['{} - {}'.format(lower, upper)
                        for lower, upper in zip(bins[:-1], bins[1:-1])])

    ax.set_xlabel('Bidded amount [ETH]')
    ax.set_ylabel('Number of bids')
    ax2.set_ylabel('Total contributed amount [%]')

def calc_autocorrelation(bids):
    time_bin_size = 60  # 1 minute
    bids['time_bin'] = bids['time'] // 60

    bids_per_bin = bids.groupby('time_bin').size()
    time_bins = np.arange(0, bids_per_bin.index[-1] + 1)
    bids_per_bin = bids_per_bin.reindex(time_bins, fill_value=0)

    tao = np.arange(1, 120)  # 2 hours
    gamma = np.zeros(tao.shape)
    for i in range(len(tao)):
        for time_bin in time_bins[:-tao[-1]]:
            gamma[i] += bids_per_bin[time_bin] * bids_per_bin[time_bin + tao[i]]

    return tao, gamma


def plot_corr(ax, bids):
    tao1, gamma1 = calc_autocorrelation(bids[bids.time <= np.median(bids.time)])
    tao2, gamma2 = calc_autocorrelation(bids[bids.time > np.median(bids.time)])
    
    ax2 = ax.twinx()
    ax2.plot(tao2, gamma2, color='C1')
    ax.plot(tao1, gamma1, color='C0')

    ax.set_xlabel('Time delta [min]')
    ax.set_ylabel('Autocorrelation first half [a.u.]')
    ax2.set_ylabel('Autocorrelation second half [a.u.]')


def print_summary(bids):
    total_amount = bids['amount'].sum()
    amount_by_sender = bids[['sender', 'amount']].groupby('sender').sum()
    median_contribution = amount_by_sender.median()
    average_contribution = amount_by_sender.mean()
    largest_bids = amount_by_sender.sort_values('amount', ascending=False).iloc[:10]
    print('total: {}'.format(total_amount))
    print('median contrib: {}'.format(median_contribution))
    print('avg contrib: {}'.format(average_contribution))
    print('largest bids: {}'.format(largest_bids))


def plot_lorenz(ax, bids):
    total_amount = bids['amount'].sum()
    bidders = bids[['sender', 'amount']].groupby('sender').sum()
    bidders['percentage'] = bidders['amount'] / bidders['amount'].sum()
    bidders = bidders.sort_values('percentage')

    lorenz_x = np.arange(len(bidders)) / len(bidders)
    lorenz_y = np.cumsum(bidders['percentage'])
    ax.plot(lorenz_x, lorenz_y)

    non_kyc_contrib = bidders[bidders['amount'] <= 2.5]['amount'].sum() / total_amount
    top_10_percent = bidders.iloc[-int(round(len(bidders) / 10)):]
    top_10_percent_contrib = top_10_percent['amount'].sum() / total_amount
    gini = (1 / len(bidders) * lorenz_y).sum() * 2
    #gini = (1 / len(bidders) * np.linspace(0, 1, len(bidders))).sum() * 2

    print('non KYC contribution: {}%'.format(non_kyc_contrib * 100))
    print('top 10% contribution: {}%'.format(top_10_percent_contrib * 100))
    print('Gini coefficient: {}%'.format(gini * 100))



def plot_failed(ax, txs, receipts):
    merged = pd.merge(txs, receipts, left_index=True, right_index=True)
    failure_details = merged[['gasUsed', 'gas', 'status', 'input', 'value']]

    passed = failure_details['status'] == 1
    failed = failure_details['status'] == 0
    zero_bid = failed & (failure_details['value'] == 0)
    low_gas = (failed &
               (failure_details['gas'] < 65000) &
               (failure_details['gas'] == failure_details['gasUsed']))
    other = failed & ~zero_bid & ~low_gas

    ax.pie(
        [sum(passed), sum(zero_bid), sum(low_gas), sum(other)],
        labels=['passed', 'zero bid', 'low gas', 'other'],
        colors=['darkgreen', 'tomato', 'maroon', 'tomato']
    )
    ax.axis('equal')

def plot_learning_bidders(ax, bids, txs, receipts):
    merged = pd.merge(txs, receipts, left_index=True, right_index=True)
    failing_tx_hashes = merged[merged['status'] == 0].index
    failing_bidders = set(merged.loc[failing_tx_hashes]['from'].unique())
    succeeding_bidders = set(bids['sender'].unique())
    forever_failing = failing_bidders - succeeding_bidders
    import pudb.b

def plot_cum_hist(ax, bids):
    bidders = bids[['sender', 'amount']].groupby('sender').sum()
    import pudb.b
    hist, bin_edges = np.histogram(bidders['amount'], bins=100)
    width = np.diff(bin_edges)
    ax.bar(bin_edges[:-1], hist, width=width, bottom=0.001)
    #ax.plot(bin_edges[:-1], np.cumsum(bidders.sort_values('amount')['amount']))
    ax2 = ax.twinx()
    ax2.plot(bin_edges[:-1], np.cumsum(bin_edges[:-1] * hist), color='C1')
    ax.set_yscale('log')

if __name__ == '__main__':
    bids = pd.DataFrame.from_csv(BID_FILENAME)
    txs = pd.DataFrame.from_csv(TX_FILENAME).set_index('hash')
    receipts = pd.DataFrame.from_csv(RECEIPT_FILENAME).set_index('transactionHash')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot_cum_bids(ax, bids)
    # plot_bid_dist(ax, bids)
    # plot_corr(ax, bids)
    # plot_failed(ax, txs, receipts)
    # plot_learning_bidders(ax, bids, txs, receipts)
    # print_summary(bids)
    # plot_lorenz(ax, bids)
    plot_cum_hist(ax, bids)
    plt.show()
