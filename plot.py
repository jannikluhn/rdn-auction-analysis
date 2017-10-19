import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

mpl.rcParams.update({'font.size': 14})


BID_FILENAME = 'bids.csv'


def plot_cum_bids(ax, bids):
    time = bids['time']
    bid_amount = bids['amount']
    cum_bid_amount = np.cumsum(bid_amount)

    time_scale = 1 / (60 * 60)
    bid_scale = 1 / 1000
    ax.fill_between(time * time_scale, 0, cum_bid_amount * bid_scale, step='pre')

    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Bidded amount [kETH]')
    ax.set_xlim(0, time.iloc[-1] * time_scale)
    ax.set_ylim(0, cum_bid_amount.iloc[-1] * bid_scale)


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



if __name__ == '__main__':
    bids = pd.DataFrame.from_csv(BID_FILENAME)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot_cum_bids(ax, bids)
    # plot_bid_dist(ax, bids)
    plot_corr(ax, bids)
    plt.show()
