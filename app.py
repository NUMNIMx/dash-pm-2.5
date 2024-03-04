from dash import Dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

import pandas as pd
import plotly.express as px

data = pd.read_csv("air4.csv")
data["DATETIMEDATA"] = pd.to_datetime(data["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
data.sort_values("DATETIMEDATA", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Air Quality Analytics: Understand Air Quality!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🌬️", className="header-emoji"),
                html.H1(
                    children="Air Quality Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the air quality data",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Parameter", className="menu-title"),
                        dcc.Dropdown(
                            id="parameter-filter",
                            options=[
                                {"label": param, "value": param}
                                for param in data.columns[1:]
                            ],
                            value="PM25",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["DATETIMEDATA"].min().date(),
                            max_date_allowed=data["DATETIMEDATA"].max().date(),
                            start_date=data["DATETIMEDATA"].min().date(),
                            end_date=data["DATETIMEDATA"].max().date(),
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Chart Type",
                            className="menu-title"
                        ),
                        dcc.Dropdown(
                            id="chart-type",
                            options=[
                                {"label": "Line Chart", "value": "line"},
                                {"label": "Bar Chart", "value": "bar"},
                                {"label": "Scatter Plot", "value": "scatter"},
                            ],
                            value="line",
                            clearable=False,
                            className="dropdown",
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
                        id="chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title"
                        ),
                        html.Div(
                            id="stats-table",
                            className="stats-table"
                        ),
                    ],
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

# APP CALLBACKS

# for Table
@app.callback(
    Output("stats-table", "children"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_stats_table(selected_parameter, start_date, end_date):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask]
    stats = filtered_data[selected_parameter].describe().reset_index()
    stats.columns = ["Statistic", "Value"]
    stats_table = dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True, className="custom-table")
    
    title = html.Div(children=f"Statistics - {selected_parameter} ({start_date}-{end_date})", className="menu-title")
    
    return [title, stats_table]

# for updating chart
@app.callback(
    Output("chart", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("chart-type", "value"),
    ],
)
def update_chart(selected_parameter, start_date, end_date, chart_type):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask]
    
    if chart_type == "line":
        trace = {
            "x": filtered_data["DATETIMEDATA"],
            "y": filtered_data[selected_parameter],
            "type": "line",
        }
    elif chart_type == "scatter":
        trace = {
            "x": filtered_data["DATETIMEDATA"],
            "y": filtered_data[selected_parameter],
            "mode": "markers",  # Scatter plot with markers
            "type": "scatter",
        }
    elif chart_type == "bar":
        trace = {
            "x": filtered_data["DATETIMEDATA"],
            "y": filtered_data[selected_parameter],
            "type": "bar",
        }
        
    layout = {
        "title": f"Air Quality Over Time - {selected_parameter}",
        "xaxis": {"title": "Datetime"},
        "yaxis": {"title": selected_parameter},
        "colorway": ["#17B897"],  # or any other color
    }
    return {"data": [trace], "layout": layout}


if __name__ == "__main__":
    app.run_server(debug=True)
