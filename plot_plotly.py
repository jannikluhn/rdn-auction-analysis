import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

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


def fig_bids(bids):
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
    hist = bidders.groupby(bidders // 1).count()
    data = [
        go.Bar(
            x=hist.index,
            y=hist
        )
    ]
    layout = go.Layout(
        title='RDN auction',
        yaxis={
            'title': 'Number of bidders'
        },
        xaxis={
            'title': 'Bid amount [ETH]'
        }
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    bids = pd.DataFrame.from_csv('bids.csv')
    bids['time_rel'] = pd.to_timedelta(bids['time'], unit='s')
    bids['time'] = pd.to_datetime(bids['time'], origin=START_TIME, unit='s')
    bids['cum_amount'] = bids['amount'].cumsum()

    bidders = bids.groupby('sender')['amount'].sum()

    # py.plot(fig_avg(bids))
    # py.plot(fig_bids(bids))
    py.plot(fig_rolling(bids))
    # py.plot(fig_bid_hist(bidders))
