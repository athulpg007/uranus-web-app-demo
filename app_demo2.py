import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
from scipy.interpolate import interp1d

data = pd.read_csv("data/uranus-temp.csv")
data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%Y")
#data.sort_values("Date", inplace=True)

launcher_list = ['falcon-heavy-expendable',  'falcon-heavy-reusable', 'delta-IVH', 'atlas-v551-w-star-48',
				 'vulcan-centaur-w-6-solids', 'vulcan-centaur-w-6-solids-w-star-48',
				 'sls-block-1', 'sls-block-1B', 'sls-block-1B-with-kick']

vinf_list = np.linspace(10, 24, 8)

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
                        html.Div(children="Launch Vehicle", className="menu-title"),
                        dcc.Dropdown(
                            id="launch-vehicle-filter",
                            options=[
                                {"label": launcher, "value": launcher}
                                for launcher in launcher_list
                            ],
                            value=launcher_list[0],
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
                            value=np.sort(data.Path.unique())[1],
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
                        id="launch-mass-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),

				html.Div(
                    children=dcc.Graph(
                        id="combined-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
				html.Div(
					children=dcc.Graph(
						id="avinf-chart",
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
    [Output("launch-mass-chart", "figure"), Output("avinf-chart", "figure"), Output("combined-chart", "figure")],
    [
        Input("launch-vehicle-filter", "value"),
        Input("path-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(launcher, path, start_date, end_date):
	XY = np.loadtxt(f"data/{launcher}.csv", delimiter=',')
	f = interp1d(XY[:, 0], XY[:, 1], kind='linear', fill_value=0, bounds_error=False)


	mask = ((data.Path == path)
		& f(data["LC3"]) > 0
		& (data.Date >= start_date)
		& (data.Date <= end_date)
	)

	filtered_data = data.loc[mask, :]

	launch_mass_chart_figure = {
		"data": [
			{
				"x": filtered_data["Date"],
				"y": f(filtered_data["LC3"]),
				"type": "scatter",
				"mode": "markers",
			},
		],
		"layout": {
			"title": {
				"text": "Launch Capability vs. Launch Year",
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
				"x": filtered_data["TOF"],
				"y": filtered_data["Avinf"],
				"type": "scatter",
				"mode": "markers",
				"marker": {'color': f(filtered_data["LC3"]), 'colorscale': 'Jet',
						   'colorbar': {'thickness': 10, 'title': 'Launch mass'}},
			},
		],
		"layout": {
			"title": {"text": "Arrival Vinf vs TOF", "x": 0.05, "xanchor": "left"},
			"xaxis": {"fixedrange": False},
			"yaxis": {"fixedrange": False},
			"colorway": ["#E12D39"],
		},
	}

	combined_chart_figure = {
		"data": [
			{
				"x": filtered_data["TOF"],
				"y": f(filtered_data["LC3"]),
				"type": "scatter",
				"mode": "markers",
				"marker": {'color': filtered_data["Avinf"], 'colorscale': 'Jet', 'colorbar': {'thickness': 10, 'title':'Arrival Vinf'}},


			},
		],
		"layout": {
			"title": {"text": "Launch Capability vs. TOF", "x": 0.05, "xanchor": "left"},
			"xaxis": {"fixedrange": False},
			"yaxis": {"fixedrange": False},
			#"colorway": ["#E12D39"],
		},
	}
	return launch_mass_chart_figure, AVINF_chart_figure, combined_chart_figure


if __name__ == "__main__":
	app.run_server(debug=True)