# pylint: disable=C0103,E0401
"""
Template for SNAP Dash apps.
"""

import pickle
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
from luts import zones, scenarios, models, treatment_options

# Load data
with open("total_area_burned.pickle", "rb") as handle:
    total_area_burned = pickle.load(handle)

# Add Statewide to zones
zones["statewide"] = "Statewide"

# PLACEHOLDER for data exploration
historical_df = total_area_burned["historical"]
df = total_area_burned

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

historical_checkbox = dcc.Checklist(
    id="historical_checkbox",
    options=[{"label": "Show historical", "value": "show_historical"}],
    values=[],
)

historical_field = html.Div(
    className="field",
    children=[
        html.Label("Show historical model data?", className="label"),
        html.Div(className="control", children=[historical_checkbox]),
    ],
)

zone_dropdown = dcc.Dropdown(
    id="zone",
    options=[{"label": zones[key], "value": key} for key in zones],
    value="statewide",
)

zone_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Area", className="label"),
        html.Div(className="control", children=[zone_dropdown]),
    ],
)

scenarios_checklist = dcc.Checklist(
    id="scenarios_checklist",
    options=[{"label": scenarios[key], "value": key} for key in scenarios],
    values=["rcp60"],
)

scenarios_checklist_field = html.Div(
    className="field",
    children=[
        html.Label("Scenarios", className="label"),
        html.Div(className="control", children=[scenarios_checklist]),
    ],
)

models_checklist = dcc.Checklist(
    id="models_checklist",
    options=[{"label": models[key], "value": key} for key in models],
    values=["CCSM4"],
)

models_checklist_field = html.Div(
    className="field",
    children=[
        html.Label("Models", className="label"),
        html.Div(className="control", children=[models_checklist]),
    ],
)

treatment_options_checklist = dcc.Checklist(
    id="treatment_options_checklist",
    options=[
        {"label": treatment_options[key], "value": key} for key in treatment_options
    ],
    values=["gcm_tx0"],
)

treatment_options_checklist_field = html.Div(
    className="field",
    children=[
        html.Label("Treatment options", className="label"),
        html.Div(className="control", children=[treatment_options_checklist]),
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

app.layout = html.Div(
    className="container",
    children=[
        navbar,
        html.H3("Total area burned", className="title is-3"),
        historical_field,
        scenarios_checklist_field,
        models_checklist_field,
        treatment_options_checklist_field,
        zone_dropdown_field,
        graph_layout,
        footer,
    ],
)


@app.callback(
    Output("total_area_burned", "figure"),
    inputs=[
        Input("zone", "value"),
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "values"),
        Input("models_checklist", "values"),
        Input("treatment_options_checklist", "values"),
    ],
)
def generate_total_area_burned(
    zone, show_historical, scenarios, models, treatment_options
):
    show_historical = "show_historical" in show_historical
    data_traces = []

    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                data_traces.append(
                    {
                        "x": df[treatment][scenario][model].index.tolist(),
                        "y": df[treatment][scenario][model][zone],
                        "type": "bar",
                        "name": treatment + scenario + model,
                    }
                )

    if show_historical:
        data_traces.append(
            {
                "x": historical_df.index.tolist(),
                "y": historical_df[zone],
                "type": "bar",
                "name": "historical",
            }
        )

    layout = go.Layout(title="Total area burned", showlegend=True)
    return {"data": data_traces, "layout": layout}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
