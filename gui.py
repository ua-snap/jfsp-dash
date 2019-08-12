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
fmos = luts.fmo_options
fmos["total"] = "Total Costs"

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

fmo_radio = dcc.RadioItems(
    labelClassName="radio",
    id="fmo_radio",
    className="control horizontal",
    options=[{"label": fmos[key], "value": key} for key in fmos],
    value="total",
)
fmo_radio_field = html.Div(
    className="field",
    children=[
        html.Label("Fire management options", className="label hidden"),
        fmo_radio,
    ],
)

decadal_radio = dcc.RadioItems(
    labelClassName="radio",
    id="decadal_radio",
    className="control horizontal",
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
about_area = dcc.Markdown('''

(placeholder inline help text)  Long term trends in fire size vary according to which GCM and treatment option being used.  This graph shows (x, y, z).

''', className="about")

veg_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="veg_counts")])
about_veg = dcc.Markdown('''

(placeholder inline help text)  The ratio between coniferous and deciduous vegetation influences the wildfire regime.  Looking at how long-term trends in vegetation ratios change gives a sense of how fires may behave in the future.

''', className="about")

costs_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="costs")])
about_future_costs = dcc.Markdown('''

(placeholder inline help text) Future fire costs can be projected by combining future burn area with historical data on actual fire costs.  Fire management options (FMOs)&mdash;Critical, Full, Modified and Limited&mdash;define spatial regions where fire management strategies differ.

This chart applies to the full spatial domain of ALFRESCO, and is not subset by the region selected in the drop-down menu.  This chart does not show historical data.

''', className="about")

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
                                historical_field,
                            ],
                        ),
                        html.Div(
                            className="column is-one-third",
                            children=[treatment_options_checklist_field],
                        ),
                        html.Div(
                            className="column is-one-third",
                            children=[scenarios_checklist_field],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            className="graphs",
            children=[
                html.H4("Total area burned", className="title is-4 first"),
                about_area,
                decadal_radio_field,
                graph_layout,
                html.H4("Vegetation type ratio", className="title is-4"),
                about_veg,
                veg_graph_layout,
                html.H4("Future costs, full model domain", className="title is-4"),
                about_future_costs,
                fmo_radio_field,
                costs_graph_layout,
            ],
        ),
        footer,
    ],
)
