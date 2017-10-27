# Analysis scripts for the of RDN token auction

Steps to run:

  - `pip install -r requirements.txt`
  - configure plotly
  - create `addresses.py` defining `AUCTION_ADDRESS` and `WALLET_ADDRESS`
  - fetch bid events with `python fetch.py`
  - select things to plot by un/commenting corresponding lines in `plot_plotly.py`
  - create plots with `plot_plotly.py`
