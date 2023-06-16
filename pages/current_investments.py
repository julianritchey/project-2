# Import dependencies
from .nav_bar import navbar
from dash import dash_table, dcc, html, register_page
from dotenv import find_dotenv, load_dotenv
from flask import session
# from imports import get_headers, get_account_balance, get_ticker, get_all_tickers, get_symbols, clean_symbols_data, get_symbols_pair, get_base_currency, get_quote_currency, get_deposit_list, get_base_fee, get_actual_fee_rate, get_24hr_stats, get_market_list, get_trade_histories, get_klines, get_currencies, get_fiat_price, get_ohlc_data, get_investment_data, get_total_portfolio_value, get_total_profit_loss, select_all_exchanges_data
from os import environ as env
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import sqlalchemy as db

# Register page with Dash app
# register_page(
#     __name__,
#     name="Current investments"
# )

# Set database credentials
db_user = env.get('DB_USER')
db_pass = env.get('DB_PASS')
api_key = env.get('KUCOIN_API_KEY')
api_secret = env.get('KUCOIN_API_SECRET')
api_passphrase = env.get('KUCOIN_API_PASSPHRASE')

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech1_db")

# Run API calls
# kucoin_account_balance = get_account_balance(api_key, api_secret, api_passphrase)
# kucoin_account_balance = pd.DataFrame(kucoin_account_balance).drop(columns=['id'])
# print(kucoin_account_balance)
kucoin_account_balance = {
    'currency':['ROUTE','ATOM','API3','KNC','USDT','USDT'],
    'type':['trade','trade','trade','trade','trade','main'],
    'balance':[3729.2422,50,235,142.316,0.00007904,0],
    'available':[3729.2422,50,235,142.316,0.00007904,0],
    'holds':[0,0,0,0,0,0]
}
kucoin_account_balance = pd.DataFrame(kucoin_account_balance)

table1_header = [html.Thead(
        html.Tr([
                html.Th("Exchange"),
                html.Th("Open date"),
                html.Th("Open price"),
                html.Th("Current PnL")
            ]))]

table1_body = [html.Tbody([
    html.Tr([html.Td("Questrade"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$6.00")]),
    html.Tr([html.Td("Kucoin"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$7.00")]),
    html.Tr([html.Td("SPY"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$8.00")]),
    html.Tr([html.Td("TSLA"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$9.00")])
])]

table2_header = [html.Thead(
        html.Tr([
                html.Th("Portfolio/ticker"),
                html.Th("Open date"),
                html.Th("Open price"),
                html.Th("Current PnL")
            ]))]

table2_body = [html.Tbody([
    html.Tr([html.Td("KuCoin"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$8.00")]),
    html.Tr([html.Td("TSLA"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$9.00")]),
    html.Tr([html.Td("GOOG"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$7.00")]),
    html.Tr([html.Td("AAPL"), html.Td(pd.Timestamp.today()), html.Td("$50.00"), html.Td("$6.00")])
])]

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            dash_table.DataTable(
                kucoin_account_balance.to_dict('records'),
                style_table={'color':'black'},
                style_header={'padding-left':'0.5rem', 'text-align':'left'},
                style_data={'padding-left':'0.5rem', 'text-align':'left'},
            ),
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Table(
                # using the same table as in the above example
                table2_header + table2_body,
                bordered=True,
                dark=True,
                hover=True,
                responsive=True,
                striped=True,
            )
        ]
    ),
    className="mt-3",
)



# Define page Layout
def layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        id='radios',
                                        class_name='btn-group ms-0 ps-0 w-100 rounded-0',
                                        input_class_name='btn-check ms-0',
                                        input_style={
                                            'margin-left':'0px',
                                            'padding-left':'0px',
                                        },
                                        label_class_name='btn rounded-0 w-100 mx-0 my-1 px-3 py-3',
                                        label_style={
                                            'border':'1px solid black',
                                            'text-align':'left',
                                        },
                                        # input_checked_class_name='active',
                                        label_checked_style={
                                            'background-color':'rgba(80, 80, 80, 0.2)',
                                            'border-right':'6px solid #00bc8c',
                                        },
                                        options=[
                                            {'label': 'Exchange 1', 'value': 1},
                                            {'label': 'Exchange 2', 'value': 2},
                                            {'label': 'Exchange 3', 'value': 3},
                                        ],
                                        style={
                                            'before':'hidden',
                                            'display':'block',
                                            'flex-direction':'column',
                                            'margin-left':'0px',
                                            'padding-left':'0px',
                                        },
                                        value=1,
                                    ),
                                ],
                                className="radio-group ms-0 ps-0",
                                style={
                                    'margin-left':'0px',
                                    'padding-left':'0px',
                                },
                            ),
                        ],
                        class_name='px-0',
                        style={
                            'border-right':'1px solid #ccc',
                                    'margin-left':'0px',
                                    'padding-left':'0px',
                        },
                        width=2,
                    ),
                    dbc.Col(
                        [
                            html.H2(["Current investments"], className='mx-3 my-3'),
                            dbc.Tabs(
                                [
                                    dbc.Tab(tab1_content, label="Kucoin"),
                                    dbc.Tab(tab2_content, label="Questrade"),
                                ],
                                active_tab='tab-0'
                            ),
                        ],
                        width=8,
                    )
                ],
                class_name='vw-100'
            )
        ],
    )
