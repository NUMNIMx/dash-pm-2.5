# Air Quality Analytics Dashboard

## Description

This project implements a web-based dashboard for analyzing air quality data and visualizing model predictions. It utilizes Flask for the backend server and Dash for creating interactive data visualization components.

## Features
- Analyze historical air quality data.
- Visualize model predictions for air quality parameters.
- Interactive charts and statistics display.
- Dynamic filtering based on date range and parameter selection.

## Installation

Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
1 Run the Flask server:
```
python app.py
```
2 Open a web browser and navigate to http://localhost:8050/ to access the dashboard.

## Data Sources

Historical Air Quality Data: This data is sourced from CSV files containing historical air quality measurements.
Model Predictions: Predictions for air quality parameters are generated by a machine learning model and stored in CSV format.

## Technologies Used

Flask: Backend server framework.
Dash: Web framework for building interactive web applications.
Pandas: Data manipulation and analysis library.
Plotly: Visualization library for creating interactive plots.
Dash Bootstrap Components: Additional UI components for Dash applications.
