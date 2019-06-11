# pylint: disable=C0103,E0401
"""
User interface for Dash app.

"""

import dash_core_components as dcc
import dash_html_components as html
from luts import zones, ecoregions, scenarios, models, treatment_options

# Zones and ecoregions together for now
zones = {**zones, **ecoregions}

# Add additional keys for items exposed via gui
zones["statewide_EcoregionsLevel2"] = "statewide_EcoregionsLevel2"
zones["statewide_FireManagementZones"] = "statewide_FireManagementZones"
models["5modelavg"] = "5modelavg"

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

decadal_radio = dcc.RadioItems(
    labelClassName="radio",
    id="decadal_radio",
    className="control",
    options=[
        {"label": " Annual ", "value": "annual"},
        {"label": " Decadal ", "value": "decadal"},
    ],
    value="annual",
)
decadal_radio_field = html.Div(
    className="field",
    children=[html.Label("Annual or decadal data?", className="label"), decadal_radio],
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
    value="FairbanksArea",
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

veg_graph_layout = html.Div(
    className="container", children=[dcc.Graph(id="veg_counts")]
)

layout = html.Div(
    className="container",
    children=[
        navbar,
        html.H3("Total area burned", className="title is-3"),
        decadal_radio_field,
        historical_field,
        scenarios_checklist_field,
        models_checklist_field,
        treatment_options_checklist_field,
        zone_dropdown_field,
        graph_layout,
        veg_graph_layout,
        footer,
    ],
)
