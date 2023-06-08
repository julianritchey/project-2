# Import dependencies
from .nav_bar import navbar
from dash import ALL, dash_table, dcc, html, register_page, callback, ctx, Input, MATCH, Output, Patch, State
from dash.exceptions import PreventUpdate
from dotenv import find_dotenv, load_dotenv
from flask import session
from holoviews.plotting.plotly.dash import to_dash
from imports import calculate_statistics, calculate_stock_betas, calculate_sharpe_ratios, delete_from_assets_portfolios, insert_into_assets, insert_into_assets_portfolios, insert_into_portfolios, MCSimulation, portfolio_analysis, run_monte_carlo_simulation, select_all_portfolio_data
from os import environ as env
from pathlib import Path
import alpaca_trade_api as tradeapi
import dash_bootstrap_components as dbc
import holoviews as hv
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import sqlalchemy as db
import yfinance as yf

# Register page with Dash app
register_page(
    __name__,
    name="Portfolio planner"
)

# Set database credentials
alpaca_api_key = env.get('ALPACA_API_KEY')
alpaca_secret_key = env.get('ALPACA_SECRET_KEY')
db_user = env.get('DB_USER')
db_pass = env.get('DB_PASS')

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech1_db")

# Get ticker data
all_ticker_data = pd.read_csv(Path("assets/nasdaq_screener_2023-04-18.csv"))
all_ticker_data = all_ticker_data[['Symbol', 'Name']]

# Define page layout
def layout():
    return html.Div(
        children=[
            html.H2(["Portfolio planner"], className='mx-3 my-3'),
            html.Div(
                [
                    dbc.Row([
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.H4("Portfolio data", className='card-title'),
                                        ]),
                                        dbc.Col(
                                            [
                                                dbc.Button("Load saved portfolio", id='load_portfolio_button', n_clicks=0),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            dbc.ModalTitle("Load portfolio"),
                                                        ),
                                                        dbc.ModalBody(
                                                            dcc.Dropdown(
                                                                id='portfolio_dropdown',
                                                            ),
                                                        ),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Load", id="select_portfolio_button", n_clicks=0, disabled=True),
                                                        ),
                                                    ],
                                                    id="load_portfolio_modal",
                                                    is_open=False,
                                                ),
                                            ],
                                            style={'text-align':'right'},
                                        ),
                                    ]),   
                                    dbc.FormFloating(
                                        [
                                            dbc.Input(placeholder="Portfolio name", id="portfolio_name_input"),
                                            dbc.Label("Portfolio name"),
                                        ],
                                        class_name='mt-3',
                                    ),  
                                    dbc.FormFloating(
                                        [
                                            dbc.Input(placeholder="Investment period (years)", id="investment_period", type='number'),
                                            dbc.Label("Investment period (years)"),
                                        ],
                                        class_name='mt-4',
                                    ),
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button("Save portfolio", id='save_portfolio_button', color='success', disabled=True, n_clicks=0),
                                            dbc.Alert(
                                                id="portfolio_saved_alert",
                                                color='success',
                                                is_open=False,
                                                dismissable=True,
                                                duration=5000,
                                                style={"position": "fixed", "bottom": "0px", "text-align": "center", "width":"50%"},
                                            ),
                                            dbc.Button("Clear portfolio", id='clear_portfolio_button', color='danger', n_clicks=0, outline=True),
                                            dbc.Modal(
                                                [
                                                    dbc.ModalHeader(
                                                        dbc.ModalTitle("Clear portfolio")
                                                    ),
                                                    dbc.ModalBody("Are you sure you wish to clear the current portfolio data?"),
                                                    dbc.ModalFooter(
                                                        dbc.Button(
                                                            "Confirm", id="confirm_clear_portfolio_button", color="danger", n_clicks=0, outline=True
                                                        )
                                                    ),
                                                ],
                                                id="clear_portfolio_modal",
                                                is_open=False,
                                            ),
                                        ],
                                        class_name='mt-3',
                                        style={'width':'100%'},
                                        vertical=True,
                                    ),
                                ]),
                            ),
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.H4("Build your portfolio", className='card-title'),
                                        ]),
                                    ]),
                                    dbc.InputGroup(
                                        [
                                            dbc.FormFloating([
                                                dbc.Input(placeholder="Ticker", id="ticker_input", style={'text-transform':'uppercase'}),
                                                dbc.Label("Ticker"),
                                            ]),
                                            dbc.Button("Add ticker", id="ticker_button", n_clicks=0),
                                        ],
                                        class_name='mt-3',
                                    ),
                                    dbc.Collapse(
                                        html.Div([
                                            dbc.Label("Ticker is invalid"),
                                        ]),
                                        id="ticker_collapse",
                                        is_open=False,
                                        style={'color':'#e74c3c'},
                                    ),
                                    dbc.ListGroup(id="ticker_group", className='mt-3'),
                                    dbc.ListGroup(id="weight_group", className='mt-3'),
                                    dbc.FormText("Note: Weights should total 1"),
                                ]),
                            ),
                        ),
                    ]),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card([
                                    dbc.CardHeader(
                                        dbc.Tabs(
                                            [
                                                dbc.Tab(label="Portfolio calculations", tab_id="portfolio_calculations_tab"),
                                                dbc.Tab(label="Portfolio simulations", tab_id="portfolio_simulations_tab", ),
                                            ],
                                            id="portfolio_tabs",
                                            active_tab="portfolio_calculations_tab",
                                        ),
                                    ),
                                    dbc.CardBody(id="card-content"),
                                ]),
                            ),
                        ],
                        class_name='mt-4 mb-4',
                    ),
                ],
            ),
            dcc.Store(id='ticker_list'),
            dcc.Store(id='portfolio_data'),
            dcc.Store(id='loaded_portfolio_store'),
            dcc.Store(id='portfolio_name_store'),
            dcc.Store(id='load_portfolio_store'),
            dcc.Store(id='save_portfolio_store'),
            dcc.Store(id='refresh_tab'),
            dcc.Store(id='investment_input_store'),
            dcc.Store(id='calculations_tab_body_store', data=[
                dbc.Button("Run calculations", class_name='mb-3', color='primary', disabled=True, id={'type':'portfolio_button', 'purpose':'calculate'}, style={'width':'100%'}),
                html.Div(id={'type':'portfolio_div', 'purpose':'calculate'}),
            ]),
            dcc.Store(id='simulations_tab_body_store', data=[
                dbc.FormFloating([
                    dbc.Input(placeholder="Investment amount", id="investment_input", type="number"),
                    dbc.Label("Investment amount"),
                ]),
                dbc.Button("Run simulations", class_name='mb-3 mt-3', color='primary', disabled=True, id={'type':'portfolio_button', 'purpose':'simulate'}, style={'width':'100%'}),
                html.Div(id={'type':'portfolio_div', 'purpose':'simulate'}),
            ]),
        ],
    ),

# Define callback function for loading saved profiles
@callback(
    Output("load_portfolio_modal", "is_open", allow_duplicate=True),
    Output("portfolio_dropdown", "options"),
    Output('portfolio_data', 'data'),
    Input("load_portfolio_button", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks):
    if n_clicks==0:
        return PreventUpdate
    portfolio_data = select_all_portfolio_data(engine)
    portfolio_names = portfolio_data['portfolio_name'].unique()
    portfolio_list = []
    for name in portfolio_names:
        portfolio_list.append({'label':name, 'value':name})
    return True, portfolio_list, portfolio_data.to_json()

# Define callback function for selecting portfolio to be loaded
@callback(
    Output('select_portfolio_button', 'disabled'),
    Input('portfolio_dropdown', 'value'),
    prevent_initial_call=True,
)
def select_portfolio(selected_portfolio):
    if selected_portfolio:
        return False
    else:
        return True

# Define callback function for loading a saved portfolio
@callback(
    Output('portfolio_name_input', 'value', allow_duplicate=True),
    Output('investment_period', 'value', allow_duplicate=True),
    Output('ticker_group', 'children', allow_duplicate=True),
    Output('weight_group', 'children', allow_duplicate=True),
    Output('ticker_list', 'data', allow_duplicate=True),
    Input('loaded_portfolio_store', 'data'),
    prevent_initial_call=True,
)
def load_portfolio(loaded_portfolio):
    if loaded_portfolio:
        investment_period = 0
        ticker_list = []
        loaded_portfolio = pd.read_json(loaded_portfolio)
        patched_ticker_children = Patch()
        patched_weight_children = Patch()
        portfolio_name = loaded_portfolio.iloc[0]['portfolio_name']

        for i in range(len(loaded_portfolio)):
            ticker = loaded_portfolio.iloc[i]['ticker']
            ticker_name = loaded_portfolio.iloc[i]['ticker_name']
            weight = loaded_portfolio.iloc[i]['weight']
            investment_period = loaded_portfolio.iloc[i]['investment_period']
            ticker_list.append(ticker)
            new_ticker = dbc.ListGroupItem(ticker + " - " + ticker_name, id={'ticker':ticker, 'ticker_name':ticker_name})
            patched_ticker_children.append(new_ticker)
            new_weight = dbc.ListGroupItem(
                dbc.InputGroup([
                    dbc.Input(disabled=True, style={'width':'60%'}, value="Portfolio weight (in decimals) for "+ticker),
                    dbc.Input(id={'type':'weight', 'ticker':ticker}, type='number', value=weight)
                ])
            )
            patched_weight_children.append(new_weight)
        return portfolio_name, investment_period, patched_ticker_children, patched_weight_children, ticker_list
    else:
        return None, None, [], [], []

# Define callback function for validating ticker input
@callback(
    Output('ticker_input', 'invalid'),
    Output('ticker_input', 'valid'),
    Output('ticker_input', 'value'),
    Output('ticker_collapse', 'is_open'),
    Input('ticker_input', 'value'),
    prevent_initial_call=True
)
def validate_ticker_input(ticker):
    if ticker:
        ticker = ticker.upper()
        if ticker in all_ticker_data['Symbol'].to_list():
            invalid = False
            valid = True
            collapse = False
        elif ticker == '':
            invalid = False
            valid = False
            collapse = False
        else:
            invalid = True
            valid = False
            collapse = True
        return invalid, valid, ticker, collapse
    else:
        return None, None, None, False

# Define callback function for adding ticker to portfolio
@callback(
    Output('ticker_group', 'children'),
    Output('weight_group', 'children'),
    Output('ticker_input', 'value', allow_duplicate=True),
    Output('ticker_list', 'data', allow_duplicate=True),
    Input('ticker_button', 'n_clicks'),
    State('ticker_input', 'value'),
    State('ticker_group', 'children'),
    State('weight_group', 'children'),
    State('ticker_list', 'data'),
    prevent_initial_call=True
)
def add_ticker(n_clicks, ticker, ticker_children, weight_children, ticker_list):
    if n_clicks==0:
        raise PreventUpdate
    
    if not ticker_list:
        ticker_list = []
    if ticker in all_ticker_data['Symbol'].to_list() and ticker not in ticker_list:
        patched_ticker_children = Patch()
        ticker_name = ''
        for i in range(len(all_ticker_data)):
            if all_ticker_data.loc[i, "Symbol"]==ticker:
                ticker_name = all_ticker_data.loc[i, 'Name']
        new_ticker = dbc.ListGroupItem(ticker + " - " + ticker_name, id={'ticker':ticker, 'ticker_name':ticker_name})
        patched_ticker_children.append(new_ticker)
        ticker_list.append(ticker)
        patched_weight_children = Patch()
        new_weight = dbc.ListGroupItem(
            dbc.InputGroup([
                dbc.Input(value="Portfolio weight (in decimals) for "+ticker, disabled=True, style={'width':'60%'}),
                dbc.Input(id={'type':'weight', 'ticker':ticker}, type='number')
            ])
        )
        patched_weight_children.append(new_weight)
        return patched_ticker_children, patched_weight_children, None, ticker_list
    else:
        return ticker_children, weight_children, ticker, ticker_list

# Define callback function for displaying modal to confirm clearing portfolio
@callback(
    Output('clear_portfolio_modal', 'is_open', allow_duplicate=True),
    Input('clear_portfolio_button', 'n_clicks'),
    prevent_initial_call=True,
)
def close_portfolio_modal(n_clicks):
    if n_clicks==0:
        return PreventUpdate
    
    return True

# Define callback function for clearing portfolio
@callback(
    Output('ticker_input', 'value', allow_duplicate=True),
    Output('portfolio_name_input', 'value', allow_duplicate=True),
    Output('investment_period', 'value', allow_duplicate=True),
    Output('ticker_group', 'children', allow_duplicate=True),
    Output('weight_group', 'children', allow_duplicate=True),
    Output('clear_portfolio_modal', 'is_open'),
    Output('load_portfolio_modal', 'is_open'),
    Output('ticker_list', 'data'),
    Output('loaded_portfolio_store', 'data'),
    Output('portfolio_dropdown', 'value'),
    Output('portfolio_data', 'data', allow_duplicate=True),
    Output({'type':'portfolio_div', 'purpose':ALL}, 'children', allow_duplicate=True),
    Input('confirm_clear_portfolio_button', 'n_clicks'),
    Input('select_portfolio_button', 'n_clicks'),
    State('portfolio_dropdown', 'value'),
    State('portfolio_data', 'data'),
    prevent_initial_call=True,
)
def clear_portfolio(clear_n, select_n, selected_portfolio, portfolio_data):
    if clear_n==0 and select_n==0:
        return PreventUpdate
    
    trigger = ctx.triggered_id
    loaded_portfolio = None
    if trigger=='select_portfolio_button':
        portfolio_data = pd.read_json(portfolio_data)
        loaded_portfolio = portfolio_data[portfolio_data['portfolio_name']==selected_portfolio]
        return None, None, None, [], [], False, False, None, loaded_portfolio.to_json(), None, None, [[]]
    else:
        return None, None, None, [], [], False, False, None, loaded_portfolio, None, None, [[]]

# Define callback function for enabling button to save portfolio
@callback(
    Output('save_portfolio_button', 'disabled'),
    Output({'type':'portfolio_button', 'purpose':ALL}, 'disabled'),
    Output('refresh_tab', 'data', allow_duplicate=True),
    Input('ticker_group', 'children'),
    Input({'type':'weight', 'ticker':ALL}, 'value'),
    Input('portfolio_name_input', 'value'),
    Input('investment_period', 'value'),
    Input('refresh_tab', 'data'),
    prevent_initial_call=True,
)
def enable_save_portfolio(tickers, weights, portfolio_name, investment_period, active_tab):
    total_weight = 0
    for weight in weights:
        if weight:
            total_weight += weight
        else:
            return True, [True], False
    if total_weight==1 and tickers and portfolio_name and investment_period:
        return False, [False], False
    else:
        return True, [True], False

# Define callback function for saving portfolio
@callback(
    Output('portfolio_name_store', 'data'),
    Output('portfolio_saved_alert', 'is_open'),
    Output('portfolio_saved_alert', 'children'),
    Input('save_portfolio_button', 'n_clicks'),
    State('portfolio_name_input', 'value'),
    State('investment_period', 'value'),
    State('ticker_group', 'children'),
    State({'type':'weight', 'ticker':ALL}, 'value'),
    prevent_initial_call=True,
)
def save_portfolio(n_clicks, portfolio_name, investment_period, ticker_group, weight_group):
    if n_clicks==0:
        return PreventUpdate
    
    asset_group = []
    for ticker in ticker_group:
        ticker_symbol = ticker['props']['id']['ticker']
        ticker_name = ticker['props']['id']['ticker_name']
        asset_id = insert_into_assets(ticker_symbol, ticker_name, engine)
        asset_group.append(asset_id)
    portfolio_id = insert_into_portfolios(portfolio_name, investment_period, engine)
    delete_from_assets_portfolios(portfolio_id, engine)
    for i in range(len(asset_group)):
        insert_into_assets_portfolios(portfolio_id, asset_group[i], weight_group[i], engine)
    notice = 'Portfolio "'+portfolio_name+'" has been saved.'
    return portfolio_name, True, notice

@callback(
    Output('card-content', 'children'),
    Output('refresh_tab', 'data'),
    Input('portfolio_tabs', 'active_tab'),
    Input('calculations_tab_body_store', 'data'),
    Input('simulations_tab_body_store', 'data'),
)
def display_portfolio_tab(active_tab, calculations_tab_data, simulations_tab_data):
    if active_tab == "portfolio_simulations_tab":
        return simulations_tab_data, True
    else:
        return calculations_tab_data, True

@callback(
    Output('investment_input_store', 'data'),
    Input('investment_input', 'value'),
    prevent_initial_call=True,
)
def set_investment_input(investment):
    return investment

@callback(
    Output({'type':'portfolio_div', 'purpose':ALL}, 'children'),
    Input({'type':'portfolio_button', 'purpose':ALL}, 'n_clicks'),
    State('ticker_list', 'data'),
    State({'type':'weight', 'ticker':ALL}, 'value'),
    State('investment_period', 'value'),
    State('investment_input_store', 'data'),
    prevent_initial_call=True,
)
def run_portfolio_calculations(n_clicks, ticker_list, weights, investment_period, investment_amount):
    if n_clicks==0 or ticker_list is None:
        return PreventUpdate
    
    today = np.datetime64('today', 'D')
    end_date = today - np.timedelta64(1, 'D')
    start_date = today - np.timedelta64(investment_period*365, 'D')
    
    if ctx.triggered_id.purpose == 'calculate':
        statistics = calculate_statistics(ticker_list, str(start_date), str(end_date))
        beta_list = calculate_stock_betas(ticker_list, str(start_date), str(end_date))
        sharpe_ratio_list = calculate_sharpe_ratios(ticker_list, str(start_date), str(end_date))
        sharpe_ratio_list = sharpe_ratio_list.drop('Index')

        beta, sharpe_ratios, cumulative_returns_portfolio, cumulative_returns_index = portfolio_analysis(ticker_list, weights, '^GSPC', str(start_date), str(end_date))
        portfolio_sr = sharpe_ratios.iloc[0]['Sharpe Ratio']
        index_sr = sharpe_ratios.iloc[1]['Sharpe Ratio']
        cumulative_returns = cumulative_returns_portfolio.join(cumulative_returns_index)

        statistics_table = sharpe_ratios.set_index('Asset')
        statistics_table = pd.concat([statistics_table, sharpe_ratio_list], axis=0)
        statistics_table = pd.concat([statistics_table, beta_list], axis=1)
        statistics_table.loc['Index', 'Beta'] = '--'
        statistics_table.loc['Portfolio', 'Beta'] = beta
        statistics_table = statistics_table.reset_index()
        statistics_table = statistics_table.rename(columns={'index': 'Assets'})

        close_price = statistics.drop(columns=['Daily Returns', 'Cumulative Returns'])
        close_price = close_price.pivot_table(values='Close Price', index='Date', columns="Symbol", dropna=True)
        daily_returns = statistics.drop(columns=['Close Price', 'Cumulative Returns'])
        daily_returns = daily_returns.pivot_table(values='Daily Returns', index='Date', columns="Symbol", dropna=True)
        cumulative_returns_stock = statistics.drop(columns=['Close Price', 'Daily Returns'])
        cumulative_returns_stock = cumulative_returns_stock.pivot_table(values='Cumulative Returns', index='Date', columns="Symbol", dropna=True)
        combined_cumulative_returns = pd.concat([cumulative_returns, cumulative_returns_stock], axis=1)
        combined_cumulative_returns = combined_cumulative_returns.rename(columns={'Portfolio Returns': 'Portfolio'})
        sharpe_ratios = statistics_table.drop(columns=['Beta'])
        sharpe_ratios = sharpe_ratios.set_index('Assets')

        ccr_data = []
        for column in combined_cumulative_returns:
            ccr_data.append({'x': combined_cumulative_returns.index, 'y': combined_cumulative_returns[column].to_numpy(), 'type': 'line', 'name': column})

        cp_data = []
        for column in close_price:
            cp_data.append({'x': close_price.index, 'y': close_price[column].to_numpy(), 'type': 'line', 'name': column})

        dr_data = []
        for column in daily_returns:
            dr_data.append({'x': daily_returns.index, 'y': daily_returns[column].to_numpy(), 'type': 'line', 'name': column})

        sr_data = []
        for column in sharpe_ratios:
            sr_data.append({'x': sharpe_ratios[column].index, 'y': sharpe_ratios[column].to_numpy(), 'type': 'bar', 'name': column})

        new_output = [
            dash_table.DataTable(
                statistics_table.to_dict('records'),
                style_table={'color':'black'},
                style_header={'padding-left':'0.5rem', 'text-align':'left'},
                style_data={'padding-left':'0.5rem', 'text-align':'left'},
            ),
            dcc.Graph(
                figure={
                    'data': sr_data,
                    'layout': {
                        'title': 'Sharpe Ratios',
                    }
                },
                className='mt-3',
            ),
            dcc.Graph(
                figure={
                    'data': ccr_data,
                    'layout': {
                        'title': 'Cumulative Returns',
                    }
                },
                className='mt-3',
            ),
            dcc.Graph(
                figure={
                    'data': dr_data,
                    'layout': {
                        'title': 'Daily Returns'
                    }
                },
                className='mt-3',
            ),
            dcc.Graph(
                figure={
                    'data': cp_data,
                    'layout': {
                        'title': 'Daily Closing Price'
                    }
                },
                className='mt-3',
            ),
        ]
    elif ctx.triggered_id.purpose == 'simulate':
        cumulative_returns, return_summary, ci_lower, ci_upper = run_monte_carlo_simulation(
            api_key=alpaca_api_key, 
            secret_key=alpaca_secret_key,
            tickers=ticker_list,
            start_date=start_date,
            end_date=end_date,
            weights=weights,
            num_simulation=500,
            num_years=investment_period,
            investment=investment_amount
        )

        return_summary = pd.DataFrame(return_summary)
        return_summary = return_summary.reset_index()
        return_summary.columns = ['Statistic', 'Value']
        for i in range(len(return_summary)):
            return_summary['Statistic'][i] = return_summary['Statistic'][i].title()

        final_cumulative_returns = pd.DataFrame(cumulative_returns.iloc[-1, :])
        final_cumulative_returns.columns = ['Value']

        fig = px.histogram(
            data_frame=final_cumulative_returns,
            histnorm='density',
            nbins=int(investment_period*5),
            title='Distribution of Final Cumuluative Returns Across All 500 Simulations',
            x='Value',
        )
        fig.update_layout(
            xaxis_title_text='Value',
            yaxis_title_text='Density',
        )
        fig.add_vline(x=return_summary.iloc[8, 1], line_color = 'firebrick')
        fig.add_vline(x=return_summary.iloc[9, 1], line_color = 'firebrick')

        sim_data = []
        for column in cumulative_returns:
            sim_data.append({
                'x': cumulative_returns.index,
                'y': cumulative_returns[column].to_numpy(),
                'type': 'line',
                'name': column
            })

        new_output = [
            html.P(f"There is a 95% chance that, with an initial investment of ${float(investment_amount):.2f}, the current portfolio will result in a total value between ${float(ci_lower):.2f} and ${float(ci_upper):.2f} after {investment_period} year(s)."),
            dash_table.DataTable(
                return_summary.to_dict('records'),
                style_table={'color':'black'},
                style_header={'padding-left':'0.5rem', 'text-align':'left'},
                style_data={'padding-left':'0.5rem', 'text-align':'left'},
            ),
            dcc.Graph(
                figure={
                    'data': sim_data,
                    'layout': {
                        'title': f'500 Simulations of Cumulative Portfolio Return Trajectories Over the Next {investment_period*252} Trading Days. ({investment_period} Years)',
                    }
                },
                className='mt-3',
            ),
            dcc.Graph(
                figure=fig,
                className='mt-3',
            ),
        ]
    return [new_output]