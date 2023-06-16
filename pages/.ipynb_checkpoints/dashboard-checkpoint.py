# Import dependencies
from .nav_bar import navbar
from dash import callback, dash_table, dcc, html, Input, Output, register_page, State
from dotenv import find_dotenv, load_dotenv
from flask import session
from imports import GetExchangeConnectionData, select_all_exchanges_data, select_exchange_connections_data, update_exchange_connections_data # get_headers, get_account_balance, get_ticker, get_all_tickers, get_symbols, clean_symbols_data, get_symbols_pair, get_base_currency, get_quote_currency, get_deposit_list, get_base_fee, get_actual_fee_rate, get_24hr_stats, get_market_list, get_trade_histories, get_klines, get_currencies, get_fiat_price, get_ohlc_data, get_investment_data, get_total_portfolio_value, get_total_profit_loss
from os import environ as env
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import sqlalchemy as db
import string
import boto3
from botocore.exceptions import ClientError

# Register page with Dash app
register_page(
    __name__,
    path="/"
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

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech2_db")

# Run preliminary API calls
all_exchange_data = select_all_exchanges_data(engine)

# Define page Layout
def layout():
    exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
    connections_list = [
        {'label':'Summary','value':'summary'},
        {'label': html.Hr(
            className='my-0',
        ), 'value': 'none', 'disabled': True,},
    ]
    if not exchange_connections_data.empty:
        exchange_list = []
        for id, connection in exchange_connections_data.iterrows():
            exchange_name = all_exchange_data.loc[all_exchange_data['exchange_id']==connection['exchange_id'], 'name'].values[0]
            exchange_list.append(exchange_name)
        exchange_list.sort()
        for exchange in exchange_list:
            connections_list.append({'label':exchange, 'value':exchange})
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        id='dashboard-radios',
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
                                        # input_checked_class_name='active',
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
                                        value='summary',
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
                            html.H2(["Dashboard"], className='mb-0 mt-3'),
                            html.H5(["Summary"], className='mb-3', id='dashboard-subtitle'),
                            html.Div(id='subpage-content', style={'overflow': 'scroll'}),
                        ],
                        class_name='px-4',
                        width=10,
                    )
                ],
                class_name='vw-100'
            ),
            dcc.Store(
                data=exchange_connections_data.to_dict(),
                id='dashboard-exchange-connections',
            ),
        ],
    )

@callback(
    Output('subpage-content', 'children'),
    Output('dashboard-subtitle', 'children'),
    Output('dashboard-exchange-connections', 'data'),
    Input('dashboard-radios', 'value'),
    State('dashboard-exchange-connections', 'data'),
)
def load_subpage_cb(subpage, connections):
    connections = pd.DataFrame.from_dict(connections)
    connection_dict = {}
    if subpage != 'summary':
        exchange_id = all_exchange_data.loc[all_exchange_data['name']==subpage, 'exchange_id'].values[0]
        connection = connections.loc[connections['exchange_id']==exchange_id]
        input_data = [connection['api_1'].values[0], connection['api_2'].values[0], connection['api_3'].values[0]]
        exchange_abbr = subpage.translate(str.maketrans('', '', string.punctuation))
        exchange_abbr = exchange_abbr.translate(str.maketrans('', '', ' '))
        account = getattr(GetExchangeConnectionData, exchange_abbr)
        account_data, api_data = account(input_data)
        account_df = None
        if subpage == 'Alpaca':
            account_df = pd.DataFrame.from_dict(account_data)
        elif subpage == 'Bitget':
            account_df = pd.DataFrame.from_dict(account_data['data'])
        elif subpage == 'KuCoin':
            account_df = pd.DataFrame.from_dict(account_data)
        elif subpage == 'Questrade Inc.':
            account_df = pd.DataFrame.from_dict(account_data['accounts'])
            update_db = update_exchange_connections_data(api_data[0], api_data[1], api_data[2], api_data[3], connection['exconn_id'].values[0], engine)
        connection_dict[subpage] = dash_table.DataTable(account_df.to_dict('records'), [{"name": i, "id": i} for i in account_df.columns])
        exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
        return connection_dict[subpage], subpage, exchange_connections_data.to_dict()
    # for id, connection in connections.iterrows():
    #     input_data = [connection['api_1'], connection['api_2'], connection['api_3']]
    #     exchange_id = connection['exchange_id']
    #     exchange = all_exchange_data.loc[all_exchange_data['exchange_id']==exchange_id, 'name'].values[0]
    #     exchange_abbr = exchange.translate(str.maketrans('', '', string.punctuation))
    #     exchange_abbr = exchange_abbr.translate(str.maketrans('', '', ' '))
    #     print(connection['exconn_id'])
    #     if exchange == 'Bitget':
    #         account = getattr(GetExchangeConnectionData, exchange_abbr)
    #         print(account)
    #         account_data, api_data = account(input_data)
    #         account_df = pd.DataFrame.from_dict(account_data['data'])
    #         connection_dict[exchange] = dash_table.DataTable(account_df.to_dict('records'), [{"name": i, "id": i} for i in account_df.columns])
    #     if exchange == 'KuCoin':
    #         account = getattr(GetExchangeConnectionData, exchange_abbr)
    #         print(account)
    #         account_data, api_data = account(input_data)
    #         account_df = pd.DataFrame.from_dict(account_data)
    #         connection_dict[exchange] = dash_table.DataTable(account_df.to_dict('records'), [{"name": i, "id": i} for i in account_df.columns])
    #     if exchange == 'Questrade Inc.':
    #         account = getattr(GetExchangeConnectionData, exchange_abbr)
    #         print(account)
    #         account_data, api_data = account(input_data)
    #         account_df = pd.DataFrame.from_dict(account_data)
    #         update_db = update_exchange_connections_data(api_data[0], api_data[1], api_data[2], api_data[3], connection['exconn_id'], engine)
    #         print(update_db)
    #         connection_dict[exchange] = dash_table.DataTable(account_df.to_dict('records'), [{"name": i, "id": i} for i in account_df.columns])
    elif subpage == 'summary':
        exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
        connection_list = {}
        for i, connection in exchange_connections_data.iterrows():
            exchange_name = all_exchange_data.loc[all_exchange_data['exchange_id']==connection['exchange_id'], 'name'].values[0]
            input_data = [connection['api_1'], connection['api_2'], connection['api_3']]
            exchange_abbr = exchange_name.translate(str.maketrans('', '', string.punctuation))
            exchange_abbr = exchange_abbr.translate(str.maketrans('', '', ' '))
            account = getattr(GetExchangeConnectionData, exchange_abbr)
            account_data, api_data = account(input_data)
            account_df = None
            if exchange_name == 'Alpaca':
                account_df = pd.DataFrame.from_dict(account_data)
            elif exchange_name == 'Bitget':
                account_df = pd.DataFrame.from_dict(account_data['data'])
            elif exchange_name == 'KuCoin':
                account_df = pd.DataFrame.from_dict(account_data)
            elif exchange_name == 'Questrade Inc.':
                account_df = pd.DataFrame.from_dict(account_data['accounts'])
                update_db = update_exchange_connections_data(api_data[0], api_data[1], api_data[2], api_data[3], connection['exconn_id'], engine)
            connection_list[exchange_name] = dbc.AccordionItem(dash_table.DataTable(account_df.to_dict('records'), [{"name": i, "id": i} for i in account_df.columns]), title=exchange_name)
        accordion_list = []
        sorted_connections = dict(sorted(connection_list.items()))
        for key, value in sorted_connections.items():
            accordion_list.append(value)
        subpage_body = dbc.Accordion(accordion_list)
        return subpage_body, "Summary", exchange_connections_data.to_dict()
    else:
        exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
        return connection_dict[subpage], subpage, exchange_connections_data.to_dict()