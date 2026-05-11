import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from data_utils import load_data, SIZE_ORDER, AGE_GROUPS

dash.register_page(__name__, path="/", name="Overview")

df = load_data()

MAX_WAIT = int(df["waiting_days"].max())


def kpi_card(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted mb-1", style={"fontSize": "0.85rem"}),
            html.H3(value, className=f"text-{color} fw-bold mb-0"),
        ]),
        className="shadow-sm h-100 text-center",
    )


def make_age_bar(data):
    counts = data["age_group"].value_counts().reindex(AGE_GROUPS).reset_index()
    counts.columns = ["age_group", "count"]
    fig = px.bar(
        counts,
        x="age_group",
        y="count",
        title="Dogs by Age Group",
        labels={"age_group": "Age Group", "count": "Number of Dogs"},
        color="age_group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=20),
        height=350,
    )
    return fig


def make_size_pie(data):
    counts = data["size"].value_counts().reset_index()
    counts.columns = ["size", "count"]
    counts["size"] = pd.Categorical(counts["size"], categories=SIZE_ORDER, ordered=True)
    counts = counts.sort_values("size")
    fig = px.pie(
        counts,
        names="size",
        values="count",
        title="Dogs by Size",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.35,
    )
    fig.update_layout(
        margin=dict(t=50, b=20),
        height=350,
    )
    return fig


def make_histogram(data, range_vals):
    filtered = data[(data["waiting_days"] >= range_vals[0]) & (data["waiting_days"] <= range_vals[1])]
    fig = px.histogram(
        filtered,
        x="waiting_days",
        nbins=40,
        title="Distribution of Waiting Days Until Adoption Readiness",
        labels={"waiting_days": "Waiting Days", "count": "Number of Dogs"},
        color_discrete_sequence=["#2c7be5"],
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.05,
        margin=dict(t=50, b=20),
        height=380,
    )
    return fig


layout = html.Div([
    html.H2("Overview", className="mb-1"),
    html.P("Summary stats and distributions for the shelter dog dataset.", className="text-muted mb-4"),

    dbc.Row([
        dbc.Col(kpi_card("Total Dogs", f"{len(df):,}"), md=3),
        dbc.Col(kpi_card("% Delayed", f"{df['delayed'].mean()*100:.1f}%", "warning"), md=3),
        dbc.Col(kpi_card("Avg Waiting Days", f"{df['waiting_days'].mean():.1f}", "info"), md=3),
        dbc.Col(kpi_card("% Highly Social", f"{(df['behavior_category']=='Highly Social').mean()*100:.1f}%", "success"), md=3),
    ], className="mb-4 g-3"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Age Group Distribution"),
                dbc.CardBody(dcc.Graph(id="age-bar", figure=make_age_bar(df), config={"displayModeBar": False})),
            ], className="shadow-sm"),
            md=7,
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Size Distribution"),
                dbc.CardBody(dcc.Graph(id="size-pie", figure=make_size_pie(df), config={"displayModeBar": False})),
            ], className="shadow-sm"),
            md=5,
        ),
    ], className="mb-4 g-3"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Waiting Days Distribution"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.Label("Filter range (days):", className="text-muted small mb-1"),
                                dcc.RangeSlider(
                                    id="wait-slider",
                                    min=0,
                                    max=MAX_WAIT,
                                    step=1,
                                    value=[0, min(MAX_WAIT, 180)],
                                    marks={0: "0", 60: "60", 120: "120", 180: "180", MAX_WAIT: str(MAX_WAIT)},
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ]),
                            md=10,
                        ),
                        dbc.Col(
                            dbc.Button("Reset", id="reset-btn", color="secondary", size="sm", className="mt-3"),
                            md=2,
                            className="d-flex align-items-start justify-content-end",
                        ),
                    ], className="mb-2"),
                    dcc.Graph(id="wait-hist", config={"displayModeBar": False}),
                ]),
            ], className="shadow-sm"),
        ),
    ], className="mb-4"),
])


@callback(
    Output("wait-hist", "figure"),
    Input("wait-slider", "value"),
)
def update_histogram(range_vals):
    return make_histogram(df, range_vals)


@callback(
    Output("wait-slider", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_slider(_):
    return [0, min(MAX_WAIT, 180)]