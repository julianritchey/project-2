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

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Set style theme
css = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'

# Create app instance
server = Flask(__name__)
app = Dash(
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
    prevent_initial_callbacks="initial_duplicate",
    server=server,
    use_pages=True,
)
app.config.suppress_callback_exceptions = True
app.title = "Investor's Dream"
server.secret_key = env.get("APP_SECRET_KEY")

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

@server.route("/login")
def login():
    redirect_uri=url_for("callback", _external=True)
    user_login = True
    return oauth.auth0.authorize_redirect(redirect_uri)

@server.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/current-investments")

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

@server.route("/")
def serve_layout():
    if session:
        return dbc.Container([
            navbar(True),
            dash.page_container
        ])
    else:
        return dbc.Container([
            navbar(False),
            html.Div(html.H1("Welcome. Please log in.", className="text-center pt-sm-5"))
        ])

# Set app Layout
app.layout = serve_layout