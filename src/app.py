import os
import sys

_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path:
    sys.path.insert(0, _src)

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("Behavior & Size", href="/analysis")),
        dbc.NavItem(dbc.NavLink("Seasonal Patterns", href="/seasonal")),
    ],
    brand="Shelter Dog Adoption Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4",
)

app.layout = html.Div([
    navbar,
    dbc.Container(
        dash.page_container,
        fluid=True,
        className="px-4 pb-4",
    ),
])

if __name__ == "__main__":
    app.run(debug=True)
