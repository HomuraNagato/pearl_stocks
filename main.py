#!/usr/bin/env python3

'''
export FLASK_APP=main.py
export FLASK_ENV=development
start server with flask run

Flask app to connect to robinhood for visualizing and predicting stocks
to buy/sell

references
robinhood api
  https://github.com/joshfraser/robinhood-to-csv
  https://github.com/sanko/Robinhood/blob/master/Watchlist.md

plotly type
  https://towardsdatascience.com/getting-started-with-plot-ly-3c73706a837c


'''

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json

from programs import gran_postgres

server = Flask(__name__)

def create_scatter(df, x_axis, y_axis, text_axis, color_axis):

    fig = go.Figure()

    df = df[df[color_axis] == 2015]
    
    data = [
        go.Scatter(
            x=df[x_axis], 
            y=df[y_axis],
            mode='markers',
            name='markers',
            text=df[text_axis]
        )
    ]

    layout = go.Layout(
        title = 'Scatter Relationship',
        yaxis = {'title': y_axis},
        xaxis = {'title': x_axis},
    )

    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_line_chart(df, x_axis, y_axis, text_axis, group_axis):

    fig = go.Figure()

    # columns: date, close_price, symbol, simple_name

    data = []
    count = 0
    for group in df[group_axis].unique():
        
        df_sub = df[df[group_axis] == group]

        # cut clutter by only displaying four items at start
        if count < 4:
            visible = True
        else:
            visible = 'legendonly'
        
        data.append(go.Scatter(
            x = df_sub[x_axis], 
            y = df_sub[y_axis],
            visible=visible,
            mode = 'lines',
            name = group,

        ))
        count += 1
    
    
    layout = go.Layout(
        title = 'Robinhood lineplot',
        showlegend = True,
        yaxis = {'title': y_axis},
        xaxis = {'title': x_axis},
        template='plotly_dark'
    )
    
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    
def create_table(df, columns):

    fig = go.Figure()

    data = [
        go.Table(
            header=dict(values= columns,
                    fill_color= '#778899',
                    align= 'left'),
            cells=dict(values= [ df[x] for x in columns ],
                    fill_color= '#303030',
                    align= 'left'),
            )
        ]

    layout = go.Layout(
        title = 'Robinhood Stocks Watchlist table',
        template='plotly_dark'
        #width = 900,
        #margin = { 'l': 20, 'r': 20, 't': 20, 'b': 20, 'pad': 10 },
        #autosize = True
    )
    
    fig = dict(data=data, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@server.route('/')
def index():

    # get df of stocks
    artifact = gran_postgres.StockConn()
    S2 = artifact.get_stocks_df()
    columns = S2.columns

    # create table
    table = create_table(S2, columns)

    # create line graph
    x_axis, y_axis, group_axis = 'date', 'close_price', 'symbol'
    linechart = create_line_chart(S2, x_axis, y_axis, y_axis, group_axis)

    return render_template('index.html', table=table, linechart=linechart)


@server.route('/table', methods=['GET', 'POST'])
def filter_table():

    # get environmental variables
    asin = request.args['asin']
    action = request.args['action']
    print("entered filter table in main")
    artifact = Amazon(asin=asin, action=action)
    
    if action == "add":
        try:
            asin_request(artifact)
            print("asin", asin, "added to database")
        except:
            print("Unable to collect asin", asin, "from Amazon")

    elif action == "delete":
        try:
            artifact.delete_sql()
        except:
            print("Unable to delete asin", asin, "from postgres database")
    
    S2 = artifact.view_database()
    columns = S2.columns
    
    if action == "filter":
        S2 = S2[S2['asin'] == asin]

    graphJSON = create_table(S2, columns)

    return graphJSON



if __name__ == '__main__':
    server.run(debug=True)
