# -*- coding: utf-8 -*-

from datetime import datetime as dt
import pandas as pd
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import plotly

pd.options.plotting.backend = "plotly"
# external_stylesheets = ['.stylesheet.css']
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Create your connection.
db_path = '../sensorsData.db'
conn = sqlite3.connect(db_path)
table_name = 'Raspberry_data'

df = pd.read_sql_query(f"SELECT * FROM {table_name} ;", conn)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.set_index("timestamp")

min_date = df.index.min() - pd.to_timedelta(48, unit="h")
max_date = df.index.max()

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='Dashboard Raspberry', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    dcc.Tabs([
        dcc.Tab(label='Time Series plot', children=[
            dcc.Graph(id='series_plot', figure=df.plot(kind='scatter'))#, subplots=True, shape=(3,1), shared_xaxes=True, fill=True, asFigure=True))#figure=df.iplot(kind='scatter', subplots=True, fill=True, asFigure=True))
        ]),
        dcc.Tab(label='Scatter plot', children=[
            dcc.Graph(
                    id='scatter_plot',
                    figure=df.plot(kind='scatter')#, mode="markers", asFigure=True) # scatter_matrix(asFigure=True)
                    # figure={
                    #     'data': [
                    #         dict(
                    #             x=df[col],
                    #             y=df["temp"],
                    #             text=col,
                    #             mode='markers',
                    #             opacity=0.7,
                    #             marker={
                    #                 'size': 15,
                    #                 'line': {'width': 0.5, 'color': 'white'}
                    #             },
                    #             name=col
                    #         ) for col in ["cpu", "ram"]],
                    #     'layout': dict(
                    #         # xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                    #         yaxis={'title': 'CPU temperature'},
                    #         #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    #         #legend={'x': 0, 'y': 1},
                    #         hovermode='closest'
                    #     )
                    # }
                )
        ]),
        dcc.Tab(label='Summary', children=[
            generate_table(df.describe())
        ]),
    ]),
    
        # input
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=min_date.to_pydatetime(),
        max_date_allowed=max_date.to_pydatetime(),
        initial_visible_month=min(pd.to_datetime("today"), max_date),# - pd.to_timedelta(48, unit="h"),
        # end_date=pd.to_datetime("today").to_pydatetime(),
        minimum_nights=0
    ),


    # html.Footer(children=dcc.Markdown(children="made with <3 with COVID 19", style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }))
])

@app.callback(
    [dash.dependencies.Output('series_plot', 'figure'),
    dash.dependencies.Output('scatter_plot', 'figure')],
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_figure(start_date, end_date):

    if start_date is None:
        start_date = max_date - pd.to_timedelta(48, unit="h")
    if end_date is None:
        end_date = max_date

    end_date = pd.to_datetime(pd.to_datetime(end_date).date()) + pd.to_timedelta(1, unit="d")

    filtered_df = df.loc[(df.index < end_date) & (df.index >= start_date)]
    
    #https://community.plot.ly/t/dash-cufflinks/19662/4
    return filtered_df.plot(), filtered_df.plot(kind='scatter')#, subplots=True, shape=(4,1), shared_xaxes=True, fill=True, asFigure=True), filtered_df.iplot(kind='scatter', mode="markers", asFigure=True)
    # {'data': [
    #     dict(
    #         x=df[col],
    #         y=df["temp"],
    #         text=col,
    #         mode='markers',
    #         opacity=0.7,
    #         marker={
    #             'size': 15,
    #             'line': {'width': 0.5, 'color': 'white'}
    #         },
    #         name=col
    #         ) for col in ["cpu", "ram"]],
    #     'layout': dict(
    #         # xaxis={'type': 'log', 'title': 'GDP Per Capita'},
    #         yaxis={'title': 'CPU temperature'},
    #         #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
    #         #legend={'x': 0, 'y': 1},
    #         hovermode='closest'
    #     )
    # }  #, hovermode="closest")

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")