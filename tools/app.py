import argparse
import pprint
import random

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
    parser.add_argument('--output-dir', help='the directory to save the logs')
    parser.add_argument('--display-all-col',
                        action='store_true',
                        help='whether to display all columns of stockframe.')
    args = parser.parse_args()

    return args


args = parse_args()

cfg_dict = Config.parse_config(cfg_pth=args.config)
pprint.pprint(cfg_dict)

if args.display_all_col:
    pd.set_option('display.max_columns', None)

trading_robot = Robot(**cfg_dict['account'])

portfolio = trading_robot.create_portfolio(
    stocks_of_interest=cfg_dict['stocks_of_interest'])
pprint.pprint(portfolio.positions)

historical_quotes = trading_robot.get_historical_quotes(
    **cfg_dict['historical_quote_dates'], )

stockframe = trading_robot.create_stockframe(data=historical_quotes)

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
        [dcc.Interval(id='interval-component', interval=10000,
                      n_intervals=0)]),
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
        dbc.Col(dcc.Dropdown(id='indicators',
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
                                 'label': indicator_name.upper(),
                                 'value': indicator_name.upper()
                             } for indicator_name in list(
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
                    ])
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


def generate_trading_activity_table():

    today_order_info = trading_robot.check_today_orders()

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


@app.callback(
    # output
    [Output('trading_activity_table', 'children')],
    # input
    [Input('interval-component', 'n_intervals')])
def update_trading_activity_table(n_interval):

    return generate_trading_activity_table()


@app.callback([Output('portfolio_chart', 'figure')],
              [Input('interval-component', 'n_intervals')])
def update_portfolio_chart(n_interval):

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

    portfolio_fig = go.Figure()

    portfolio_info = portfolio.get_portfolio_info()

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
    State('indicators', 'value')
])
def run_futubot(n_intervals, code_name, indicator):

    df = stockframe.frame.loc[code_name]

    fig = go.Figure()

    latest_prices = trading_robot.get_latest_bar()
    stockframe.add_rows(data=latest_prices)
    indicator_client.refresh()

    existing_orders = trading_robot.check_existing_orders(
        code_list=portfolio.holdings)
    print('existing_orders', existing_orders)

    StrategyClass = cfg_dict['strategy']['name']
    strategy_client = StrategyClass(stockframe, portfolio, indicator_client,
                                    existing_orders,
                                    **cfg_dict['strategy']['params'])
    buy_sell_signals = strategy_client.calculate_buy_sell_signals()

    order_infos = trading_robot.execute_signals(
        buy_sell_signals=buy_sell_signals)
    pprint.pprint(order_infos)

    portfolio.update_positions(order_infos=order_infos)

    print('after', portfolio.holdings)

    fig.add_trace(trace=go.Candlestick(x=df.index,
                                       open=df['open'],
                                       high=df['high'],
                                       low=df['low'],
                                       close=df['close'],
                                       name='Close'))

    volume_colors = [
        'green' if row['open'] - row['close'] >= 0 else 'red'
        for _, row in df.iterrows()
    ]

    if indicator == 'Volume':
        fig = go.Figure(data=go.Bar(x=df.index,
                                    y=df['volume'],
                                    marker_color=volume_colors,
                                    name='Volume'))

    if indicator[:3] == 'RSI':
        fig = go.Figure(
            data=go.Scatter(x=df.index,
                            y=df[indicator.lower()],
                            name=indicator,
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

    if indicator[:3] == 'SMA':
        fig.add_trace(trace=go.Scatter(
            x=df.index,
            y=df[indicator.lower()],
            name=indicator,
            line=dict(color='orange', width=2),
        ), )

    if indicator[:3] == 'EMA':
        fig.add_trace(trace=go.Scatter(
            x=df.index,
            y=df[indicator.lower()],
            name=indicator,
            line=dict(color='#2ed9ff', width=2),
        ), )

    if indicator == 'MACD':
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

    if indicator == 'BOLLINGER_BANDS':
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

    if indicator == 'STANDARD_DEVIATION':
        fig = go.Figure(
            go.Scatter(x=df.index,
                       y=df['standard_deviation'],
                       line=dict(color='rgb(102, 166, 30)', width=2),
                       name='Standard Deviation'))

    if indicator == 'STOCHASTIC_OSCILLATOR':
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

    return [fig]


if __name__ == '__main__':
    app.run_server()
