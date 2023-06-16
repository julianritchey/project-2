# Import dependencies
from .nav_bar import navbar
from dash import ALL, callback, callback_context, dash_table, dcc, html, Input, MATCH, Output, Patch, register_page, State
from dash.exceptions import PreventUpdate
from dotenv import find_dotenv, load_dotenv
from flask import request, session
from imports import AddExchangeConnectionData, auth0_get_user, delete_from_exchange_connections, insert_into_exchange_connections, patch_user_risk_tolerance, risk_prediction_build_df, risk_prediction_load_model, risk_prediction_predict_risk_score, select_all_exchanges_data, select_exchange_connections_data
from os import environ as env
from questrade_api import Questrade
import dash_bootstrap_components as dbc
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objs as go
import sqlalchemy as db
import string
from datetime import datetime, timezone
from dash_bootstrap_templates import ThemeSwitchAIO, template_from_url

""" ROBO ADVISOR AND EMAIL """

from flask import Flask, render_template
import boto3
import os
from datetime import date
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pathlib
import base64
import botocore.session
from botocore.config import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Register page with Dash app
register_page(
    __name__,
    name="Account management"
)


# Access the environment variables
email_address = env.get('EMAIL_ADDRESS')
email_password = env.get('EMAIL_PASSWORD')

""" AWS Lexbot configuration """

# Configure the AWS region
# app.config['AWS_REGION'] = 'us-east-1'

# Create a Botocore session with the AWS region
boto_session = botocore.session.Session()

# Configure the AWS region in the session
boto_session.set_config_variable('region', 'us-east-1')

# Create a client for the Lex bot service using the session
config = Config(region_name='us-east-1')
lex_client = boto_session.create_client('lex-runtime', config=config)

# Set credentials
db_user = env.get('DB_USER')
db_pass = env.get('DB_PASS')
auth0_access_token = env.get('AUTH0_ACCESS_TOKEN')
# aws_access_key_id = env.get('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = env.get('AWS_SECRET_ACCESS_KEY')

# Connect to database
engine = db.create_engine("postgresql://"+db_user+":"+db_pass+"@localhost:5432/fintech2_db")

# Run preliminary API calls
all_exchange_data = select_all_exchanges_data(engine)
all_exchange_data.sort_values(by=['name'], inplace=True)

""" Subpage content """

# Alpaca connection form
alpaca_form = [
    dbc.Row(
        [
            dbc.Label("API key", html_for='alpaca-api-1-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-1-input', 'exchange':'Alpaca'},
                    placeholder="Enter API key",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
    dbc.Row(
        [
            dbc.Label("API secret", html_for='alpaca-api-2-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-2-input', 'exchange':'Alpaca'},
                    placeholder="Enter API secret",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
]

# Bitget connection form
bitget_form = [
    dbc.Row(
        [
            dbc.Label("API key", html_for='bitget-api-1-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-1-input', 'exchange':'Bitget'},
                    placeholder="Enter API key",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
    dbc.Row(
        [
            dbc.Label("API secret", html_for='bitget-api-3-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-3-input', 'exchange':'Bitget'},
                    placeholder="Enter API secret",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
    dbc.Row(
        [
            dbc.Label("API passphrase", html_for='bitget-api-2-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-2-input', 'exchange':'Bitget'},
                    placeholder="Enter API passphrase",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
]

# KuCoin connection form
kucoin_form = [
    dbc.Row(
        [
            dbc.Label("API key", html_for='kucoin-api-1-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-1-input', 'exchange':'KuCoin'},
                    placeholder="Enter API key",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
    dbc.Row(
        [
            dbc.Label("API secret", html_for='kucoin-api-3-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-3-input', 'exchange':'KuCoin'},
                    placeholder="Enter API secret",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
    dbc.Row(
        [
            dbc.Label("API passphrase", html_for='kucoin-api-2-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-2-input', 'exchange':'KuCoin'},
                    placeholder="Enter API passphrase",
                ),
                width=8,
            ),
        ],
        className='mb-3',
    ),
]

# Questrade connection form
questrade_form = [
    dbc.Row(
        [
            dbc.Label("Refresh token", html_for='questrade-api-1-input', width=4),
            dbc.Col(
                dbc.Input(
                    autocomplete='off',
                    id={'purpose':'api-3-input', 'exchange':'Questrade Inc.'},
                    placeholder="Enter refresh token",
                ),
                width=12,
            ),
        ],
        className='mb-3',
    ),
]

# Generate modal for adding connections
add_connection_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("New connection"),
            close_button=False
        ),
        dbc.ModalBody(
            [
                dbc.Form(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Exchange", html_for='exchange-input', width=4),
                                dbc.Col(
                                    dbc.Select(
                                        options=[
                                            {'label': row['name'], 'value': row['name']}
                                            for index, row in all_exchange_data.iterrows()
                                        ],
                                        id='exchange-input',
                                        name='exchange-input-name',
                                        placeholder="Select exchange",
                                    ),
                                    width=8,
                                ),
                            ],
                            className='mb-3',
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Collapse(
                                            dbc.Alert(
                                                [
                                                    html.A(id='api-instructions-alert'),
                                                ],
                                                color='info',
                                            ),
                                            id='api-instructions-collapse',
                                            is_open=False,
                                        )
                                    ],
                                )
                            ]
                        ),
                        html.Div(id='connection-form-div'),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Alert(
                                            color='danger',
                                            id='connection-error-alert',
                                            is_open=False,
                                        ),
                                    ],
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Add connection",
                                    disabled=True,
                                    id='add-connection-button',
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
                                    "Cancel",
                                    color='danger',
                                    id='cancel-connection-modal-button',
                                    n_clicks=0,
                                    outline=True,
                                ),
                            ],
                            style={
                                'text-align':'right',
                            },
                            width=6,
                        ),
                    ],
                    class_name='vw-100',
                ),
            ],
        ),
    ],
    backdrop='static',
    id='add-connection-modal',
    is_open=False,
)

# Generate modal for editing connections
edit_connection_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Edit connection"),
            close_button=False
        ),
        dbc.ModalBody(
            [
                dbc.Form(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Exchange", html_for='exchange-input1', width=3),
                                dbc.Col(
                                    dbc.Input(
                                        autocomplete='off',
                                        disabled=True,
                                        id='edit-exchange-input',
                                        type='text'
                                    ),
                                    width=9,
                                ),
                            ],
                            className='mb-3',
                        ),
                        dbc.Row(
                            [
                                dbc.Label("API key", html_for='api-1-input1', width=3),
                                dbc.Col(
                                    dbc.Input(
                                        autocomplete='off',
                                        disabled=True,
                                        id='edit-api-1-input',
                                        type='text'
                                    ),
                                    width=9,
                                ),
                            ],
                            className='mb-3',
                        ),
                    ],
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Remove connection",
                                    color = 'danger',
                                    id = 'remove-connection-button',
                                    n_clicks = 0,
                                ),
                            ],
                            style={'text-align':'left'},
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Cancel",
                                    color = 'danger',
                                    id = 'cancel-edit-connection-modal-button',
                                    n_clicks = 0,
                                    outline = True
                                ),
                            ],
                            style={'text-align':'right'},
                            width=6,
                        ),
                    ],
                    class_name='vw-100',
                ),
            ],
        ),
    ],
    backdrop='static',
    id='edit-connection-modal',
    is_open=False,
)

# Generate modal for confirming the removal of connections
remove_connection_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Confirm removal"),
            close_button=False
        ),
        dbc.ModalBody(
            [
                dbc.Form(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Alert(
                                        "Are you sure you wish to remove this connection? This cannot be undone.",
                                        color='danger',
                                    ),
                                ),
                            ],
                            className='mb-3',
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        "To confirm, type the following in the box below.",
                                        dbc.Alert(
                                            class_name='text-center',
                                            color='info',
                                            id='remove-connection-alert',
                                        ),
                                        dbc.Input(
                                            autocomplete='off',
                                            class_name='text-center',
                                            id='remove-connection-input',
                                            type='text'
                                        ),
                                    ],
                                ),
                            ],
                            className='mb-3',
                        ),
                    ]
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Confirm removal",
                                    color = 'danger',
                                    disabled=True,
                                    id = 'confirm-remove-connection-button',
                                    n_clicks = 0,
                                ),
                            ],
                            style={'text-align':'left'},
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Cancel",
                                    color = 'danger',
                                    id = 'cancel-remove-connection-modal-button',
                                    n_clicks = 0,
                                    outline = True
                                ),
                            ],
                            style={'text-align':'right'},
                            width=6,
                        ),
                    ],
                    class_name='vw-100',
                ),
            ],
        ),
    ],
    backdrop='static',
    id='remove-connection-modal',
    is_open=False,
)

# Generate modal for changing risk tolerance
change_risk_tolerance_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Change risk tolerance"),
            close_button=False
        ),
        dbc.ModalBody(
            [
                dbc.Form(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Risk tolerance", html_for='change-risk-tolerance-input', width=4),
                                dbc.Col(
                                    dbc.Select(
                                        options=[
                                            {'label': '1 (very low risk)', 'value': '1 (very low risk)'},
                                            {'label': '2 (low risk)', 'value': '2 (low risk)'},
                                            {'label': '3 (moderate risk)', 'value': '3 (moderate risk)'},
                                            {'label': '4 (high risk)', 'value': '4 (high risk)'},
                                            {'label': '5 (very high risk)', 'value': '5 (very high risk)'},
                                        ],
                                        id='change-risk-tolerance-input',
                                        placeholder="Select risk tolerance level",
                                    ),
                                    width=8,
                                ),
                            ],
                            className='mb-3',
                        ),
                    ]
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Change",
                                    className='ms-auto',
                                    id='change-risk-tolerance-button',
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
                                    "Cancel",
                                    color='danger',
                                    id='close-risk-modal-button',
                                    n_clicks=0,
                                    outline=True,
                                ),
                            ],
                            style={
                                'text-align':'left',
                            },
                            width=6,
                        ),
                    ],
                ),
            ],
        ),
    ],
    backdrop='static',
    id='change-risk-tolerance-modal',
    is_open=False,
)

# Generate modal for changing risk tolerance
robo_advisor_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Risk tolerance advisor"),
            close_button=False
        ),
        dbc.ModalBody(
            [
                dbc.Form(
                    [
                        html.Div(id='robo-advisor-chat-log', className='flex-column mb-3 px-2 py-1 rounded-3', style={'border':'1px solid rgb(120,120,120)'}),
                        dbc.Row(
                            [
                                dbc.Label("User input", html_for='robo-advisor-user-input', width=4),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            autocomplete='off',
                                            id='robo-advisor-user-input',
                                            placeholder='Type your message...',
                                            type='text'
                                        ),
                                    ],
                                    width=8,
                                ),
                            ],
                            className='mb-3',
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Enter",
                                            className='w-100',
                                            id='robo-advisor-user-input-button',
                                        ),
                                    ],
                                    style={
                                        'text-align':'center',
                                    },
                                ),
                            ],
                        ),
                    ],
                    action='/chat',
                    id="chat-form",
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Submit",
                                    disabled=True,
                                    id='submit-robo-advisor-chat-button',
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
                                    "Cancel",
                                    color='danger',
                                    id='close-robo-advisor-button',
                                    n_clicks=0,
                                    outline=True,
                                ),
                            ],
                            style={
                                'text-align':'right',
                            },
                            width=6,
                        ),
                    ],
                    class_name='vw-100',
                ),
            ],
        ),
    ],
    backdrop='static',
    id='robo-advisor-modal',
    is_open=False,
)

""" Set page Layout """

# Define layout function
def layout():

    # Get existing connections from database
    exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
    
    # Return layout
    return html.Div(
        [
            # Page content
            dbc.Row(
                [
                    # Side bar
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        id='account-radios',
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
                                        options=[
                                            {'label': 'Connections', 'value': 'connections'},
                                            {'label': 'Profile', 'value': 'profile'},
                                        ],
                                        style={
                                            'before':'hidden',
                                            'display':'block',
                                            'flex-direction':'column',
                                            'margin-left':'0px',
                                            'padding-left':'0px',
                                        },
                                        value='connections',
                                    ),
                                ],
                                className='radio-group ms-0 ps-0 pt-3',
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
                    
                    # Main page
                    dbc.Col(
                        [
                            html.H2(["Account"], className='mb-0 mt-3'),
                            html.Div(id='account-subpage-content'),
                        ],
                        class_name='px-4',
                        width=10,
                    ),
                ],
                class_name='vw-100',
            ),
            
            # Page alert
            dbc.Alert(
                "Connection added successfully!",
                class_name='fixed-bottom m-0 rounded-0',
                dismissable=True,
                # duration=4000,
                id='page_alert',
                is_open=False,
            ),

            # Subpage data stores
            dcc.Store(
                data=exchange_connections_data.to_dict(),
                id='exchange-connections-store',
            ),
            dcc.Store(
                id='edit-exchange-connection-store',
            ),
            dcc.Store(
                id='user-risk-tolerance-store',
            ),
            dcc.Store(
                id='robo-advisor-chat-store',
            ),
            dcc.Store(
                data=False,
                id='account-content-trigger-store',
            ),

            # Subpage modals
            add_connection_modal,
            edit_connection_modal,
            remove_connection_modal,

            # Subpage modals
            change_risk_tolerance_modal,
            robo_advisor_modal,
        ],
    )

""" Define callback functions """

# Callback for changing page tabs
@callback(
    Output('account-subpage-content', 'children'),
    Output('user-risk-tolerance-store', 'data'),
    Output('account-content-trigger-store', 'data'),
    Input('account-radios', 'value'),
    Input('account-content-trigger-store', 'data'),
    State('exchange-connections-store', 'data'),
)
def change_page_content_cb(value, trigger, connections):
    if callback_context.triggered_id=='account-content-trigger-store' and trigger==False:
        return PreventUpdate()
    content = None
    user_id = session.get('user')['userinfo']['sub']
    user_name = session.get('user')['userinfo']['name']
    user_email = session.get('user')['userinfo']['email']
    user_data = auth0_get_user(auth0_access_token, user_id)
    user_risk_tolerance = ''
    if 'user_metadata' in user_data and 'risk_tolerance' in user_data['user_metadata']:
        user_risk_tolerance = user_data['user_metadata']['risk_tolerance']
    if value=='connections':
        connections = pd.DataFrame.from_dict(connections)
        connections['date_added'] = pd.to_datetime(connections['date_added'])
        subpage_body = None
        if not connections.empty:
            table_header = [
                html.Thead(
                    [
                        html.Tr(
                            [
                                html.Th("Exchange"),
                                html.Th("Access token/API key"),
                                html.Th("Date added"),
                                html.Th("Edit", className='text-center'),
                            ]
                        )
                    ]
                )
            ]
            table_rows = []
            exchange_list = []
            for index, row in connections.iterrows():
                exchange = all_exchange_data.loc[all_exchange_data['exchange_id']==row['exchange_id'], 'name'].values[0]
                table_rows.append(
                    html.Tr(
                        [
                            html.Td(exchange),
                            html.Td(row['api_1']),
                            html.Td(row['date_added'].strftime('%Y-%m-%d')),
                            html.Td(
                                html.A(
                                    className='bi bi-pencil-square',
                                    id={
                                        'type':'edit-connection-a',
                                        'exconn-id':row['exconn_id']
                                    },
                                    n_clicks=0,
                                    role='button',
                                ),
                                className='text-center',
                            ),
                        ]
                    )
                )
            table_body = [html.Tbody(table_rows)]
            subpage_body = html.Div(
                [
                    dbc.Table(
                        table_header + table_body,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        striped=True,
                    ),
                ]
            )
        else:
            subpage_body = html.Div(
                [
                    html.P("You do not have any connections."),
                ]
            )
        content = html.Div(
            [
                # Subpage content
                html.H5("Connections", className='mb-3'),
                subpage_body,
                dbc.Button("Add connection", id='open-connection-modal-button', n_clicks=0),
                dcc.Graph(
                    className='mt-3',
                    id='exchange-locations-graph',
                ),
            ]
        ),
    elif value=='profile':
        content = html.Div(
            [
                html.H5("Profile", className='mb-3'),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Name"),
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Input(
                                    autocomplete='off',
                                    disabled=True,
                                    placeholder="Name",
                                    value=user_name,
                                ),
                                dbc.FormText("Derived from your social login."),
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
                                dbc.Label("Email"),
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Input(
                                    autocomplete='off',
                                    disabled=True,
                                    placeholder="Email",
                                    value=user_email,
                                ),
                                dbc.FormText("Derived from your social login."),
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
                                dbc.Label("Risk tolerance"),
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            autocomplete='off',
                                            disabled=True,
                                            id='account-user-risk-tolerance',
                                            placeholder="No risk tolerance set",
                                            value=user_risk_tolerance
                                        ),
                                        dbc.Button(
                                            "Change",
                                            id='open-risk-modal-button',
                                            n_clicks=0,
                                        ),
                                    ],
                                ),
                            ],
                            width=9,
                        ),
                    ],
                    className='mb-3',
                ),
                dbc.Alert(
                    [
                        "Unsure of your risk tolerance? ",
                        html.A("Click here", className='text-decoration-underline', id='robo-advisor-link', n_clicks=0, role='button'),
                        " to have our robo-advisor help you decide!",
                    ],
                    color='info',
                ),
            ]
        )
    if trigger:
        trigger=False
    return content, user_risk_tolerance, trigger

# Callback for displaying the Add Connection modal
@callback(
    Output('add-connection-modal', 'is_open', allow_duplicate=True),
    Output('exchange-input', 'value'),
    Output('connection-error-alert', 'is_open', allow_duplicate=True),
    Input('open-connection-modal-button', 'n_clicks'),
    Input('cancel-connection-modal-button', 'n_clicks'),
    State('add-connection-modal', 'is_open'),
    prevent_initial_call=True
)
def display_add_connection_modal_cb(n1, n2, is_open):
    if n1 and callback_context.triggered_id=='open-connection-modal-button':
        return True, '', False
    else:
        return False, '', False

# Callback for displaying the API Instructions alert
@callback(
    Output('api-instructions-collapse', 'is_open'),
    Output('api-instructions-alert', 'children'),
    Output('connection-form-div', 'children'),
    Input('exchange-input', 'value'),
    State('api-instructions-collapse', 'is_open'),
    prevent_initial_call=True
)
def display_api_instructions_cb(exchange, is_open):
    if exchange:
        api_instructions = all_exchange_data.loc[all_exchange_data['name']==exchange, 'api_instructions'].values[0]
        connection_form = None
        instructions = None
        if exchange == 'Alpaca':
            instructions = [
                "To connect your Alpaca account, you will need to generate, and provide us with, an API key and an API secret. Please follow ",
                html.A("these instructions", href=api_instructions, target='_blank'),
                " to complete this process, then enter the information below.",
            ]
            connection_form = alpaca_form
        elif exchange == 'Bitget':
            instructions = [
                "To connect your Bitget account, you will need to generate, and provide us with, an API key, an API secret and an API passphrase. Please follow ",
                html.A("these instructions", href=api_instructions, target='_blank'),
                " to complete this process, then enter the information below.",
            ]
            connection_form = bitget_form
        elif exchange == 'KuCoin':
            instructions = [
                "To connect your KuCoin account, you will need to generate, and provide us with, an API key, an API secret and an API passphrase. Please follow ",
                html.A("these instructions", href=api_instructions, target='_blank'),
                " to complete this process, then enter the information below.",
            ]
            connection_form = kucoin_form
        elif exchange == 'Questrade Inc.':
            instructions = [
                "To connect your Questrade account, you will need to generate, and provide us with, a refresh token. Please follow ",
                html.A("these instructions", href=api_instructions, target='_blank'),
                " to complete this process, then enter the information below.",
            ]
            connection_form = questrade_form
        return True, instructions, connection_form
    else:
        return False, "", []

# Callback for enabling the Add Connection button
@callback(
    Output('add-connection-button', 'disabled'),
    Input({'purpose':'api-1-input', 'exchange':ALL}, 'value'),
    Input({'purpose':'api-2-input', 'exchange':ALL}, 'value'),
    Input({'purpose':'api-3-input', 'exchange':ALL}, 'value'),
    State('exchange-input', 'value'),
    prevent_initial_call=True
)
def enable_add_connection_button_cb(input_1, input_2, input_3, exchange):
    if input_1 or input_2 or input_3:
        if exchange == 'Questrade Inc.':
            if input_3[0]:
                return False
            else:
                return True
        elif exchange == 'Alpaca':
            if input_1[0] and input_2[0]:
                return False
            else:
                return True
        else:
            if input_1[0] and input_2[0] and input_3[0]:
                return False
            else:
                return True
    else:
        return True

# Callback for adding a new exchange connection
@callback(
    Output('add-connection-modal', 'is_open'),
    Output('connection-error-alert', 'is_open'),
    Output('connection-error-alert', 'children'),
    Output('page_alert', 'children', allow_duplicate=True),
    Output('page_alert', 'is_open', allow_duplicate=True),
    Output('exchange-connections-store', 'data'),
    Output('account-content-trigger-store', 'data', allow_duplicate=True),
    Input('add-connection-button', 'n_clicks'),
    State('add-connection-modal', 'is_open'),
    State({'purpose':'api-1-input', 'exchange':ALL}, 'value'),
    State({'purpose':'api-2-input', 'exchange':ALL}, 'value'),
    State({'purpose':'api-3-input', 'exchange':ALL}, 'value'),
    State('exchange-connections-store', 'data'),
    State('exchange-input', 'value'),
    State('account-radios', 'value'),
    State('account-content-trigger-store', 'data'),
    prevent_initial_call=True
)
def add_connection_cb(n, is_open, api_1, api_2, api_3, connections, exchange, subpage, trigger):
    exchange_abbr = exchange.translate(str.maketrans('', '', string.punctuation))
    exchange_abbr = exchange_abbr.translate(str.maketrans('', '', ' '))
    input_data = [api_1, api_2, api_3]
    account = getattr(AddExchangeConnectionData, exchange_abbr)
    api_data = account(input_data)
    exchange_id = all_exchange_data.loc[all_exchange_data['name']==exchange, 'exchange_id'].values[0]
    connections = pd.DataFrame.from_dict(connections)
    if api_data==None:
        return True, True, "Connection error. Please confirm your credentials.", "", False, connections.to_dict(), False
    elif len(connections) > 0 and api_data[0] in connections.loc[connections['exchange_id']==exchange_id, 'api_1'].values:
        return True, True, "Connection already made with API key.", "", False, connections.to_dict(), False
    else:
        message = "Connection added successfully!"
        user_id = session.get('user')['userinfo']['sub']
        utc_dt = datetime.utcnow()
        insert_into_exchange_connections(exchange_id, user_id, utc_dt, api_data[0], api_data[1], api_data[2], api_data[3], engine)
        new_exchange_connections_data = select_exchange_connections_data(session.get('user')['userinfo']['sub'], engine)
        return False, False, "", message, True, new_exchange_connections_data.to_dict(), True

# Callback for toggling the display of the Edit Connection modal and its contents
@callback(
    Output('edit-connection-modal', 'is_open', allow_duplicate=True),
    Output('edit-api-1-input', 'value', allow_duplicate=True),
    Output('edit-exchange-input', 'value', allow_duplicate=True),
    Output('edit-exchange-connection-store', 'data', allow_duplicate=True),
    Input({'type':'edit-connection-a', 'exconn-id':ALL}, 'n_clicks'),
    State('edit-connection-modal', 'is_open'),
    State('exchange-connections-store', 'data'),
    prevent_initial_call=True
)
def edit_connection_cb(n1, is_open, connections):
    n3 = 0
    for n in n1:
        if n > 0:
            n3 = n
            break
    if n3:
        triggered_id = callback_context.triggered_id['exconn-id']
        connections = pd.DataFrame.from_dict(connections)
        connection = connections.loc[connections['exconn_id']==triggered_id]
        api_1 = connection['api_1'].values[0]
        exchange_id = connection['exchange_id'].values[0]
        exchange_name = all_exchange_data.loc[all_exchange_data['exchange_id']==exchange_id, 'name'].values[0]
        return True, api_1, exchange_name, connection.to_dict()
    else:
        return False, "", "", ""
    
@callback(
    Output('edit-connection-modal', 'is_open', allow_duplicate=True),
    Output('edit-api-1-input', 'value', allow_duplicate=True),
    Output('edit-exchange-input', 'value', allow_duplicate=True),
    Output('edit-exchange-connection-store', 'data', allow_duplicate=True),
    Input('cancel-edit-connection-modal-button', 'n_clicks'),
    prevent_initial_call=True
)
def close_edit_connection_cb(n):
    return False, "", "", ""
    
# Callback for toggling the display of the Remove Connection modal and its contents
@callback(
    Output('remove-connection-modal', 'is_open', allow_duplicate=True),
    Output('remove-connection-alert', 'children'),
    Output('edit-connection-modal', 'is_open'),
    Input('remove-connection-button', 'n_clicks'),
    Input('cancel-remove-connection-modal-button', 'n_clicks'),
    State('edit-api-1-input', 'value'),
    State('remove-connection-modal', 'is_open'),
    prevent_initial_call=True
)
def remove_connection_cb(n1, n2, api_1, is_open):
    if is_open:
        return False, "", True
    else:
        confirmation = "delete-"+api_1
        return True, confirmation, False

# Callback for verifying the connection removal confirmation input
@callback(
    Output('confirm-remove-connection-button', 'disabled'),
    Input('remove-connection-input', 'value'),
    State('remove-connection-alert', 'children'),
    prevent_initial_call=True
)
def verify_removal_confirmation_cb(value, confirmation):
    if value == confirmation:
        return False
    else:
        return True

# Callback for removing exchange connection
@callback(
    Output('remove-connection-modal', 'is_open'),
    Output('page_alert', 'children', allow_duplicate=True),
    Output('page_alert', 'is_open', allow_duplicate=True),
    Input('confirm-remove-connection-button', 'n_clicks'),
    State('edit-exchange-connection-store', 'data'),
    prevent_initial_call=True
)
def remove_connection_cb(n, data):
    exchange_data = pd.DataFrame.from_dict(data)
    exconn_id = exchange_data['exconn_id'].values[0]
    result = delete_from_exchange_connections(exconn_id, engine)
    if result:
        message = "Connection removed successfully!"
        return False, message, True
    else:
        return True, "", False

# Callback for switching graph templates based on application theme
@callback(
    Output('exchange-locations-graph', 'figure'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
    State('exchange-connections-store', 'data'),
)
def update_exchange_locations_figure_cb(theme_toggle, connections):
    connections = pd.DataFrame.from_dict(connections)
    fig = None
    if len(connections) > 0:
        exchange_ids = connections['exchange_id'].values
        connected_exchange_data = pd.DataFrame()
        for exchange_id in exchange_ids:
            connected_exchange_data = pd.concat([connected_exchange_data, all_exchange_data.loc[all_exchange_data['exchange_id']==exchange_id]])
        template = 'bootstrap' if theme_toggle else 'darkly'
        fig = go.Figure(
            data = go.Scattergeo(
                lat = connected_exchange_data['latitude'],
                lon = connected_exchange_data['longitude'],
                marker = {
                    'color': '#00bc8c',
                    'size': 20
                },
                text = connected_exchange_data['name'],
            ),
            layout = go.Layout(
                geo = go.layout.Geo(
                    projection_type='natural earth',
                    showcountries=True,
                    countrycolor='rgba(120, 120, 120, 0.1)'
                ),
                height = 400,
                margin = {
                    'b':30,
                    'l':0,
                    'r':0,
                    't':30,
                },
                paper_bgcolor = 'rgba(255,255,255,0)',
                template = template,
                # title = {
                #     'text': "Exchange Locations",
                #     'x': 0.5,
                #     'xanchor': 'center',
                #     'y': 0.02,
                #     'yanchor': 'bottom',
                # },
            )
        )
    else:
        template = 'bootstrap' if theme_toggle else 'darkly'
        fig = go.Figure(
            data = go.Scattergeo(
            ),
            layout = go.Layout(
                geo = go.layout.Geo(
                    projection_type='natural earth',
                    showcountries=True,
                    countrycolor='rgba(120, 120, 120, 0.1)'
                ),
                height = 400,
                margin = {
                    'b':30,
                    'l':0,
                    'r':0,
                    't':30,
                },
                paper_bgcolor = 'rgba(255,255,255,0)',
                template = template,
            )
        )
    return fig

# Callback for toggling the display of the Change Risk Tolerance modal and its contents
@callback(
    Output('change-risk-tolerance-modal', 'is_open', allow_duplicate=True),
    Output('change-risk-tolerance-input', 'value'),
    Input('open-risk-modal-button', 'n_clicks'),
    State('change-risk-tolerance-modal', 'is_open'),
    State('user-risk-tolerance-store', 'data'),
    prevent_initial_call=True
)
def open_risk_tolerance_modal_cb(n, is_open, risk_level):
    if n:
        return True, risk_level
    else:
        return False, risk_level

@callback(
    Output('change-risk-tolerance-modal', 'is_open', allow_duplicate=True),
    Input('close-risk-modal-button', 'n_clicks'),
    prevent_initial_call=True
)
def close_risk_tolerance_modal_cb(n):
    if n:
        return False
    else:
        return True

# Callback for storing risk tolerance level
@callback(
    Output('user-risk-tolerance-store', 'data', allow_duplicate=True),
    Input('change-risk-tolerance-input', 'value'),
    prevent_initial_call=True
)
def store_risk_tolerance_cb(value):
    return value
    
# Callback for changing risk tolerance level
@callback(
    Output('change-risk-tolerance-modal', 'is_open'),
    Output('page_alert', 'children'),
    Output('page_alert', 'is_open'),
    Output('account-user-risk-tolerance', 'value'),
    Input('change-risk-tolerance-button', 'n_clicks'),
    State('user-risk-tolerance-store', 'data'),
    State('account-user-risk-tolerance', 'value'),
    prevent_initial_call=True
)
def change_risk_tolerance_cb(n, new_risk_level, old_risk_level):
    if n:
        print(new_risk_level)
        print(old_risk_level)
        user_id = session.get('user')['userinfo']['sub']
        response = patch_user_risk_tolerance(auth0_access_token, new_risk_level, user_id)
        if response:
            message = "Risk tolerance changed successfully!"
            return False, message, True, new_risk_level
        else:
            return True, '', False, old_risk_level
    else:
        return True, '', False, old_risk_level
    
# Callback for opening Robo-Advisor modal
@callback(
    Output('robo-advisor-modal', 'is_open', allow_duplicate=True),
    Output('robo-advisor-chat-log', 'children', allow_duplicate=True),
    Output('robo-advisor-user-input', 'disabled', allow_duplicate=True),
    Output('robo-advisor-user-input-button', 'disabled', allow_duplicate=True),
    Output('submit-robo-advisor-chat-button', 'disabled', allow_duplicate=True),
    Input('robo-advisor-link', 'n_clicks'),
    prevent_initial_call=True
)
def open_robo_advisor(n):
    chat = []
    if n:
        chat_post('StartChat')
        response = chat_post(session.get('user')['userinfo']['given_name'])
        chat.append(dbc.Row([dbc.Col([html.Div(response['message'], className='bg-light d-inline-block me-auto my-1 px-2 py-1 rounded-3 text-dark')], width=10),dbc.Col(width=2)]))
        return True, chat, False, False, True
    else:
        return False, chat, False, False, True

# Callback for closing Robo-Advisor modal
@callback(
    Output('robo-advisor-modal', 'is_open'),
    Output('robo-advisor-user-input', 'value', allow_duplicate=True),
    Input('close-robo-advisor-button', 'n_clicks'),
    State('robo-advisor-user-input', 'value'),
    prevent_initial_call=True
)
def open_robo_advisor(n, value):
    if n:
        close_lex_session()
        return False, None
    else:
        return True, value

# Callback for providing user inputs to the robo advisor
@callback(
    Output('robo-advisor-chat-log', 'children'),
    Output('robo-advisor-user-input', 'value'),
    Output('robo-advisor-user-input', 'disabled'),
    Output('robo-advisor-user-input-button', 'disabled'),
    Output('submit-robo-advisor-chat-button', 'disabled'),
    Output('robo-advisor-chat-store', 'data'),
    Input('robo-advisor-user-input-button', 'n_clicks'),
    State('robo-advisor-user-input', 'value'),
    State('robo-advisor-chat-log', 'children'),
    prevent_initial_call=True
)
def enter_robo_advisor_user_input(n, value, chat):
    if not chat:
        chat = []
    advisor_complete = False
    if n:
        value_component = dbc.Row([dbc.Col(width=2),dbc.Col([html.Div(value, className='bg-primary d-inline-block ms-auto my-1 px-2 py-1 rounded-3 text-white')], style={'text-align':'right'}, width=10)])
        chat.append(value_component)
        response = chat_post(value)
        message = response['message']
        if message == 'Thank you. Please click "Submit" to get your risk tolerance evaluated.':
            advisor_complete = True
            risk_score = calculate_risk_tolerance(response['slots'])
            message = "Thank you. Based on the information you have provided, I predict that you can tolerate "+risk_score.lower()+". Please close this popup and adjust your risk tolerance as you see fit. Should you wish to have a copy of this chat for your future reference, click the Submit button below."
            response['slots']['risk_score'] = risk_score
        message_component = dbc.Row([dbc.Col([html.Div(message, className='bg-light d-inline-block me-auto my-1 px-2 py-1 rounded-3 text-dark')], width=10),dbc.Col(width=2)])
        chat.append(message_component)
        return chat, '', advisor_complete, advisor_complete, not advisor_complete, response['slots']
    else:
        return None, value, advisor_complete, advisor_complete, not advisor_complete, None

@callback(
    Output('robo-advisor-modal', 'is_open', allow_duplicate=True),
    Input('submit-robo-advisor-chat-button', 'n_clicks'),
    State('robo-advisor-chat-store', 'data'),
    prevent_initial_call=True
)
def submit_robo_advisor_chat(n, chat):
    if n:
        message = (""
                   "<h3>Investor's Dream</h3>"
                   "<p>Risk tolerance robo-advisor responses</p>"
                   "<br>"
                   "<p>First name: "+chat['firstName']+"</p>"
                   "<p>Age: "+chat['age']+"</p>"
                   "<p>Net worth: "+chat['networth']+"</p>"
                   "<p>Income: "+chat['income']+"</p>"
                   "<p>Married: "+chat['marriage']+"</p>"
                   "<p>Kids: "+chat['kids']+"</p>"
                   "<br>"
                   "<p>Risk tolerance: "+chat['risk_score']+"</p>"
                   "")
        subject = "PROFILE UPDATE: Risk Tolerance"
        send_email(message, subject)
        return False
    else:
        return True

def chat_post(user_input):
    firstName = ''
    age = ''
    kids = ''
    networth = ''
    income = ''
    marriage = ''
    
    # Generate a unique user ID
    user_id = session.get('user')['userinfo']['given_name'].replace(' ', '')

    # Send user input to the bot and receive the response
    response = lex_client.post_text(
        botName= 'RiskScore',
        botAlias= '$LATEST',
        userId= user_id,
        inputText= user_input
    )

    # Extract slot values from the Lex response
    slots = response['slots']
    firstName = slots.get('firstName') 
    age = slots.get('age')
    kids = slots.get('kids')
    networth = slots.get('networth')
    income = slots.get('income')
    marriage = slots.get('marriage')

    return response

def close_lex_session():
    lex_client.delete_session(
        botName= 'RiskScore',
        botAlias= '$LATEST',
        userId= session.get('user')['userinfo']['given_name'].replace(' ', ''),
    )

def send_email(message, subject):
    recipient = session.get('user')['userinfo']['email']
    subject = subject
    
    email_body = message
    
    email_server_host = 'smtp.gmail.com'
    port = 587
    sender = email_address
    password = email_password
    
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(email_body, 'html'))
    
    server = smtplib.SMTP(email_server_host, port)
    server.ehlo()
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, msg.as_string())
    server.close()
    
    return 'Email sent successfully!'

def calculate_risk_tolerance(chat):
    risk_df = risk_prediction_build_df(chat['age'], chat['kids'], chat['networth'], chat['income'], chat['marriage'])
    risk_model = risk_prediction_load_model('risk_ml_gradient_balanced')
    risk_score = risk_prediction_predict_risk_score(risk_model, risk_df)
    return risk_score