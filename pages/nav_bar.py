import dash
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import redirect, session

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
                                        active="exact",    
                                    )
                                ]
                            )
                            for page in dash.page_registry.values()
                            if not page["path"].startswith("/account-management")
                        ],
                        pills=True,
                    ),
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem(session.get('user')['userinfo']['name'], disabled=True),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Account management", href="/account-management", external_link=True),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Logout", href="/logout", external_link=True)
                        ],
                        label=html.Img(
                            src=session.get('user')['userinfo']['picture'],
                            height=26
                        ),
                        caret=False,
                        color='dark',
                        in_navbar=True,
                        align_end=True,
                        style={'margin-left':'24px'}
                    ),
                ],
                brand="Investor's Dream",
                #brand_href='/',
                brand_style={'color':'#00bc8c', 'font-weight':'bold'},
                color='dark',
                dark=True,
                fluid=True,
            )
        )
    else:
        return html.Div(
            dbc.NavbarSimple(
                [
                    dcc.Link(
                        dbc.NavLink("Login", class_name="me-1"),
                        href="/login",
                        refresh=True
                    )
                ],
                brand="Investor's Dream",
                #brand_href='/',
                color='dark',
                dark=True,
            )
        )