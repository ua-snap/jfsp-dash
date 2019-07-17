# pylint: disable=C0103,E0401
"""
User interface for Dash app.

"""

import dash_core_components as dcc
import dash_html_components as html
import luts

# Zones and ecoregions together for now
regions = {**luts.zones, **luts.ecoregions}

# Add additional keys for items exposed via gui
regions["AllFMZs"] = "Full Model Extent"
models = luts.models
models["5modelavg"] = "5-Model Average"

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
    children=[
        html.Label("Annual or decadal data?", className="label hidden"),
        decadal_radio,
    ],
)

historical_checkbox = dcc.Checklist(
    id="historical_checkbox",
    className="checkbox",
    labelClassName="checkbox",
    options=[{"label": "Show historical", "value": "show_historical"}],
    values=[],
)

historical_field = html.Div(
    className="field",
    children=[
        html.Label("Show historical model data?", className="label hidden"),
        html.Div(className="control tight", children=[historical_checkbox]),
    ],
)

region_dropdown = dcc.Dropdown(
    id="region",
    options=[{"label": regions[key], "value": key} for key in regions],
    value="AllFMZs",
)

region_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Area", className="label hidden"),
        html.Div(className="control", children=[region_dropdown]),
    ],
)

scenarios_checklist = dcc.RadioItems(
    id="scenarios_checklist",
    className="radio",
    labelClassName="radio",
    options=[
        {"label": " " + luts.scenarios[key], "value": key} for key in luts.scenarios
    ],
    value="rcp60",
)

scenarios_checklist_field = html.Div(
    className="field",
    children=[
        html.Label("Scenarios", className="label"),
        html.Div(className="control", children=[scenarios_checklist]),
    ],
)

models_checklist = dcc.RadioItems(
    id="models_checklist",
    labelClassName="radio",
    className="radio models_checklist",
    options=[{"label": " " + models[key], "value": key} for key in sorted(models)],
    value="5modelavg",
)

models_checklist_field = html.Div(
    className="field",
    children=[
        html.Label("Models", className="label"),
        html.Div(className="control", children=[models_checklist]),
    ],
)

rolling_window_slider = dcc.Slider(
    className="",
    id="rolling_slider",
    min=1,
    max=40,
    step=1,
    value=30,
    marks={1: "1", 10: "10", 20: "20", 30: "30", 40: "40"},
)

rolling_window_slider_field = html.Div(
    className="field rolling-window",
    children=[
        html.Label("Rolling average window", className="label"),
        html.Div(className="control", children=[rolling_window_slider]),
    ],
)

treatment_options_checklist = dcc.Checklist(
    id="treatment_options_checklist",
    labelClassName="checkbox",
    options=[
        {"label": luts.treatment_options[key], "value": key}
        for key in luts.treatment_options
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

graph_layout = html.Div(className="graph", children=[dcc.Graph(id="total_area_burned")])

veg_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="veg_counts")])

costs_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="costs")])

layout = html.Div(
    className="container",
    children=[
        navbar,
        html.Div(
            className="sticky",
            children=[
                html.Div(
                    className="columns",
                    children=[
                        html.Div(
                            className="column is-one-third",
                            children=[
                                region_dropdown_field,
                                decadal_radio_field,
                                historical_field,
                                rolling_window_slider_field,
                            ],
                        ),
                        html.Div(
                            className="column is-one-third",
                            children=[
                                treatment_options_checklist_field,
                                scenarios_checklist_field,
                            ],
                        ),
                        html.Div(
                            className="column is-one-third",
                            children=[models_checklist_field],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            className="graphs",
            children=[graph_layout, veg_graph_layout, costs_graph_layout],
        ),
        footer,
    ],
)
