# Import dependencies
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

from dash import Dash, Input, Output, State, dcc, html
from flask import Flask, redirect, render_template, session, url_for
import dash
import dash_bootstrap_components as dbc
from pages.nav_bar import navbar

import boto3
import botocore.session
from botocore.config import Config

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Set style theme
bi_css = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css'
dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'

# Create app instance
server = Flask(__name__)
app = Dash(
    external_stylesheets=[bi_css, dbc_css, dbc.themes.BOOTSTRAP],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
    prevent_initial_callbacks='initial_duplicate',
    server=server,
    use_pages=True,
)
app.config.suppress_callback_exceptions = True
app.title = "Investor's Dream"
server.secret_key = env.get("APP_SECRET_KEY")

""" ROBO ADVISOR CONFIG """

# # Configure the AWS region
# server.config['AWS_REGION'] = 'us-east-1'  

# # Create a Botocore session with the AWS region
# boto_session = botocore.session.Session()

# # Configure the AWS region in the session
# boto_session.set_config_variable('region', server.config['AWS_REGION'])

# # Create a client for the Lex bot service using the session
# config = Config(region_name=server.config['AWS_REGION'])
# lex_client = boto_session.create_client('lex-runtime', config=config)

# # Set global variables
# firstName = ''
# dateOfBirth = ''
# kids = 0
# networth = 0
# income = 0
# marriage = ''

""" OAUTH CONFIG """

# Initialize OAuth
oauth = OAuth(server)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

""" SERVER ROUTING """

@server.route("/login")
def login():
    redirect_uri=url_for("callback", _external=True)
    user_login = True
    return oauth.auth0.authorize_redirect(redirect_uri)

@server.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@server.route("/logout")
def logout():
    session.clear()
    user_login = False
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("/", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# @server.route('/chat', methods=['POST'])
# def chat_post():

#     global firstName, dateOfBirth, kids, networth, income, marriage

#     user_input = request.form['user_input']

#     # Generate a unique user ID
#     user_id = "test"

#     networth = 20

#     # Send user input to the bot and receive the response
#     response = lex_client.post_text(
#         botName= 'RiskScore',
#         botAlias= '$LATEST',
#         userId= user_id,
#         inputText= user_input
#     )

#     # Extract slot values from the Lex response
#     slots = response['slots']
#     firstName = slots.get('firstName') 
#     dateOfBirth = slots.get('dateOfBirth')
#     kids = slots.get('kids')
#     networth = slots.get('networth')
#     income = slots.get('income')
#     marriage = slots.get('marriage')


#     # Extract the bot's response from the API response
#     bot_response = response['message']

#     return bot_response

@server.route("/")
def dashboard():
    return redirect("/")

def serve_layout():
    if session:
        return html.Div(
            [
                navbar(True),
                dash.page_container,
            ],
            className='mx-0 px-0'
        )
    else:
        return html.Div(
            [
                navbar(False),
                dbc.Container(
                    [
                        html.Img(
                            className='my-4',
                            src='assets/logotype_id_light_90.svg',
                        ),
                        html.H1(
                            "Make your dream a reality.",
                            #className="pt-sm-5",
                            style={
                                'color':'white'
                            }
                        ),
                        html.H3(
                            [
                                dcc.Link(
                                    "Sign up now.",
                                    className="pt-2",
                                    href="/login",
                                    refresh=True,
                                    style={
                                        'color':'white'
                                    }
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            className='vh-100',
            style={
                'background-image': 'url(/assets/1504342112-huge.jpg)',
                'background-size': 'contain',
                'background-repeat': 'no-repeat',
            },
        )

# Set app Layout
app.layout = serve_layout