# pylint: disable=C0103,E0401
"""
User interface for Dash app.

"""

import dash_core_components as dcc
import dash_html_components as html
import luts

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

region_dropdown = dcc.Dropdown(
    id="region",
    options=[{"label": luts.regions[key], "value": key} for key in luts.regions],
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

about = dcc.Markdown(
    """

How might wildfires in Alaska change over time?  How do different fire management decisions impact costs?  This tool has interactive graphs showing projected future fire behavior, cost, and vegetation indices.

The data used in this tool comes from [ALFRESCO](https://www.snap.uaf.edu/methods/ecosystem-modeling), a software model that simulates the responses of subarctic and boreal vegetation to climatic changes.  We use the model to produce future projections of fire size and vegetation types under varying climate scenarios and fire treatment options.

The story that the projected data are telling is that inter-annual variabiliy of fire size is decreasing&mdash;configerous vegetation is being relegated to optimized, evenly-spaced patches over time.

Costs are estimated by randomly assigning prior years&rsquo; known costs for different the different fire management options (FMOs) to each future year.  For example, if we know that fire costs for Limited option areas were $100/acre, $200/acre, and $1000/acre in the past, we can randomly assign future years to one of these values to estimate possible future costs.  Fire management option polygons from 2017 are used in this data.

""",
    className="about is-size-5 content",
)

graph_layout = html.Div(className="graph", children=[dcc.Graph(id="total_area_burned")])
about_area = dcc.Markdown(
    """

The chart below shows total area burned for the selected region, including the historical results of the model run (1950&ndash;2100).

""",
    className="about is-size-5 content",
)

ia_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="ia")])
about_ia = dcc.Markdown(
    """

The line in the chart below shows inter-annual variability, which can be seen to be decreasing over time.

""",
    className="about is-size-5 content",
)

veg_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="veg_counts")])
about_veg = dcc.Markdown(
    """

A higher coniferous/deciduous ratio indicates more fuel for wildfires.

""",
    className="about is-size-5 content",
)

costs_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="costs")])
about_future_costs = dcc.Markdown(
    """

This chart applies to the full spatial domain of ALFRESCO, and is not subset by the region selected in the drop-down menu.  Scroll down for more information on how costs are estimated.

""",
    className="about is-size-5 content",
)

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
                            children=[region_dropdown_field],
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
                html.Div(className="wrapper", children=[graph_layout]),
                html.H4("Inter-annual variability", className="title is-4 first"),
                about_ia,
                html.Div(className="wrapper", children=[ia_graph_layout]),
                html.H4("Vegetation type ratio", className="title is-4"),
                about_veg,
                html.Div(className="wrapper", children=[veg_graph_layout]),
                html.H4("Future costs, full model domain", className="title is-4"),
                about_future_costs,
                fmo_radio_field,
                html.Div(className="wrapper", children=[costs_graph_layout]),
            ],
        ),
        html.H2("About these charts", className="title is-3"),
        about,
        footer,
    ],
)
