# Import necessary libraries
from flask import Flask, render_template
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

# Read data from CSV file
data_air = pd.read_csv("air4.csv")
data_air["DATETIMEDATA"] = pd.to_datetime(data_air["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
data_air.sort_values("DATETIMEDATA", inplace=True)

# Read data from CSV file for prediction
data_pred = pd.read_csv("model_predictions.csv")
data_pred["DATETIMEDATA"] = pd.to_datetime(data_pred["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
data_pred.sort_values("DATETIMEDATA", inplace=True)

# Define external stylesheets
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app
app = Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.title = "Air Quality Analytics: Understand Air Quality!"

navbar = html.Div(
    className="navbar",  # Added a class name for styling
    children=[
        html.Nav(
            className="nav",
            children=[
                html.A('Analysis', href='/'),
                html.A('Prediction', href='/page-2'),
            ]
        )
    ]
)
# Define layout of the Dash app
app.layout = html.Div(
    children=[
        navbar,
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
                                for param in data_air.columns[1:]
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
                            min_date_allowed=pd.to_datetime(data_air["DATETIMEDATA"]).min(),
                            max_date_allowed=pd.to_datetime(data_air["DATETIMEDATA"]).max(),
                            start_date=data_air["DATETIMEDATA"].min(),
                            end_date=data_air["DATETIMEDATA"].max(),
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
                    children=dcc.Graph(
                        id="daily-stats", config={"displayModeBar": False},
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

# Define app callbacks

# Callback for updating statistics table
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
        (data_air["DATETIMEDATA"] >= start_date)
        & (data_air["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data_air.loc[mask]
    stats = filtered_data[selected_parameter].describe().reset_index().round(2)
    stats.columns = ["Statistic", "Value"]
    
    # Get the minimum and maximum values and their dates
    min_val = filtered_data[selected_parameter].min()
    min_date = filtered_data.loc[filtered_data[selected_parameter].idxmin()]["DATETIMEDATA"]
    max_val = filtered_data[selected_parameter].max()
    max_date = filtered_data.loc[filtered_data[selected_parameter].idxmax()]["DATETIMEDATA"]
    
    # Format strings for minimum and maximum values with dates
    min_val_str = f"{min_val} ({min_date})"
    max_val_str = f"{max_val} ({max_date})"
    
    # Replace the min and max values in the stats dataframe
    stats.loc[stats["Statistic"] == "min", "Value"] = min_val_str
    stats.loc[stats["Statistic"] == "max", "Value"] = max_val_str
    
    stats_table = dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True, className="custom-table")
    
    title = html.Div(children=f"Statistics - {selected_parameter}", className="menu-title")
    
    return [title, stats_table]

# Callback for updating chart
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
        (data_air["DATETIMEDATA"] >= start_date)
        & (data_air["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data_air.loc[mask]
    
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

# Callback for updating daily statistics chart
@app.callback(
    Output("daily-stats", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_daily_stats(selected_parameter, start_date, end_date):
    mask = (
        (data_air["DATETIMEDATA"] >= start_date)
        & (data_air["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data_air.loc[mask]

    # Group by date and calculate daily maximum, minimum, and mean values
    daily_stats = filtered_data.groupby(filtered_data["DATETIMEDATA"].dt.date)[selected_parameter].agg(['max', 'min', 'mean']).reset_index()

    # Create traces for each statistic
    traces = []
    for stat in ['max', 'min', 'mean']:
        traces.append(go.Scatter(
            x=daily_stats["DATETIMEDATA"],
            y=daily_stats[stat],
            mode='lines',
            name=stat.capitalize()  # Capitalize the statistic name for legend
        ))

    layout = {
        "title": f"Daily Statistics - {selected_parameter}",
        "xaxis": {"title": "Date"},
        "yaxis": {"title": selected_parameter},
        "colorway": ["#FF5733", "#33FF57", "#5733FF"],  # Different color for each statistic
    }

    return {"data": traces, "layout": layout}

# Define Dash layout for predictions
predict_layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈", className="header-emoji"),
                html.H1(
                    children="Model Predictions", className="header-title"
                ),
                html.P(
                    children="Visualize the predictions made by the model",
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
                            id="parameter-filter-predict",
                            options=[
                                {"label": param, "value": param}
                                for param in data_pred.columns[1:]
                            ],
                            value="predicted_value",  # Adjust this according to your data
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
                        id="chart-predict", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


# Define Flask route to serve Dash app
@server.route('/')
def index():
    return app.index()


# Run the server
if __name__ == "__main__":
    server.run(debug=True)
