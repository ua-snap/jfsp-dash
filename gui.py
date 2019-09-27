# pylint: disable=C0103,E0401
"""
User interface for Dash app.

"""
import os
from string import Template
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import luts

models = luts.models
models["5modelavg"] = "5-Model Average"
fmos = luts.fmo_options
fmos["total"] = "Total Costs"

path_prefix = os.environ["REQUESTS_PATHNAME_PREFIX"]

header = html.Div(
    children=[
        html.Div(
            className="header",
            children=[
                html.H1(
                    "Impacts of Climate and Management Options on Wildland Fire Fighting in Alaska: Implications for Operational Costs and Complexity under Future Scenarios",
                    className="title is-3"
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
    className="footer has-text-centered",
    children=[
        html.Div(
            children=[
                html.A(
                    href="http://www.neptuneinc.org",
                    target="_blank",
                    className="level-item neptune",
                    children=[html.Img(src=path_prefix + "assets/neptune.jpg")],
                ),
                html.A(
                    href="https://snap.uaf.edu",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=path_prefix + "assets/SNAP_color_all.svg")],
                ),
                html.A(
                    href="https://uaf.edu/uaf/",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=path_prefix + "assets/UAF.svg")],
                ),
            ]
        ),
        dcc.Markdown(
            """
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className="content is-size-6",
        ),
    ],
)

intro_text = ddsih.DangerouslySetInnerHTML('''
<div class="content intro about">

    <p class="is-size-5">This tool is designed to give insight to questions such as: How might wildfires in Alaska change over time? Will birch and aspen replace spruce as the dominant forest type? How do different fire management decisions impact costs?</p>

    <div class="is-size-6">
        <p>This website was developed as part of project (#16-1-01-18) funded by the Joint Fire Science Program.</p>

        <ul>
            <li>Courtney Schultz, Colorado State University, Principal Investigator</li>
            <li>Dr. Paul Duffy, Neptune, Inc., Co-Principal Investigator</li>
            <li>Dr. Nancy Fresco, University of Alaska, Fairbanks, Co-Principal Investigator</li>
            <li>Randi Jandt, Alaska Fire Science Consortium, Collaborator</li>
        </ul>
    </div>
</div>
''')

about_text = Template('''
<div class="content is-size-5 about">
    <h2 class="title is-4">The modeling behind this tool</h2>
    <p>Here we summarize  outputs from ALFRESCO (ALaska FRame-based EcoSystem COde), a spatially explicit landscape-scale wildfire model. We use ALFRESCO to simulate wildfire and vegetation dynamics in response to transient changes in climate, across a wide range of future conditions.</p>

    <h2 class="title is-4">What this tool does</h2>
    <ul>
        <li>Addresses the natural variability of fire by visualizing broad trends and patterns</li>
        <li>Displays future projections using the average of 5 top performing GCMs, plus 10-year summaries</li>
        <li>Provides more exploration opportunities by including 3 different climate scenarios, or RCPs, as well as &ldquo;treatments&rdquo;.</li>
        <li>Provides the ability to subset the analysis by Fire Management Zones, Ecoregions, or look at statewide results.</li>
    </ul>

    <h2 class="title is-4">Treatment options TX0, TX1, TX2</h2>
    <p>ALFRESCO model runs include 3 experimental &ldquo;treatments&rdquo; that simulate alteration of the fire management options: Critical, Full, Modified, and Limited.</p>

    <ul>
        <li><strong>TX0&mdash;Baseline:</strong> Current fire management options are continued into the future, with the exception being all Modified areas are switched to Limited. Otherwise, this scenario assumes minimal changes to current management practices.</li>
        <li><strong>TX1&mdash;More Full Suppression:</strong> Starting with the TX0 treatment, Full suppression areas were then extended by a 10km buffer and were applied to future simulations. This represents an overall increase in suppression efforts in the affected areas.</li>
        <li><strong>TX2&mdash;No Full Suppression:</strong> Starting with the TX0 treatment, Full and Modified suppression areas were re-assigned to Limited status for the purpose of future simulations. Critical areas remained unchanged. This represents an overall decrease in suppression efforts.</li>
    </ul>

    <h2 class="title is-4">General Circulation Models (GCMs) and how they fit into this work</h2>
    <p>GCMs are used to depict how temperature and precipitation respond to changing levels of various gases in the atmosphere. GCMs use future compositions of gases in the atmosphere to make projections of future climate. For this work, GCMs provide projections of future precipitation that drive wildfire activity in the model.</p>
    <p>More info: <a href="http://www.ipcc-data.org/guidelines/pages/gcm_guide.html">Intergovernmental Panel on Climate Change GCM guide</a></p>

    <h2 class="title is-4">Representative Concentration Pathways (RCPs) and how they fit into this work</h2>
    <p>RCPs are used to characterize the consequences of different assumptions about human population growth and economic development. In particular, economic development associated with energy use—energy amounts and sources—is an important driver of future climate. We consider 3 RCPs here (4.5, 6.0, and 8.5).</p>
    <ul>
        <li>RCP 4.5 represents an aggressive reduction in the emission of greenhouse gases like CO2 and methane.</li>
        <li>RCP 8.5 represents increases in the population and a continuation of the use of energy sources that emit large quantities of greenhouse gases.</li>
        <li>RCP 6.0 lies somewhere in between.</li>
    </ul>

    <p>More info: <a href="https://www.ipcc-data.org/guidelines/pages/glossary/glossary_r.html">Intergovernmental Panel on Climate Change RCP Definition</a></p>

    <h2 class="title is-4">What are Fire Management Zones?</h2>
<p>These regions are the current Fire Management Zones for Alaska. For more information, please see <a href="https://afs.ak.blm.gov/fire-management/zones-alaska-zone-coverage-maps.php">the zone coverage</a> maps created by the US Bureau of Land Management / Alaska Fire Service.</p>

<img src="assets/zones.png" alt="Current fire management zones for Alaska"/>

<h2 class="title is-4">What are Ecoregions?</h2>
<p>Ecoregions are areas where ecosystems (and the type, quality, and quantity of environmental resources) are generally similar (Omernik 1987).</p>

<img src="assets/ecoregions.jpg" alt="Ecoregions of Alaska"/>

''')

graph_layout = html.Div(className="graph", children=[dcc.Graph(id="total_area_burned")])
about_area = dcc.Markdown('''

The chart below shows total area burned for the selected region, including the historical results of the model run (1950&ndash;2100).

''', className="about is-size-5 content")

ia_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="ia")])
about_ia = dcc.Markdown('''

The line in the chart below shows inter-annual variability, which can be seen to be decreasing over time.

''', className="about is-size-5 content")

veg_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="veg_counts")])
about_veg = dcc.Markdown('''

A higher coniferous/deciduous ratio indicates more fuel for wildfires.

''', className="about is-size-5 content")

costs_graph_layout = html.Div(className="graph", children=[dcc.Graph(id="costs")])
about_future_costs = dcc.Markdown('''

This chart applies to the full spatial domain of ALFRESCO, and is not subset by the region selected in the drop-down menu.  Scroll down for more information on how costs are estimated.

''', className="about is-size-5 content")

layout = html.Div(
    className="container",
    children=[
        header,
        intro_text,
        html.Div(
            className="sticky controls",
            children=[
                html.Div(
                    className="columns",
                    children=[
                        html.Div(
                            className="column is-one-third",
                            children=[
                                region_dropdown_field,
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
        ddsih.DangerouslySetInnerHTML(about_text.substitute(prefix=path_prefix)),
        footer,
    ],
)
