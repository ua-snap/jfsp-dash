# pylint: disable=C0103,E0401
"""
Template for SNAP Dash apps.
"""

import dash
import dash_table
import pickle
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from pprint import pprint
from luts import zones
from dash.dependencies import Input, Output, State

# Load data
with open("total_area_burned.pickle", "rb") as handle:
    total_area_burned = pickle.load(handle)

# Add Statewide to zones
zones["statewide"] = "Statewide"

# PLACEHOLDER for data exploration
df = total_area_burned["gcm_tx0"]["rcp45"]["CCSM4"]

app = dash.Dash(__name__)
# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = "JFSP"

navbar = html.Div(
    className="navbar",
    role="navigation",
    children=[
        html.Div(
            className="navbar-brand",
            children=[
                html.A(
                    className="navbar-item",
                    href="#",
                    children=[html.Img(src="assets/SNAP_acronym_color.svg")],
                )
            ],
        )
    ],
)

dropdown = dcc.Dropdown(
    id="zone",
    options=[{"label": zones[key], "value": key} for key in zones],
    value="statewide",
)

dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Area", className="label"),
        html.Div(className="control", children=[dropdown]),
    ],
)

footer = html.Footer(
    className="footer",
    children=[
        html.Div(
            className="content has-text-centered",
            children=[
                dcc.Markdown(
                    """
This is a page footer, where we'd put legal notes and other items.
                    """
                )
            ],
        )
    ],
)

graph_layout = html.Div(
    className="container", children=[dcc.Graph(id="total_area_burned")]
)

table = dash_table.DataTable(
    id="table",
    columns=[
        {"name": i, "id": i}
        for i in df.columns
    ],
    data=df.to_dict("records"),
)

app.layout = html.Div(
    className="container",
    children=[
        navbar,
        html.H3("Total area burned", className="title is-3"),
        dropdown_field,
        graph_layout,
        table,
        footer,
    ],
)


@app.callback(Output("total_area_burned", "figure"), inputs=[Input("zone", "value")])
def generate_total_area_burned(zone):
    return {"data": [{"x": df.index.tolist(), "y": df[zone], "type": "bar"}]}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
