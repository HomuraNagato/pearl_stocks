
'''
for displaying plots in Opened VcXsrv
export DISPLAY=localhost:0.0
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


if __name__ == '__main__':

    path = 'robinhood_watchlist.csv'
    #S2 = reload_data()
    #S2.to_csv(path, index=False)
    
    S2 = pd.read_csv(path)
    print(S2.head())


