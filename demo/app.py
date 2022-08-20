import argparse
import pprint
import random
from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dash_table
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from futubot.indicators import Indicators
from futubot.robot import Robot
from utils.config import Config


def parse_args():
    parser = argparse.ArgumentParser(description='Run FutuBot')
    parser.add_argument('config', help='config file path')
    parser.add_argument('--display-all-cols',
                        action='store_true',
                        help='whether to display all columns of stockframe.')
    args = parser.parse_args()

    return args


args = parse_args()

cfg_dict = Config.parse_config(cfg_pth=args.config)
pprint.pprint(cfg_dict)

if args.display_all_cols:
    pd.set_option('display.max_columns', None)

futubot = Robot(**cfg_dict['account'])

portfolio = futubot.create_portfolio(
    stocks_of_interest=cfg_dict['stocks_of_interest'])
pprint.pprint(portfolio.positions)

start_date = cfg_dict['historical_quote_dates']['start_date']
end_date = cfg_dict['historical_quote_dates']['end_date']

i = 0

historical_quotes = futubot.get_historical_quotes(
    **cfg_dict['historical_quote_dates'], )

stockframe = futubot.create_stockframe(data=historical_quotes)

indicator_client = Indicators(stockframe=stockframe)
indicator_client.rsi()
indicator_client.sma()
indicator_client.ema()
indicator_client.macd()
indicator_client.bollinger_bands()
indicator_client.standard_deviation()
indicator_client.stochastic_oscillator()

colors = {'background': '#000000', 'text': '#ffFFFF'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    html.Div(
        [dcc.Interval(id='interval-component', interval=6000, n_intervals=0)]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='code_names',
                             options=[{
                                 'label': code,
                                 'value': code,
                             } for code in portfolio.positions.keys()],
                             searchable=True,
                             value=random.choice(
                                 list(portfolio.positions.keys())),
                             placeholder='Code',
                             style={
                                 'backgroundColor': 'rgba(0, 0, 0, 0)',
                                 'margin-left': '0.5em'
                             }),
                width={
                    'size': 3,
                    'offset': 0
                }),
        dbc.Col(dcc.Dropdown(id='indicator_names',
                             options=[
                                 {
                                     'label': 'Candlestick',
                                     'value': 'Candlestick'
                                 },
                                 {
                                     'label': 'Volume',
                                     'value': 'Volume'
                                 },
                             ] + [{
                                 'label': current_indicator.upper(),
                                 'value': current_indicator.upper()
                             } for current_indicator in list(
                                 indicator_client.current_indicators.keys())],
                             value='Candlestick',
                             placeholder='Indicator',
                             style={'backgroundColor': 'rgba(0, 0, 0, 0)'}),
                width={'size': 3})
    ]),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                [dbc.Card([dbc.CardBody([
                    dcc.Graph(id='live_graph'),
                ])])],
                width={'size': 9},
            ),
            dbc.Col(
                [
                    dbc.Card([dbc.CardBody([
                        dcc.Graph(id='portfolio_fig'),
                    ])]),
                ],
                width={'size': 3},
            )
        ],
        className='g-0',
    ),
    dbc.Row(
        [
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6('Intraday Trading Activity',
                                className='text-left'),
                        html.Div(
                            id='trading_activity_table',
                            children=[],
                        ),
                    ]),
                ])
            ],
                    width={'size': 9},
                    style={
                        'height': '450px',
                        'overflow': 'scroll'
                    }),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6('Portfolio Distribution',
                                className='text-center'),
                        dcc.Graph(id='portfolio_chart')
                    ])
                ])
            ],
                    width={'size': 3})
        ],
        className='g-0',
    )
])


def generate_trading_activiy_table():
    """Generate trading activity table.

    This function calls the Futu API order_list_query()
    to get all the orders of today and then generate a
    table of trading activity.

    Returns:
        (dash_table.DataTable): A dash datatable with columns
            'order_id', 'code', 'stock_name', 'trd_side',
            'order_type', 'qty', 'order_status', 'price',
            'currency', 'create_time', 'updated_time'.
    """
    today_order_info = futubot.check_today_orders()

    if today_order_info is None:
        return [
            dash_table.DataTable(
                id='table',
                columns=[{
                    'name': i,
                    'id': i
                } for i in [
                    'order_id', 'code', 'stock_name', 'trd_side', 'order_type',
                    'qty', 'order_status', 'price', 'currency', 'create_time',
                    'updated_time'
                ]],
                style_table={
                    'height': 'auto',
                    'overflowX': 'scroll'
                },
                style_cell={
                    'white_space': 'normal',
                    'height': 'auto',
                    'backgroundColor': 'rgba(0, 0, 0, 0)',
                    'color': 'white',
                    'font_size': '13px',
                    'font-family': 'Arial'
                },
                style_header={
                    'backgroundColor': 'rgba(0, 0, 0, 0)',
                    'fontWeight': 'bold',
                    'border': '#4d4d4d',
                    'font_size': '16px',
                },
                style_cell_conditional=[{
                    'if': {
                        'column_id': c
                    },
                    'textAlign': 'right'
                } for c in ['attribute', 'value']],
                style_as_list_view=True,
            )
        ]

    return [
        dash_table.DataTable(
            id='table',
            columns=[{
                'name': i,
                'id': i
            } for i in today_order_info.columns],
            data=today_order_info.to_dict('records'),
            # style_table={"maxheight": "10", "overflowY": "scroll"},
            # css=[{"selector": ".dash-table-container tr",
            #  "rule":'max-height: "5px"; height: "5px"; '}],
            # fixed_rows={ 'headers': True, 'data': 0 },
            style_cell={
                'white_space': 'normal',
                'height': 'auto',
                'backgroundColor': 'rgba(0, 0, 0, 0)',
                'color': 'white',
                'font_size': '13px',
                'font-family': 'Arial'
            },
            style_header={
                'backgroundColor': 'rgba(0, 0, 0, 0)',
                'fontWeight': 'bold',
                'border': '#4d4d4d',
                'font_size': '16px',
            },
            style_cell_conditional=[{
                'if': {
                    'column_id': c
                },
                'textAlign': 'right'
            } for c in ['attribute', 'value']],
            style_data_conditional=[{
                'if': {
                    'filter_query':
                    '{order_status} = "CANCELLED_ALL" || {order_status} = "UNSUBMITTED" \
                || {order_status} = "SUBMIT_FAILED" \
                    || {order_status} = "FAILED" \
                        || {order_status} = "DELETED"',
                    'column_id': 'order_status'
                },
                'color': 'red'
            }, {
                'if': {
                    'filter_query': '{order_status} = "SUBMITTED" \
                         || {order_status} = "SUBMITTING"',
                    'column_id': 'order_status'
                },
                'color': 'rgb(255, 255, 51)'
            }, {
                'if': {
                    'filter_query': '{order_status} = "FILLED_ALL"',
                    'column_id': 'order_status'
                },
                'color': '#16ff32'
            }],
            style_as_list_view=True,
        )
    ]


@app.callback([Output('trading_activity_table', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_trading_activity_table(n_interval):
    """Update the trading activity table in real time.

    This function updates the trading activity table by
    calling generate_trading_activity_table() when the
    interval-component fires a callback periodically.

    Args:
        n_interval (int): The number of times the interval
            has passed. It is incremented by dcc.Interval with
            id 'interval-component' at every interval milliseconds
            in order to update the app in real time. For demo mode,
            the 'interval' is set to 6000 milliseconds.

    Returns:
        (dash_table.DataTable): A dash datatable with id
            'trading_activity_table'.
    """
    return generate_trading_activiy_table()


@app.callback([Output('portfolio_chart', 'figure')],
              [Input('interval-component', 'n_intervals')])
def update_portfolio_chart(n_interval):
    """Update the portfolio pie chart in real time.

    This function updates the portfolio distribution pie
    chart by calling calculate_portfolio_weights() when the
    interval-component fires a callback periodically.

    Args:
        n_interval (int): The number of times the interval
            has passed. It is incremented by dcc.Interval with
            id 'interval-component' at every interval milliseconds
            in order to update the app in real time. For demo mode,
            the 'interval' is set to 6000 milliseconds.

    Returns:
        (plotly.graph_objects.Pie): A Plotly pie chart of
            portfolio distribution with id 'portfolio_chart'.
    """
    weights = portfolio.calculate_portfolio_weights()

    portfolio_chart = go.Figure()
    portfolio_chart.add_trace(
        go.Pie(labels=list(weights.keys()), values=list(weights.values())))
    portfolio_chart.update_traces(hole=.7, hoverinfo='label+percent')
    portfolio_chart.update_traces(textposition='outside',
                                  textinfo='label+percent')
    portfolio_chart.update_layout(showlegend=False)
    portfolio_chart.update_layout(height=400,
                                  plot_bgcolor='rgba(0, 0, 0, 0)',
                                  paper_bgcolor='rgba(0, 0, 0, 0)',
                                  font={'color': colors['text']},
                                  margin=go.layout.Margin(l=50,
                                                          r=50,
                                                          b=50,
                                                          t=50))

    return [portfolio_chart]


@app.callback([Output('portfolio_fig', 'figure')],
              [Input('interval-component', 'n_intervals')])
def update_portfolio(n_intervals):
    """Update the portfolio information figure in real time.

    This function calls get_protfolio_info() when the
    interval-component fires a callback periodically and updates
    the Plotly Indicator figure of total assets. The percentage
    difference between the total assets and total invested value
    is also updated in real time.

    Args:
        n_interval (int): The number of times the interval
            has passed. It is incremented by dcc.Interval with
            id 'interval-component' at every interval milliseconds
            in order to update the app in real time. For demo mode,
            the 'interval' is set to 6000 milliseconds.

    Returns:
        (plotly.graph_objects.Indicator): A Plotly Indicator of
            portfolio's total assets, with percentage reference
            'total_invested_value'.
    """
    portfolio_fig = go.Figure()

    portfolio_info = portfolio.portfolio_info

    # today_pnl_value = portfolio_info["today_pnl_value"]

    total_assets = portfolio_info['total_assets']
    total_invested_value = portfolio_info['total_invested_value']

    portfolio_fig.add_trace(
        go.Indicator(mode='number+delta',
                     value=abs(total_assets),
                     number={
                         'prefix': '$ ',
                         'valueformat': 'f'
                     },
                     title={
                         'text':
                         "<br><span style='font-size:0.9em;"
                         "color:gray'>Total Assets</span>"
                     },
                     delta={
                         'position': 'bottom',
                         'reference': total_invested_value,
                         'relative': True,
                         'valueformat': '.3%'
                     },
                     domain={
                         'row': 0,
                         'column': 0
                     }))

    portfolio_fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font={'color': colors['text']},
    )

    return [portfolio_fig]


@app.callback([Output('live_graph', 'figure')], [
    Input('interval-component', 'n_intervals'),
    State('code_names', 'value'),
    State('indicator_names', 'value')
])
def run_futubot(n_intervals, code_name, indicator_name, start_date=start_date):
    """Implementation of FutuBot in real time.

    This function implements the main logic of FutuBot in real time
    by calculating buy and sell signals based on latest bar data and
    then places orders accordingly. It also updates StockFrame graphs
    in real time based on the input 'code_name' and 'indicators'. For
    demo mode, the real time is updated by an artificial counter 'i'
    which is incremented periodically by the interval-component callback.
    The live_graph has the following options:
        - Candlestick (default)
        - Volume
        - RSI
        - SMA
        - EMA
        - MACD
        - Bollinger Bands
        - Standard Deviation
        - Stochastic Oscillator

    Args:
        n_interval (int): The number of times the interval
            has passed. It is incremented by dcc.Interval with
            id 'interval-component' at every interval milliseconds
            in order to update the app in real time. For demo mode,
            the 'interval' is set to 6000 milliseconds.
        code_name (str): The name of code for which the live graph
            is plotted. Its value is controlled by the state of the
            dcc.Dropdown table with id 'code_names'.
        indicator (str): The name of indicator for which the live graph
            is plotted. Its value is controlled by the state of the
            dcc.Dropdown table with id 'indicators'.

    Returns:
        (plotly.graph_objects): A Plotly graph of StockFrame with id
            'live_graph'.
    """
    # Artificial counter for advancing time
    global i
    # print(i)

    df = stockframe.frame.loc[code_name]

    fig = go.Figure()

    end_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = end_date + i * timedelta(minutes=1)
    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

    print('holdings before', portfolio.holdings)

    latest_prices = futubot.get_latest_bar(start_date=start_date,
                                           end_date=end_date,
                                           demo=True)
    stockframe.add_rows(data=latest_prices)
    indicator_client.refresh()

    existing_orders = futubot.check_existing_orders(
        code_list=portfolio.holdings)
    print('existing_orders', existing_orders)

    StrategyClass = cfg_dict['strategy']['name']
    strategy_client = StrategyClass(stockframe, portfolio, indicator_client,
                                    existing_orders,
                                    **cfg_dict['strategy']['params'])
    buy_sell_signals = strategy_client.calculate_buy_sell_signals()

    order_infos = futubot.execute_signals(buy_sell_signals=buy_sell_signals)
    pprint.pprint(order_infos)

    portfolio.update_positions(order_infos=order_infos)

    print('holdings after', portfolio.holdings)

    fig.add_trace(trace=go.Candlestick(x=df.index,
                                       open=df['open'],
                                       high=df['high'],
                                       low=df['low'],
                                       close=df['close'],
                                       name='Close'))

    volume_colors = [
        '#16ff32' if row['open'] - row['close'] >= 0 else 'red'
        for _, row in df.iterrows()
    ]

    if indicator_name == 'Volume':
        fig = go.Figure(data=go.Bar(x=df.index,
                                    y=df['volume'],
                                    marker_color=volume_colors,
                                    name='Volume'))

    if indicator_name[:3] == 'RSI':
        fig = go.Figure(
            data=go.Scatter(x=df.index,
                            y=df[indicator_name.lower()],
                            name=indicator_name,
                            line=dict(color='rgb(255, 237, 111)', width=2)))
        fig.update_layout(yaxis_range=[0, 100])
        fig.add_hline(y=30.0,
                      line_width=1,
                      line_dash='dash',
                      annotation_text='Oversold Line',
                      line_color='#16ff32',
                      annotation_font_color='#16ff32')
        fig.add_hline(y=70.0,
                      line_width=1,
                      line_dash='dash',
                      annotation_text='Overbought Line',
                      line_color='#fb0d0d',
                      annotation_font_color='#fb0d0d')

    if indicator_name[:3] == 'SMA':
        fig.add_trace(trace=go.Scatter(
            x=df.index,
            y=df[indicator_name.lower()],
            name=indicator_name,
            line=dict(color='orange', width=2),
        ), )

    if indicator_name[:3] == 'EMA':
        fig.add_trace(trace=go.Scatter(
            x=df.index,
            y=df[indicator_name.lower()],
            name=indicator_name,
            line=dict(color='#2ed9ff', width=2),
        ), )

    if indicator_name == 'MACD':
        fig = go.Figure()
        macd_colors = [
            '#16ff32' if val >= 0 else 'red'
            for val in df.histogram.values.tolist()
        ]

        fig.add_trace(
            go.Bar(x=df.index,
                   y=df.histogram,
                   marker_color=macd_colors,
                   name='Histogram'))

        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df.macd,
                       line=dict(color='#ffa15a', width=2),
                       name='MACD'))

        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df.signal,
                       line=dict(color='#2ed9ff', width=2),
                       name='Signal'))

    if indicator_name == 'BOLLINGER_BANDS':
        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df['sma'],
                       line=dict(color='orange', width=2),
                       name='SMA'))

        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df['upper_band'],
                       line_color='#2ed9ff',
                       line={'dash': 'dash'},
                       name='Upper Band',
                       opacity=0.1))

        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df['lower_band'],
                       line_color='#2ed9ff',
                       line={'dash': 'dash'},
                       fill='tonexty',
                       name='Lower Band',
                       opacity=0.1))

    if indicator_name == 'STANDARD_DEVIATION':
        fig = go.Figure(
            go.Scatter(x=df.index,
                       y=df['standard_deviation'],
                       line=dict(color='rgb(102, 166, 30)', width=2),
                       name='Standard Deviation'))

    if indicator_name == 'STOCHASTIC_OSCILLATOR':
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df['%K'],
                       name='%K Line (Fast)',
                       line=dict(color='#af0038', width=2)))

        fig.add_trace(
            go.Scatter(x=df.index,
                       y=df['%D'],
                       name='%D Line (Slow)',
                       line=dict(color='rgb(29, 105, 150)', width=2)))

    fig.update_layout(
        height=400,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font={'color': colors['text']},
    )
    # Increment the counter by one every callback
    i += 1

    return [fig]


if __name__ == '__main__':
    app.run_server(port=8054)
