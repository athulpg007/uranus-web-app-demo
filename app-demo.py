import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

data = pd.read_csv("uranus-temp.csv")
data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%Y")
#data.sort_values("Date", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "App Demo"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Uranus Trajectory Exploration", className="header-title"
                ),
                html.P(
                    children="Analyze the trajectories to Uranus",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Targets", className="menu-title"),
                        dcc.Dropdown(
                            id="target-filter",
                            options=[
                                {"label": target, "value": target}
                                for target in np.sort(data.Target.unique())
                            ],
                            value=np.sort(data.Target.unique())[0],
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Path", className="menu-title"),
                        dcc.Dropdown(
                            id="path-filter",
                            options=[
                                {"label": path, "value": path}
                                for path in data.Path.unique()
                            ],
                            value=np.sort(data.Path.unique())[0],
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Launch Date", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="C3-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="tof-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("C3-chart", "figure"), Output("tof-chart", "figure")],
    [
        Input("target-filter", "value"),
        Input("path-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(target, path, start_date, end_date):
    mask = (
        (data.Target == target)
        & (data.Path == path)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    C3_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["LC3"],
                "type": "scatter",
                "mode": "markers"
            },
        ],
        "layout": {
            "title": {
                "text": "Launch C3",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": False},
            "yaxis": {"fixedrange": False},
            "colorway": ["#17B897"],
        },
    }

    AVINF_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Avinf"],
                "type": "scatter",
                "mode": "markers"
            },
        ],
        "layout": {
            "title": {"text": "Arrival Vinf", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": False},
            "yaxis": {"fixedrange": False},
            "colorway": ["#E12D39"],
        },
    }
    return C3_chart_figure, AVINF_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)