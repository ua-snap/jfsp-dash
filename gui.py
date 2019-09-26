# pylint: disable=C0103,E0401
"""
User interface for Dash app.

"""
from copy import deepcopy
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
    value=["gcm_tx0"],
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

intro_about = dcc.Markdown(
    """
    **This tool is designed to give insight to questions such as:** How might wildfires in Alaska change over time? Will birch and aspen replace spruce as the dominant forest type? How do different fire management decisions impact costs?
    """,
    className="about is-size-4 content",
)

about = dcc.Markdown(
    """

### The modeling behind this tool

Here we summarize  outputs from ALFRESCO (ALaska FRame-based EcoSystem COde), a spatially explicit landscape-scale wildfire model. We use ALFRESCO to simulate wildfire and vegetation dynamics in response to transient changes in climate, across a wide range of future conditions.

#### What this tool does

 * Addresses the natural variability of fire by visualizing broad trends and patterns
 * Displays future projections using the average of 5 top performing GCMs, plus 10-year summaries
 * Provides more exploration opportunities by including 3 different climate scenarios, or RCPs, as well as “treatments”.
 * Provides the ability to subset the analysis by Fire Management Zones, Ecoregions, or look at statewide results.

#### Treatment options TX0, TX1, TX2

ALFRESCO model runs include 3 experimental “treatments” that simulate alteration of the fire management options: Critical, Full, Modified, and Limited.

 * TX0&mdash;No Change: No change in current management approaches. Current fire management options are used into the future.
 * TX1&mdash;More Full Suppression: Current Full suppression areas were extended out by 10km and were used into the future. This represents a large increase in suppression efforts as more fires would fall into the Full area requiring more suppression actions.
 * TX2&mdash;No Full Suppression: Full and Modified suppression areas were re-assigned as Limited, Critical areas remained Critical, and these were used into the future. This represents a large decrease in suppression efforts, as many fires would fall into the Limited area, but many may burn into the Critical area.

#### General Circulation Models (GCMs) and how they fit into this work

GCMs are used to depict how temperature and precipitation respond to changing levels of various gases in the atmosphere. GCMs use future compositions of gases in the atmosphere to make projections of future climate. For this work, GCMs provide projections of future precipitation that drive wildfire activity in the model.

More info: Intergovernmental Panel on Climate Change GCM guide

#### Representative Concentration Pathways (RCPs) and how they fit into this work

RCPs are used to characterize the consequences of different assumptions about human population growth and economic development. In particular, economic development associated with energy use—energy amounts and sources—is an important driver of future climate. We consider 3 RCPs here (4.5, 6.0, and 8.5).

 * RCP 4.5 represents an aggressive reduction in the emission of greenhouse gases like CO2 and methane.
 * RCP 8.5 represents increases in the population and a continuation of the use of energy sources that emit large quantities of greenhouse gases.
 * RCP 6.0 lies somewhere in between.

More info: Intergovernmental Panel on Climate Change RCP Definition

#### What are Fire Management Zones?

These regions are the current Fire Management Zones for Alaska. For more information, please see the zone coverage maps created by the US Bureau of Land Management / Alaska Fire Service.

picture placeholder


#### What are Ecoregions?

Ecoregions are areas where ecosystems (and the type, quality, and quantity of environmental resources) are generally similar (Omernik 1987).

picture placeholder2

""",
    className="about is-size-5 content",
)

area_config = deepcopy(luts.fig_configs)
area_config["toImageButtonOptions"]["filename"] = "Area_Burned_Inter-annual_Variability"
graph_layout = html.Div(
    className="graph", children=[dcc.Graph(id="total_area_burned", config=area_config)]
)
about_area = dcc.Markdown(
    """

The chart below shows total area burned for the selected region, including the historical results of the model run (1950&ndash;2100).

""",
    className="about is-size-5 content",
)

veg_config = deepcopy(luts.fig_configs)
veg_config["toImageButtonOptions"]["filename"] = "Costs_Veg_Ratios"
veg_graph_layout = html.Div(
    className="graph", children=[dcc.Graph(id="veg_counts", config=veg_config)]
)
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
        intro_about,
        html.Div(
            className="graphs",
            children=[
                html.H4(
                    "Total area burned & inter-annual variability",
                    className="title is-4 first",
                ),
                about_area,
                html.Div(className="wrapper", children=[graph_layout]),
                html.H4(
                    "Future costs, full model domain &amp; vegetation type ratio",
                    className="title is-4",
                ),
                about_future_costs,
                about_veg,
                fmo_radio_field,
                html.Div(className="wrapper", children=[veg_graph_layout]),
            ],
        )
    ],
)
