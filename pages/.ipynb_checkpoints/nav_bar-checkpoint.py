import assets
import dash
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import redirect, session
from dash_bootstrap_templates import ThemeSwitchAIO, template_from_url
from imports import auth0_get_user, patch_user_theme_preference
from dotenv import find_dotenv, load_dotenv
from os import environ as env

url_theme1 = dbc.themes.BOOTSTRAP
url_theme2 = dbc.themes.DARKLY

def navbar(user_login):
    if user_login:
        return html.Div(
            dbc.NavbarSimple(
                [
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                [
                                    dbc.NavLink(
                                        page["name"],
                                        href=page["path"],
                                        #active="exact",    
                                    )
                                ]
                            )
                            for page in dash.page_registry.values()
                            if not page["path"].startswith("/account")
                        ],
                    ),
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem(session.get('user')['userinfo']['name'], disabled=True),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Account", href="/account"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Logout", href="/logout", external_link=True),
                        ],
                        label=html.Img(
                            src=session.get('user')['userinfo']['picture'],
                            height=30,
                        ),
                        caret=False,
                        in_navbar=True,
                        align_end=True,
                        toggle_style={
                            'background': 'none',
                            'border': 'none',
                        },
                    ),
                    html.Div(
                        [
                            ThemeSwitchAIO(
                                aio_id="theme",
                                themes=[
                                    url_theme1,
                                    url_theme2
                                ],
                            ),
                        ],
                        style={
                            'margin-left':'16px',
                            'margin-top':'12px',
                        }
                    ),
                ],
                brand=[
                    html.Img(src='assets/logotype_id_dark_30.svg'),
                ],
                class_name='py-2',
                fluid=True,
                id='navbar-simple',
                style={
                    'border-bottom':'2px solid #00bc8c',
                },
            )
        )
    else:
        return html.Div(
            dbc.NavbarSimple(
                [
                    dbc.NavLink("Login", href="/login", external_link=True),
                    html.Div(
                        [
                            ThemeSwitchAIO(
                                aio_id="theme",
                                themes=[
                                    url_theme1,
                                    url_theme2
                                ],
                            ),
                        ],
                        style={
                            'margin-left':'16px',
                            'margin-top':'12px',
                        }
                    ),
                ],
                # brand=[
                #     html.Img(src='assets/logotype_id_dark_30.svg'),
                # ],
                fluid=True,
                id='navbar-simple',
                style={'border-bottom':'2px solid #00bc8c'},
            )
        )

@callback(
    Output('navbar-simple', 'color'),
    Output('navbar-simple', 'dark'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_graph_theme(toggle):
    color = "light" if toggle else "dark"
    dark = False if toggle else True
    return color, dark