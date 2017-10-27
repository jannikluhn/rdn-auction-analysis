import numpy as np
import pandas as pd
from plotly import tools as plotly_tools
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
from eth_utils import denoms


START_TIME = pd.to_datetime(1508341187, unit='s')


def fig_avg(bids):
    data = [go.Scatter(
        x=bids['time'],
        y=bids['cum_amount'] / (bids['time_rel'].dt.total_seconds() / 60 / 60)
    )]
    layout = go.Layout(
        title='RDN auction',
        yaxis=dict(
            title='Average bid amount per hour [ETH]'
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


# def fig_repeated(bids, bidders):
#     repeated_bidders = bidders[bidders['n_bids'] > 1]
#     bids = bids[bids['sender'].isin(repeated_bidders.index)]
#     sorted = bids.sort_values('sender')
#     fig = ff.create_facet_grid(
#         bids,
#         x='time',
#         y='amount',
#         facet_row='sender'
#     )
#     return fig


def fig_bids(bids, bidders):
    time_bins = pd.date_range(START_TIME, bids['time'].max(), freq='4h')
    relevant_bids = bids[bids['amount'] > 2.5]
    bins = pd.cut(relevant_bids['time'], time_bins)
    binned_bids = relevant_bids.groupby(bins)
    mean_bid_amount = binned_bids['amount'].median()
    data = [
        go.Scatter(
            x=bids['time'],
            y=bids['amount'],
            mode='markers',
            name='Bids'
        ),
        go.Scatter(
            x=bids['time'],
            y=bids['cum_amount'],
            name='Total amount',
            yaxis='y2'
        ),
        go.Scatter(
            x=time_bins,
            y=mean_bid_amount,
            name='mean bid amount',
            yaxis='y1'
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        yaxis={
            'title': 'Individual bid amount [ETH]',
            'type': 'log'
        },
        yaxis2={
            'side': 'right',
            'title': 'Cumulative amount [ETH]',
            'overlaying': 'y'
        }
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


def fig_rolling(bids):
    hour = (bids['time'] - pd.to_datetime(0)).dt.total_seconds() // 60 // 60
    hour = pd.to_datetime(hour, unit='h')
    hourly = bids.groupby(hour)['amount'].sum()

    volume = bids.groupby('time')['amount'].sum()
    rolling = volume.rolling('1d', center=False).sum()

    data = [
        go.Bar(
            x=hourly.index,
            y=hourly,
            name='hourly volume'
        ),
        go.Scatter(
            x=rolling.index,
            y=rolling,
            name='24h rolling sum'
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        yaxis={
            'title': 'Bid amount [ETH]',
        }
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


def fig_bid_hist(bidders):
    grouped = bidders.groupby(bidders['amount'] // 1)
    hist = grouped.size()
    total = bidders['amount'].sum()
    cumulative = grouped['amount'].sum().cumsum() / total
    data = [
        go.Bar(
            x=hist.index,
            y=hist,
            name='Bidder histogram'
        ),
        go.Scatter(
            x=cumulative.index,
            y=cumulative * 100,
            line={
                'shape': 'hv'
            }, 
            yaxis='y2',
            name='Cumulative contribution'
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        xaxis={
            'title': 'Bid amount [ETH]'
        },
        yaxis={
            'title': 'Number of bidders',
            'type': 'log'
        },
        yaxis2={
            'title': 'Cumulative bid amount [ETH]',
            'side': 'right',
            'overlaying': 'y',
            'ticksuffix': '%',
        }
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


def fig_lorenz(bidders):
    total_amount = bidders['amount'].sum()
    bidders = bidders.sort_values('percentage')

    lorenz_x = np.arange(len(bidders)) / len(bidders)
    lorenz_y = np.cumsum(bidders['percentage'])

    gini = 1 - 2 * (1 / len(bidders) * lorenz_y).sum()

    data = [
        go.Scatter(
            x=lorenz_x * 100,
            y=lorenz_y * 100,
            name='Lorenz curve',
            fill='tozeroy'
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        xaxis={
            'title': 'Percentage of bidders',
            'ticksuffix': '%'
        },
        yaxis={
            'title': 'Percentage of contribution',
            'ticksuffix': '%'
        },
        annotations=[{
            'x': 50,
            'y': 50,
            'text': 'Gini coefficient: {:0.1f}%'.format(gini * 100),
            'showarrow': False,
            'font': {
                'size': 14
            }
        }]
    )

    return go.Figure(data=data, layout=layout)

    # non_kyc_contrib = bidders[bidders['amount'] <= 2.5]['amount'].sum() / total_amount
    # top_10_percent = bidders.iloc[-int(round(len(bidders) / 10)):]
    # top_10_percent_contrib = top_10_percent['amount'].sum() / total_amount
    gini = (1 / len(bidders) * lorenz_y).sum() * 2
    # #gini = (1 / len(bidders) * np.linspace(0, 1, len(bidders))).sum() * 2

    # print('non KYC contribution: {}%'.format(non_kyc_contrib * 100))
    # print('top 10% contribution: {}%'.format(top_10_percent_contrib * 100))
    # print('Gini coefficient: {}%'.format(gini * 100))


def fig_gas_usage(bids, receipts):
    merged = pd.merge(bids, receipts, left_on='txhash', right_index=True)
    gas_used = merged.groupby('block')['gasUsed'].sum()
    data = [
        go.Bar(
            x=gas_used.index,
            y=gas_used
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        xaxis={
            'title': 'Block'
        },
        yaxis={
            'title': 'Gas usage'
        }
    )
    return go.Figure(data=data, layout=layout)


def fig_gas_prices(txs):
    hist_price = txs.groupby(txs['gasPrice'] // denoms.gwei).size()
    hist_limit = txs.groupby(txs['gas'] // 1000).size()

    trace_price = go.Bar(
        x=hist_price.index,
        y=hist_price,
        xaxis='x1',
        yaxis='y1',
        name='Gas price'
    )
    trace_limit = go.Bar(
        x=hist_limit.index,
        y=hist_limit,
        xaxis='x2',
        yaxis='y2',
        name='Gas limit'
    )
    fig = plotly_tools.make_subplots(rows=1, cols=2)
    fig.append_trace(trace_price, 1, 1)
    fig.append_trace(trace_limit, 1, 2)
    fig['layout']['title'] = 'RDN auction'
    fig['layout']['xaxis1']['title'] = 'Gas price [GWei]'
    fig['layout']['xaxis2']['title'] = 'Gas limit [k]'
    fig['layout']['yaxis1']['title'] = 'Number of bids'
    fig['layout']['yaxis2']['title'] = 'Number of bids'
    fig['layout']['yaxis2']['side'] = 'right'
    return fig


def fig_fits(bids):
    outlier_bound = 500
    bids = bids[bids['amount'] < outlier_bound]
    cum_amount = bids['amount'].cumsum()
    data = [
        go.Scatter(
            x=bids['time'],
            y=cum_amount
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        xaxis={
            'title': 'Block'
        },
        yaxis={
            'title': 'Gas usage'
        }
    )
    return go.Figure(data=data, layout=layout)



if __name__ == '__main__':
    bids = pd.DataFrame.from_csv('bids.csv')
    receipts = pd.DataFrame.from_csv('receipts.csv')
    txs = pd.DataFrame.from_csv('txs.csv')

    bids['time_rel'] = pd.to_timedelta(bids['time'], unit='s')
    bids['time'] = pd.to_datetime(bids['time'], origin=START_TIME, unit='s')
    bids['cum_amount'] = bids['amount'].cumsum()

    bidders = bids.groupby('sender')['amount'].sum()
    bidders = pd.DataFrame({}, index=bids['sender'].unique())
    bidders['amount'] = bids.groupby('sender')['amount'].sum()
    bidders['percentage'] = bidders['amount'] / bidders['amount'].sum()
    bidders['n_bids'] = bids['sender'].value_counts()

    # py.plot(fig_avg(bids), filename='RDN average')
    # py.plot(fig_bids(bids, bidders), filename='RDN bids')
    # py.plot(fig_rolling(bids), filename='RDN rolling')
    py.plot(fig_bid_hist(bidders), filename='RDN bid hist')
    # # py.plot(fig_repeated(bids, bidders), filename='RDN repeated bidders')
    # py.plot(fig_lorenz(bidders), filename='RDN lorenz')
    # py.plot(fig_gas_usage(bids, receipts), filename='RDN gas usage')
    # py.plot(fig_gas_prices(txs), filename='RDN gas prices')
    # # py.plot(fig_fits(bids), filename='RDN fits')
