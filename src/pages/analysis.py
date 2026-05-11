import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from data_utils import load_data, SIZE_ORDER, AGE_GROUPS, BEHAVIOR_ORDER

dash.register_page(__name__, path="/analysis", name="Behavior & Size")

df = load_data()

size_options = [{"label": s.capitalize(), "value": s} for s in SIZE_ORDER]
age_options = [{"label": "All Age Groups", "value": "All"}] + [
    {"label": ag, "value": ag} for ag in AGE_GROUPS
]


def make_bubble(data, selected_sizes):
    if selected_sizes:
        data = data[data["size"].isin(selected_sizes)]
    grouped = data.groupby(["behavior_category", "size"], observed=True).agg(
        waiting_days=("waiting_days", "mean"),
        count=("waiting_days", "count"),
    ).reset_index()
    fig = px.scatter(
        grouped,
        x="behavior_category",
        y="size",
        size="count",
        color="waiting_days",
        hover_name="behavior_category",
        hover_data={"size": True, "waiting_days": ":.1f", "count": True},
        title="Adoption Readiness Timeline: Behavioral Profile vs Dog Size<br>"
              "<sub>Bubble size = number of dogs; Color = average waiting days</sub>",
        color_continuous_scale="RdYlGn_r",
        size_max=50,
        labels={
            "waiting_days": "Avg Waiting Days",
            "behavior_category": "Behavioral Category",
            "size": "Dog Size",
            "count": "Number of Dogs",
        },
        category_orders={
            "behavior_category": BEHAVIOR_ORDER,
            "size": SIZE_ORDER,
        },
        height=480,
    )
    fig.update_layout(
        font=dict(size=12),
        coloraxis_colorbar=dict(title="Avg Days"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=80, b=40),
    )
    return fig


def make_heatmap(data, age_group):
    if age_group != "All":
        data = data[data["age_group"] == age_group]
    pivot = data.pivot_table(
        values="waiting_days",
        index="behavior_category",
        columns="size",
        aggfunc="mean",
        observed=True,
    )
    pivot = pivot.reindex(BEHAVIOR_ORDER)
    for s in SIZE_ORDER:
        if s not in pivot.columns:
            pivot[s] = float("nan")
    pivot = pivot[SIZE_ORDER]
    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn_r",
        title=f"Average Waiting Days — {age_group}",
        labels=dict(x="Dog Size", y="Behavioral Profile", color="Days"),
        text_auto=".1f",
        aspect="auto",
        height=420,
    )
    fig.update_layout(
        font=dict(size=12),
        coloraxis_colorbar=dict(title="Avg Days"),
        paper_bgcolor="white",
        margin=dict(t=60, b=40),
    )
    return fig


layout = html.Div([
    html.H2("Behavior & size", className="mb-1"),
    html.P("Behavior category vs size and average waiting days.", className="text-muted mb-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Label("Filter by Age Group", className="fw-semibold mb-1"),
                    dcc.Dropdown(
                        id="age-dropdown",
                        options=age_options,
                        value="All",
                        clearable=False,
                    ),
                ])
            ], className="shadow-sm"),
            md=4,
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Label("Filter Sizes (Bubble Chart)", className="fw-semibold mb-1"),
                    dcc.Dropdown(
                        id="size-multi-dropdown",
                        options=size_options,
                        value=SIZE_ORDER,
                        multi=True,
                        placeholder="Select sizes…",
                    ),
                ])
            ], className="shadow-sm"),
            md=8,
        ),
    ], className="mb-4 g-3"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Behavioral Profile vs Dog Size (Bubble Chart)"),
                dbc.CardBody(dcc.Graph(id="bubble-chart", config={"displayModeBar": False})),
            ], className="shadow-sm"),
        ),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Avg waiting days (behavior × size)"),
                dbc.CardBody(
                    dcc.Graph(id="heatmap-chart", config={"displayModeBar": False}),
                ),
            ], className="shadow-sm"),
        ),
    ], className="mb-4"),
])


@callback(
    Output("bubble-chart", "figure"),
    Input("age-dropdown", "value"),
    Input("size-multi-dropdown", "value"),
)
def update_bubble(age_group, selected_sizes):
    data = df if age_group == "All" else df[df["age_group"] == age_group]
    return make_bubble(data, selected_sizes)


@callback(
    Output("heatmap-chart", "figure"),
    Input("age-dropdown", "value"),
)
def update_heatmap(age_group):
    return make_heatmap(df, age_group)