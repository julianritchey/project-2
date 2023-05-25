# Import dependencies
from .nav_bar import navbar
from dash import dash_table, dcc, html, register_page
from dotenv import find_dotenv, load_dotenv
from flask import session
from imports import get_headers, get_account_balance, get_ticker, get_all_tickers, get_symbols, clean_symbols_data, get_symbols_pair, get_base_currency, get_quote_currency, get_deposit_list, get_base_fee, get_actual_fee_rate, get_24hr_stats, get_market_list, get_trade_histories, get_klines, get_currencies, get_fiat_price, get_ohlc_data, get_investment_data, get_total_portfolio_value, get_total_profit_loss, select_all_exchanges_data
from os import environ as env
from questrade_api import Questrade
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import sqlalchemy as db

# Register page with Dash app
register_page(
    __name__,
    name="Account management"
)

# Set credentials
db_user = env.get('DB_USER')
db_pass = env.get('DB_PASS')
api_key = env.get('KUCOIN_API_KEY')
api_secret = env.get('KUCOIN_API_SECRET')
api_passphrase = env.get('KUCOIN_API_PASSPHRASE')
# q_refresh_token = env.get('QUESTRADE_REFRESH_TOKEN')
# q = Questrade()

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech1_db")

# Run API calls
all_exchange_data = select_all_exchanges_data(engine)
kucoin_account_balance = get_account_balance(api_key, api_secret, api_passphrase)
kucoin_account_balance = pd.DataFrame(kucoin_account_balance).drop(columns=['id'])

fig1 = go.Figure(data=go.Scattergeo(
    lon=all_exchange_data['longitude'],
    lat=all_exchange_data['latitude'],
    text=all_exchange_data['name'],
))
fig1.update_geos(projection_type="orthographic")
fig1.update_layout(
    height=400,
    margin={"r":0,"t":60,"l":0,"b":30},
    title="Exchange Locations",
)

fig2 = go.Figure(data=go.Scattergeo(
    lon=all_exchange_data['longitude'],
    lat=all_exchange_data['latitude'],
    text=all_exchange_data['name'],
))
fig2.update_geos(projection_type="natural earth")
fig2.update_layout(
    height=400,
    margin={"r":0,"t":60,"l":0,"b":30},
    title="Exchange Locations",
)

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

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            dash_table.DataTable(
                all_exchange_data.to_dict('records'),
                style_table={'color':'black'},
                style_header={'padding-left':'0.5rem', 'text-align':'left'},
                style_data={'padding-left':'0.5rem', 'text-align':'left'},
            ),
            dcc.Graph(
                figure=fig1,
                className='mt-3',
            ),
            dcc.Graph(
                figure=fig2,
                className='mt-3',
            ),
        ]
    ),
    className="mt-3",
)



# Define page Layout
def layout():
    return html.Div(
        children=[
            html.H2(["Account management"], className='mx-3 my-3'),
            dbc.Tabs(
                [
                    dbc.Tab(tab1_content, label="Questrade"),
                    dbc.Tab(tab2_content, label="Kucoin"),
                    dbc.Tab(tab3_content, label="Exchanges information"),
                ],
                active_tab="tab-0"
            )
        ]
    )
