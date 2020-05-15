
'''
for saving image, required packages:
  npm install -g electron@1.8.4 orca
  pip install psutil
'''

import pandas as pd
import numpy as np
import matplotlib
import plotly
import plotly.graph_objects as go

from programs import gran_postgres

def reload_data():
    artifact = gran_postgres.StockConn()
    S2 = artifact.get_stocks_df()
    return S2

def technical_indicators(S2, symbol):

    S2 = S2[S2['symbol'] == symbol]

    # add 7 and 21 day moving average
    S2['ma7'] = S2['close_price'].rolling(window=7).mean()
    S2['ma21'] = S2['close_price'].rolling(window=21).mean()

    return S2

def show_stock(S2, x_axis, y_axes, symbol):

    S3 = S2[S2['symbol'] == symbol]

    fig = go.Figure()

    for y_axis in y_axes:
        fig.add_trace(go.Scatter(
            x = S3[x_axis], 
            y = S3[y_axis],
            visible=True,
            mode = 'lines',
            name = symbol + ' ' + y_axis,
        ))

    fig.update_layout(
        title = 'Robinhood lineplot',
        showlegend = True,
        yaxis = {'title': y_axes[0]},
        xaxis = {'title': x_axis},
        template='plotly_dark'
    )
    
    fig.show()

if __name__ == '__main__':

    path = 'robinhood_watchlist.csv'
    #S2 = reload_data()
    #S2.to_csv(path, index=False)
    
    S2 = pd.read_csv(path)
    #print(S2.head())

    symbol = 'TSLA'
    S3 = technical_indicators(S2, symbol)

    x_axis, group_axis = 'date', 'symbol'
    y_axes = ['close_price', 'ma7', 'ma21']
    show_stock(S3, x_axis, y_axes, symbol)
