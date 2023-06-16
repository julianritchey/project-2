# Import dependencies
from .nav_bar import navbar
from dash import ALL, callback, callback_context, dash_table, dcc, html, Input, MATCH, Output, register_page, State
from dotenv import find_dotenv, load_dotenv
from flask import session
from imports import alpaca_get_asset, nn_train_and_predict_stock, select_all_exchanges_data, select_exchange_connections_data, TradingStrategies, trix_evaluate_portfolio, trix_evaluate_trades, trix_generate_and_plot_ema_signals
from os import environ as env
from pathlib import Path
from datetime import date, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import sqlalchemy as db
import boto3
import talib as ta
from botocore.exceptions import ClientError
import websocket
import json
import asyncio

# Register page with Dash app
register_page(
    __name__
)

# Set database credentials
# def get_secret():
#     secret_name = "arn:aws:secretsmanager:ca-central-1:763833024939:secret:dev/fintech2/postgresql-GQS0HT"
#     region_name = "ca-central-1"

#     # Create a Secrets Manager client
#     session = boto3.session.Session(region_name=region_name)
#     print(session)
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         get_secret_value_response = client.get_secret_value(
#             SecretId=secret_name
#         )
#         print(get_secret_value_response)
#     except ClientError as e:
#         # For a list of exceptions thrown, see
#         # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
#         raise e

#     # Decrypts secret using the associated KMS key.
#     secret = get_secret_value_response['SecretString']

#     return secret

db_user = env.get('DB_USER')
db_pass = env.get('DB_PASS')

websocket_message = []

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech2_db")

# Run preliminary API calls
all_exchange_data = select_all_exchanges_data(engine)
trading_strategy_list = TradingStrategies.StrategyList()

# Get ticker list
nasdaq_ticker_data = pd.read_csv(Path("assets/nasdaq_screener_2023-04-18.csv"))
nasdaq_ticker_list = nasdaq_ticker_data[['Symbol', 'Name']]
today = date.today()
tomorrow = today + timedelta(days = 1)
yesterday = today - timedelta(days = 1)
prediction_start_date = today - timedelta(weeks = 156)

# Create dictionary for subpage content
content = {
    'guide':html.Div(
        [
            html.H5("Guide", className='mb-3'),
            dbc.CardBody(
                [
                    html.P(
                        [
                            "In order to trade using this platform, you must have performed the following:",
                            html.Ul(
                                [
                                    html.Li("Connected an account you have with an exchange, using an API with trading access."),
                                    html.Li("Added your risk tolerance to your profile.")
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    ),
    'predictor':html.Div(
        [
            html.H5("Predictor", className='mb-3'),
            dbc.CardBody(
                [
                    html.P(
                        [
                            "Enter a ticker of your choosing.",
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Label("Ticker symbol", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-predictor',
                                                            'type':'symbol-input',
                                                        },
                                                        placeholder="Enter a ticker symbol",
                                                        style={'text-transform':'uppercase'},
                                                        type='text',
                                                    ),
                                                    dbc.FormText(
                                                        id={
                                                            'purpose':'trading-predictor',
                                                            'type':'symbol-formtext',
                                                        },
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label("Training start date", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-predictor',
                                                            'type':'startdate-input',
                                                        },
                                                        disabled=True,
                                                        type='Date',
                                                        value=prediction_start_date,
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label("Training end date", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-predictor',
                                                            'type':'enddate-input',
                                                        },
                                                        disabled=True,
                                                        type='Date',
                                                        value=today,
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        "Run predictor",
                                                        className='w-100',
                                                        id={
                                                            'purpose':'trading-predictor',
                                                            'type':'run-button',
                                                        },
                                                    ),
                                                ],
                                                width=12,
                                            ),
                                        ],
                                        className='w-100 mb-3 text-center',
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("A note about the predictor"),
                                            dbc.CardBody(
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li("At this time, the predictor can only predict Nasdaq equities."),
                                                            html.Li("The predictor only predicts the next trading day's closing price."),
                                                            html.Li("The predictor's model uses the last 156 weeks (roughly, three years) of ticker data for training and testing."),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Collapse(
                                        [
                                            dbc.Card(
                                                id={
                                                    'purpose':'trading-predictor',
                                                    'type':'subpage-details-card',
                                                },)
                                        ],
                                        id={
                                            'purpose':'trading-predictor',
                                            'type':'subpage-details-collapse',
                                        },
                                        is_open=False,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    'strategies':html.Div(
        [
            html.H5("Strategy evaluator", className='mb-3'),
            dbc.CardBody(
                [
                    html.P(
                        [
                            "Select a strategy and backtest it with a ticker of your choosing.",
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Label("Strategy", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Select(
                                                        id='trading-strategy-input',
                                                        options=[
                                                            {'label':strategy, 'value':strategy}
                                                            for strategy in trading_strategy_list
                                                        ],
                                                        placeholder="Select a strategy",
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label("Ticker symbol", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-strategies',
                                                            'type':'symbol-input',
                                                        },
                                                        placeholder="Enter a ticker symbol",
                                                        style={'text-transform':'uppercase'},
                                                        type='text',
                                                    ),
                                                    dbc.FormText(
                                                        id={
                                                            'purpose':'trading-strategies',
                                                            'type':'symbol-formtext',
                                                        },
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label("Backtest start date", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-strategies',
                                                            'type':'startdate-input',
                                                        },
                                                        max=yesterday,
                                                        min='1950-01-01',
                                                        type='Date',
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label("Backtest end date", width=4),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        id={
                                                            'purpose':'trading-strategies',
                                                            'type':'enddate-input',
                                                        },
                                                        max=yesterday,
                                                        min='1950-01-01',
                                                        type='Date',
                                                        value=yesterday,
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                        ],
                                        className='w-100 mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        "Run backtest",
                                                        className='w-100',
                                                        id={
                                                            'purpose':'trading-strategies',
                                                            'type':'run-button',
                                                        },
                                                    ),
                                                ],
                                                width=12,
                                            ),
                                        ],
                                        className='w-100 mb-3 text-center',
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Collapse(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(id='trading-strategy-cardheader'),
                                                    dbc.CardBody(id='trading-strategy-cardbody'),
                                                ],
                                            ),
                                        ],
                                        id="trading-strategy-details-collapse",
                                        is_open=False,
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Collapse(
                                        [
                                            dbc.Card(
                                                id={
                                                    'purpose':'trading-strategies',
                                                    'type':'subpage-details-card',
                                                },
                                            )
                                        ],
                                        id={
                                            'purpose':'trading-strategies',
                                            'type':'subpage-details-collapse',
                                        },
                                        is_open=False,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
    'trading':html.Div(
        [
            html.H5("Bot", className='mb-3'),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    dbc.Row(
                                                                        [
                                                                            dbc.Label("Exchange", width=3),
                                                                            dbc.Col(
                                                                                [
                                                                                    dbc.Select(
                                                                                        id='trading-bot-exchange-input',
                                                                                        options=[
                                                                                            {'label':'Alpaca (paper)', 'value':'Alpaca'}
                                                                                        ],
                                                                                        placeholder="Select an exchange",
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                        className='mb-3',
                                                                    ),
                                                                    dbc.Row(
                                                                        [
                                                                            dbc.Label("Ticker symbol", width=3),
                                                                            dbc.Col(
                                                                                [
                                                                                    dbc.Input(
                                                                                        id={
                                                                                            'purpose':'trading-bot',
                                                                                            'type':'symbol-input',
                                                                                        },
                                                                                        placeholder="Enter a ticker symbol",
                                                                                        style={'text-transform':'uppercase'},
                                                                                        type='text',
                                                                                    ),
                                                                                    dbc.FormText(
                                                                                        id={
                                                                                            'purpose':'trading-bot',
                                                                                            'type':'symbol-formtext',
                                                                                        },
                                                                                    ),
                                                                                ],
                                                                                width=9,
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                        className='mb-3',
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Collapse(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardBody(
                                                                        [
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Label("Order type", width=3),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Select(
                                                                                                id='trading-bot-order-type-input',
                                                                                                options=[
                                                                                                    {'label':'Limit', 'value':'Limit'},
                                                                                                    {'label':'Market', 'value':'Market'},
                                                                                                ],
                                                                                                placeholder="Select an order type",
                                                                                                value='Limit',
                                                                                            ),
                                                                                        ],
                                                                                        width=9,
                                                                                    ),
                                                                                ],
                                                                                className='mb-3',
                                                                            ),
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Label("Quantity", width=3),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Input(
                                                                                                id={
                                                                                                    'purpose':'trading-bot',
                                                                                                    'type':'quantity-input',
                                                                                                },
                                                                                                placeholder="Enter quantity",
                                                                                                type='number',
                                                                                            ),
                                                                                        ],
                                                                                        width=9,
                                                                                    ),
                                                                                ],
                                                                                className='mb-3',
                                                                            ),
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Label("Price", width=3),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Input(
                                                                                                id={
                                                                                                    'purpose':'trading-bot',
                                                                                                    'type':'price-input',
                                                                                                },
                                                                                                placeholder="Enter price",
                                                                                                type='number',
                                                                                            ),
                                                                                        ],
                                                                                        width=9,
                                                                                    ),
                                                                                ],
                                                                                className='mb-3',
                                                                            ),
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Button(
                                                                                                "BUY",
                                                                                                color='success',
                                                                                                id={
                                                                                                    'purpose':'buy',
                                                                                                    'subpage':'trading-bot',
                                                                                                    'type':'order-button',
                                                                                                },
                                                                                                class_name='w-100',
                                                                                                n_clicks=0,
                                                                                            ),
                                                                                        ],
                                                                                        style={
                                                                                            'text-align':'left',
                                                                                        },
                                                                                        width=6,
                                                                                    ),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Button(
                                                                                                "SELL",
                                                                                                color='danger',
                                                                                                id={
                                                                                                    'purpose':'sell',
                                                                                                    'subpage':'trading-bot',
                                                                                                    'type':'order-button',
                                                                                                },
                                                                                                class_name='w-100',
                                                                                                n_clicks=0,
                                                                                            ),
                                                                                        ],
                                                                                        style={
                                                                                            'text-align':'right',
                                                                                        },
                                                                                        width=6,
                                                                                    ),
                                                                                ],
                                                                                className='mb-3',
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                        id={
                                                            'purpose':'trading-form-collapse',
                                                            'subpage':'trading-bot',
                                                        },
                                                        is_open=False,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Collapse(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(id='trading-bot-ticker-details-cardheader'),
                                                    dbc.CardBody(id='trading-bot-ticker-details-cardbody'),
                                                ],
                                            ),
                                        ],
                                        id={
                                            'purpose':'ticker-details-collapse',
                                            'subpage':'trading-bot',
                                        },
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(id='trading-bot-order-div', className='mb-3'),
                                    dbc.Button("Start websocket", id='start-websocket-button'),
                                    html.Div(id='websocket-update-div', className='mb-3'),
                                    dcc.Interval(disabled=True, id='websocket-update', interval=1000),
                                ],
                                width=6,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
}
websocket_message = None
# Define page Layout
def layout():
    #open_websocket()
    exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
    connections_list = [
        {'label':'Guide','value':'guide'},
        {'label': html.Hr(
            className='my-0',
        ), 'value': 'none', 'disabled': True,},
        {'label':'Predictor','value':'predictor'},
        {'label':'Strategies','value':'strategies'},
        {'label': html.Hr(
            className='my-0',
        ), 'value': 'none', 'disabled': True,},
        {'label':'Trading bot','value':'trading'},
    ]
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        id='trading-radios',
                                        class_name='btn-group ms-0 ps-0 w-100 rounded-0',
                                        input_class_name='btn-check ms-0',
                                        input_style={
                                            'margin-left':'0px',
                                            'padding-left':'0px',
                                        },
                                        label_class_name='btn rounded-0 w-100 mx-0 my-0 px-3 py-2',
                                        label_style={
                                            'border':'none',
                                            'text-align':'left',
                                        },
                                        label_checked_style={
                                            'background-color':'rgba(80, 80, 80, 0.2)',
                                            'border-right':'6px solid #00bc8c',
                                        },
                                        options=connections_list,
                                        style={
                                            'before':'hidden',
                                            'display':'block',
                                            'flex-direction':'column',
                                            'margin-left':'0px',
                                            'padding-left':'0px',
                                        },
                                        value='guide',
                                    ),
                                ],
                                className="radio-group ms-0 ps-0 pt-3",
                                style={
                                    'margin-left':'0px',
                                    'padding-left':'0px',
                                },
                            ),
                        ],
                        class_name='px-0',
                        style={
                            'border-right':'1px solid rgba(80, 80, 80, 0.2)',
                        },
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.H2(["Trading"], className='mb-0 mt-3'),
                            html.Div(content['guide'], id='trading-subpage-content'),
                        ],
                        class_name='px-4',
                        width=10,
                    ),
                    dcc.Store(id='websocket-store'),
                ],
                class_name='vw-100'
            )
        ],
    )

# Callback for displaying subpage content
@callback(
    Output('trading-subpage-content', 'children'),
    Input('trading-radios', 'value'),
    prevent_initial_call=True
)
def trading_load_subpage(subpage):
    return content[subpage]

# Callback for displaying strategy details
@callback(
    Output('trading-strategy-cardheader', 'children'),
    Output('trading-strategy-cardbody', 'children'),
    Output('trading-strategy-details-collapse', 'is_open'),
    Input('trading-strategy-input', 'value'),
    prevent_initial_call=True
)
def display_strategy_details(strategy):
    if strategy:
        strategy_class = getattr(TradingStrategies, strategy+'Strategy')
        strategy_data = strategy_class.information()
        return strategy_data['title'], strategy_data['description'], True
    else:
        return None, None, False

# Callback for validating ticker input
@callback(
    Output({'type':'symbol-input','purpose':MATCH}, 'invalid'),
    Output({'type':'symbol-input','purpose':MATCH}, 'valid'),
    Output({'type':'symbol-input','purpose':MATCH}, 'value'),
    Output({'type':'symbol-formtext','purpose':MATCH}, 'children'),
    Input({'type':'symbol-input','purpose':MATCH}, 'value'),
    prevent_initial_call=True
)
def validate_ticker_input(symbol):
    if symbol:
        symbol = symbol.upper()
        ticker_details = None
        if symbol in nasdaq_ticker_data['Symbol'].to_list():
            ticker_details = ' - '.join([symbol, nasdaq_ticker_data.loc[nasdaq_ticker_data['Symbol']==symbol, 'Name'].values[0]])
            invalid = False
            valid = True
            collapse = False
        elif symbol == '':
            ticker_details = None
            invalid = False
            valid = False
            collapse = False
        else:
            ticker_details = 'Ticker symbol is invalid'
            invalid = True
            valid = False
            collapse = True
        return invalid, valid, symbol, ticker_details
    else:
        return None, None, None, None

# Callback for adjusting backtest end date minimum value
@callback(
    Output({'type':'enddate-input','purpose':MATCH}, 'min'),
    Input({'type':'startdate-input','purpose':MATCH}, 'value'),
)
def adjust_backtest_enddate_min(date):
    if date:
        return date
    else:
        return '1950-01-01'

# Callback for adjusting backtest start date maximum value
@callback(
    Output({'type':'startdate-input','purpose':MATCH}, 'max'),
    Input({'type':'enddate-input','purpose':MATCH}, 'value'),
)
def adjust_backtest_enddate_min(date):
    if date:
        return date
    else:
        return yesterday
    
# Callback for backtesting a strategy on a ticker
@callback(
    Output({'type':'subpage-details-collapse','purpose':'trading-strategies'}, 'is_open'),
    Output({'type':'subpage-details-card','purpose':'trading-strategies'}, 'children'),
    Input({'type':'run-button','purpose':'trading-strategies'}, 'n_clicks'),
    State('trading-strategy-input', 'value'),
    State({'type':'symbol-input','purpose':'trading-strategies'}, 'value'),
    State({'type':'startdate-input','purpose':'trading-strategies'}, 'value'),
    State({'type':'enddate-input','purpose':'trading-strategies'}, 'value'),
    prevent_initial_call=True
)
def run_strategy_backtest(n, strategy, symbol, start_date, end_date):
    content = []
    if n:
        # Generate card header
        card_header = dbc.CardHeader("Backtest results - Strategy: " + strategy + " - Ticker symbol: " + symbol)
                
        # Get backtest data
        strategy_class = getattr(TradingStrategies, strategy+'Strategy')
        signal_evaluation_figures, trade_evaluation_figures, portfolio_evaluation_tables = strategy_class.backtest(symbol, start_date, end_date)
        
        # Generate card body
        card_body = dbc.CardBody(
            [
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dcc.Graph(figure=figure)
                                for figure in signal_evaluation_figures
                            ],
                            title="Signal evaluation",
                        ),
                        dbc.AccordionItem(
                            [
                                dcc.Graph(figure=figure)
                                for figure in trade_evaluation_figures
                            ],
                            title="Trade evaluation",
                        ),
                        dbc.AccordionItem(
                            [
                                html.Div(table)
                                for table in portfolio_evaluation_tables
                            ],
                            title="Portfolio evaluation",
                        ),
                    ],
                )
            ]
        )
        content.append(card_header)
        content.append(card_body)
        return True, content
    else:
        return False, content
    
# Callback for predicting market movement for a ticker
@callback(
    Output({'type':'subpage-details-collapse','purpose':'trading-predictor'}, 'is_open'),
    Output({'type':'subpage-details-card','purpose':'trading-predictor'}, 'children'),
    Input({'type':'run-button','purpose':'trading-predictor'}, 'n_clicks'),
    State({'type':'symbol-input','purpose':'trading-predictor'}, 'value'),
    State({'type':'startdate-input','purpose':'trading-predictor'}, 'value'),
    State({'type':'enddate-input','purpose':'trading-predictor'}, 'value'),
    prevent_initial_call=True
)
def run_market_predictor(n, symbol, start_date, end_date):
    content = []
    if n:
        # Generate card header
        card_header = dbc.CardHeader("Predictor results - Ticker symbol: " + symbol)
        
        # Get prediction data
        end_date = date.fromisoformat(end_date)
        end_date = end_date + timedelta(days = 1)
        test_df, train_df, cvrmse_list = nn_train_and_predict_stock(symbol, start_date, end_date)
        
        # Generate prediction plot
        prediction_fig = go.Figure()
        prediction_fig.add_trace(
            go.Scatter(
                mode='lines',
                name='Training data',
                x=train_df.index,
                y=train_df['GT'],
            )
        )
        prediction_fig.add_trace(
            go.Scatter(
                mode='lines',
                name='Testing data',
                x=test_df.index,
                y=test_df['GT']
            )
        )
        prediction_fig.add_trace(
            go.Scatter(
                mode='lines',
                name='Predicted data',
                x=test_df.index,
                y=test_df['Predict']
            )
        )
        prediction_fig.update_layout(
            xaxis_title_text='Date',
            yaxis_title_text='Price in USD',
            title="Daily Closing Prices for Training, Testing and Predicted Data",
        )
        
        # Generate card body
        card_body = dbc.CardBody(
            [
                html.Div("Next day's predicted closing price: USD "+str(test_df['Predict'][-1]), style={'font-weight':'bold'}),
                html.Div("Predicted CVRMSE: "+str(cvrmse_list['predicted_cvrmse'])),
                html.Div("Shifted CVRMSE: "+str(cvrmse_list['shifted_cvrmse'])),
                dcc.Graph(figure=prediction_fig),
            ]
        )
        content.append(card_header)
        content.append(card_body)
        return True, content
    else:
        return False, content
    
# Callback for selecting trading bot exchange
@callback(
    Output({'subpage':'trading-bot','purpose':'trading-form-collapse'}, 'is_open'),
    Input('trading-bot-exchange-input', 'value'),
    prevent_initial_call=True
)
def open_trading_bot_form(value):
    if value:
        return True
    else:
        return False

@callback(
    Output({'purpose':'ticker-details-collapse','subpage':'trading-bot'}, 'is_open'),
    Output('trading-bot-ticker-details-cardheader', 'children'),
    Output('trading-bot-ticker-details-cardbody', 'children'),
    Output('websocket-store', 'data', allow_duplicate=True),
    Input({'purpose':'trading-bot','type':'symbol-input',}, 'value'),
    State({'purpose':'trading-bot','type':'symbol-input'}, 'valid'),
    prevent_initial_call=True
)
def display_ticker_details(symbol, valid):
    if symbol and valid:
        exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
        connection = exchange_connections_data.loc[exchange_connections_data['exchange_id']==4]
        details_body = []
        api_1 = connection['api_1'].values[0]
        api_2 = connection['api_2'].values[0]
        
        websocket_store = [api_1, api_2, symbol]
        
        asset_data = alpaca_get_asset(api_1, api_2, symbol)
        details_header = symbol+" - "+asset_data['name']
        for key, value in asset_data.items():
            details_body.append(html.Div(key+": "+value))
        return True, details_header, details_body, websocket_store
    else:
        return False, None, None, None
    
@callback(
    Output('trading-bot-order-div', 'children'),
    Input({'subpage':'trading-bot','type':'order-button','purpose':ALL}, 'n_clicks'),
    State({'purpose':'trading-bot','type':'symbol-input'}, 'value'),
    State('trading-bot-order-type-input', 'value'),
    State({'purpose':'trading-bot','type':'quantity-input'}, 'value'),
    State({'purpose':'trading-bot','type':'price-input'}, 'value'),
    prevent_initial_call=True
)
def place_order(n, symbol, order_type, quantity, price):
    if n[0] and callback_context.triggered_id['purpose']=='buy':
        if symbol and order_type and quantity and price:
            return order_type+" Buy "+str(quantity)+" "+symbol+" at USD "+str(price)
    elif n[1] and callback_context.triggered_id['purpose']=='sell':
        if symbol and order_type and quantity and price:
            return order_type+" Sell "+str(quantity)+" "+symbol+" at USD "+str(price)

@callback(
    Output('websocket-update-div', 'children', allow_duplicate=True),
    Input('websocket-update', 'n_intervals'),
    prevent_initial_call=True
)
def update_websocket_div(intervals):
    return websocket_message

@callback(
    Output('websocket-update', 'disabled'),
    Input('start-websocket-button', 'n_clicks'),
    prevent_initial_call=True
)
def start_websocket(n):
    if n:
        asyncio.run(open_websocket())
        return True
    else:
        return True

async def open_websocket():
    exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
    connection = exchange_connections_data.loc[exchange_connections_data['exchange_id']==4]
    api_1 = connection['api_1'].values[0]
    api_2 = connection['api_2'].values[0]

    def on_open(ws):
        auth_data = {
            'action': 'auth',
            'key': api_1,
            'secret': api_2
        }

        ws.send(json.dumps(auth_data))

        subscription_message = {
            "action": "subscribe",
            "trades": ["BTC/USDT"],
            #"quotes": ["AAPL"],
            #"bars": ["*"],
            # "dailyBars":["VOO"],
            # "statuses":["*"]
        }

        ws.send(json.dumps(subscription_message))

    def on_message(ws, message):
        print(message)
        websocket_message = message

    def on_close(ws):
        print("closed connection")

    socket = "wss://stream.data.alpaca.markets/v1beta2/crypto"

    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
    return None