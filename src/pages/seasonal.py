import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from data_utils import load_data, SIZE_ORDER, SEASON_ORDER

dash.register_page(__name__, path="/seasonal", name="Seasonal Patterns")

df = load_data()

size_options = [{"label": s.capitalize(), "value": s} for s in SIZE_ORDER]
hb_options = [
    {"label": "All", "value": "All"},
    {"label": "Housebroken: Yes", "value": "yes"},
    {"label": "Housebroken: No", "value": "no"},
]


def make_season_bar(size_filter, metric):
    temporal = df.groupby(["season_found", "size"]).agg(
        avg_waiting=("waiting_days", "mean"),
        delay_rate=("delayed", "mean"),
        count=("name", "count"),
    ).reset_index()
    temporal.columns = ["season", "size", "avg_waiting", "delay_rate", "count"]

    data = temporal[temporal["size"] == size_filter].copy()
    data["season"] = pd.Categorical(data["season"], categories=SEASON_ORDER, ordered=True)
    data = data.sort_values("season")

    if metric == "delay_rate":
        y_col = "delay_rate"
        text_vals = data["delay_rate"].apply(lambda x: f"{x*100:.1f}%")
        title = f"Delay Rate by Season — {size_filter.capitalize()} Dogs"
    else:
        y_col = "avg_waiting"
        text_vals = data["avg_waiting"].apply(lambda x: f"{x:.1f}")
        title = f"Avg Waiting Days by Season — {size_filter.capitalize()} Dogs"

    fig = px.bar(
        data,
        x="season",
        y=y_col,
        hover_data={"count": True, "delay_rate": ":.1%", "avg_waiting": ":.1f"},
        title=title,
        labels={
            "delay_rate": "Delay Rate",
            "avg_waiting": "Avg Waiting Days",
            "season": "Season",
            "count": "Number of Dogs",
        },
        color="season",
        color_discrete_sequence=px.colors.qualitative.Safe,
        text=text_vals,
        height=420,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        template="plotly_white",
        margin=dict(t=60, b=40),
        font=dict(size=12),
    )
    return fig


def make_housebroken_bar(hb_filter):
    df_hb = df[df["housebroken"] != "unknown"].copy()
    if hb_filter != "All":
        df_hb = df_hb[df_hb["housebroken"] == hb_filter]

    agg = df_hb.groupby(["housebroken", "size"]).agg(
        avg_waiting_days=("waiting_days", "mean"),
        count=("name", "count"),
    ).reset_index()
    agg["formatted_days"] = agg["avg_waiting_days"].apply(lambda x: f"{x:.2f}")

    title = (
        f"Avg Waiting Days by Size — Housebroken: {hb_filter.upper()}"
        if hb_filter != "All"
        else "Avg Waiting Days by Size — All Housebroken Statuses"
    )

    fig = px.bar(
        agg,
        x="size",
        y="avg_waiting_days",
        color="housebroken",
        barmode="group",
        hover_data={"count": True, "avg_waiting_days": ":.2f"},
        title=title,
        labels={
            "size": "Dog Size",
            "avg_waiting_days": "Avg Waiting Days",
            "housebroken": "Housebroken",
            "count": "Number of Dogs",
        },
        text="formatted_days",
        height=420,
        category_orders={"size": SIZE_ORDER},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=60, b=40),
        font=dict(size=12),
    )
    return fig


def make_delayed_by_size():
    delay_rate_size = df.groupby("size")["delayed"].mean().reset_index()
    delay_rate_size["delayed_pct"] = delay_rate_size["delayed"] * 100
    delay_rate_size["size"] = pd.Categorical(delay_rate_size["size"], categories=SIZE_ORDER, ordered=True)
    delay_rate_size = delay_rate_size.sort_values("size")
    fig = px.bar(
        delay_rate_size,
        x="size",
        y="delayed_pct",
        title="% of Dogs with Delayed Adoption by Size",
        labels={"size": "Dog Size", "delayed_pct": "Delayed (%)"},
        color="size",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        text=delay_rate_size["delayed_pct"].round(1),
        height=380,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=60, b=40),
        font=dict(size=12),
    )
    return fig


layout = html.Div([
    html.H2("Season & housebroken", className="mb-1"),
    html.P("Season and housebroken vs delays.", className="text-muted mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Seasonal Delay Analysis"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Dog Size", className="fw-semibold mb-1"),
                            dcc.Dropdown(
                                id="season-size-dropdown",
                                options=size_options,
                                value="large",
                                clearable=False,
                            ),
                        ], md=4),
                        dbc.Col([
                            html.Label("Metric", className="fw-semibold mb-1"),
                            dcc.RadioItems(
                                id="season-metric-radio",
                                options=[
                                    {"label": "Delay rate", "value": "delay_rate"},
                                    {"label": "Avg waiting days", "value": "avg_waiting"},
                                ],
                                value="delay_rate",
                                inline=True,
                                inputStyle={"marginRight": "4px"},
                                labelStyle={"marginRight": "16px"},
                                className="mt-1",
                            ),
                        ], md=8),
                    ], className="mb-3"),
                    dcc.Graph(id="season-bar", config={"displayModeBar": False}),
                ]),
            ], className="shadow-sm"),
        ),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Avg Waiting Days by Housebroken Status & Size"),
                dbc.CardBody([
                    html.Label("Housebroken Status", className="fw-semibold mb-1"),
                    dcc.Dropdown(
                        id="hb-dropdown",
                        options=hb_options,
                        value="All",
                        clearable=False,
                        className="mb-3",
                    ),
                    dcc.Graph(id="hb-bar", config={"displayModeBar": False}),
                ]),
            ], className="shadow-sm"),
            md=7,
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Delay Rate by Size"),
                dbc.CardBody([
                    dcc.Graph(
                        id="delayed-size-bar",
                        figure=make_delayed_by_size(),
                        config={"displayModeBar": False},
                    ),
                ]),
            ], className="shadow-sm h-100"),
            md=5,
        ),
    ], className="mb-4 g-3"),
])


@callback(
    Output("season-bar", "figure"),
    Input("season-size-dropdown", "value"),
    Input("season-metric-radio", "value"),
)
def update_season_bar(size_filter, metric):
    return make_season_bar(size_filter, metric)


@callback(
    Output("hb-bar", "figure"),
    Input("hb-dropdown", "value"),
)
def update_hb_bar(hb_filter):
    return make_housebroken_bar(hb_filter)