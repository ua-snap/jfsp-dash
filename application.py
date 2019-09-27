# pylint: disable=C0103,E0401,R0913,C0330,too-many-locals
"""
JFSP app.

See gui.py for the Dash components and GUI.
See luts.py for the lookup tables which drive both the data ingest and GUI.
See preprocess.py for the data structure that this code assumes!

"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import dash
import pandas as pd
import luts
from gui import layout

total_area_burned = pd.read_pickle("total_area_burned.pickle")
veg_counts = pd.read_pickle("veg_counts.pickle")
costs = pd.read_pickle("costs.pickle")

# Window for doing rolling average/std
rolling_window = 10

app = dash.Dash(__name__)
# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = "JFSP"
app.layout = layout


@app.callback(
    Output("total_area_burned", "figure"),
    inputs=[
        Input("region", "value"),
        Input("scenarios_checklist", "value"),
        Input("treatment_options_checklist", "value"),
    ],
)
def generate_total_area_burned(region, scenario, treatment_options):
    """

    Regenerate plot data for area burned,
    combined with inter-annual variability.

    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add historical trace
    fig.add_trace(
        go.Scatter(
            {
                "x": list(range(2015, 2095)),
                "y": [112200] * 80, # historical median
                "mode": "lines",
                "name": "Historical average (1950-2013)",
                "line": {
                    "width": 3,
                    "color": "rgba(0, 0, 0, 0.2)"
                },
                "showlegend": False,
                "hoverinfo": "skip"
            }
        ),
        secondary_y=False,
    )

    # For each trace, draw a box plot but don't repeat the
    # plots for historical stuff.  Use a counter to decide
    # if to trim the data set.
    counter = 0  # index for colors
    for treatment in treatment_options:
        dt = pd.DataFrame()
        t = total_area_burned[
            (total_area_burned.region == region)
            & (total_area_burned.scenario == scenario)
            & (total_area_burned.model == luts.MODEL_AVG)
            & (total_area_burned.treatment == treatment)
        ]

        # copy to use later
        p = t.copy()

        t["year"] = pd.to_numeric(t.index)
        t = t[(t.year >= 2020) & (t.year <= 2100)]

        # Trick to group the data into decadal buckets,
        # to match what Dash wants for box plots.
        t = t.groupby(t.index // 10 * 10)
        for key, values in t:  # pylint: disable=unused-variable
            a = t.get_group(key)
            a = a.assign(decade=key)
            dt = dt.append(a)

        fig.add_trace(
            go.Box(
                name="Area burned, " + luts.treatment_options[treatment],
                x=dt.decade,
                y=dt.area.apply(luts.to_hectares),
                marker_color=luts.iav_colors[counter],
            ),
            secondary_y=False,
        )

        # Add inter-annual variability
        rolling_std = p.area.rolling(rolling_window, center=True).std()
        rolling_std = rolling_std.loc[2020:2095]

        fig.add_trace(
            go.Scatter(
                {
                    "x": rolling_std.index.tolist(),
                    "y": rolling_std.apply(luts.to_hectares).tolist(),
                    "mode": "lines",
                    "name": ", ".join(
                        [
                            "10-year rolling standard deviation, "
                            + luts.treatment_options[treatment]
                        ]
                    ),
                    "marker_color": luts.iav_colors[counter],
                }
            ),
            secondary_y=True,
        )

        counter += 1

    fig.update_layout(
        title="Total area burned, "
        + luts.regions[region]
        + ", "
        + luts.scenarios[scenario]
        + ", "
        + luts.models[luts.MODEL_AVG],
        showlegend=True,
        legend_orientation="h",
        boxmode="group",
        font={"family": "Arial"},
        legend={"font": {"family": "Arial", "size": 12}, "y": -0.15},
        xaxis={"title": "Year"},
        # <br> adds padding from y-axis
        height=550,
        paper_bgcolor="#fff",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 75, "r": 75, "b": 75, "t": 50, "pad": 10},
        annotations=[
            go.layout.Annotation(
                x=.115,
                y=112200,
                ax=-20,
                ay=40,
                showarrow=True,
                arrowhead=7,
                xref="paper",
                yref="y",
                text="Historical median, 112.2k ha",
            )
        ]
    )

    fig.update_yaxes(
        title_text="<br>Annual inter-annual variability, hectares", secondary_y=True
    )
    fig.update_yaxes(title_text="Decadal area burned, hectares<br>&nbsp;", secondary_y=False)

    return fig


@app.callback(
    Output("veg_counts", "figure"),
    inputs=[
        Input("region", "value"),
        Input("scenarios_checklist", "value"),
        Input("treatment_options_checklist", "value"),
        Input("fmo_radio", "value"),
    ],
)
def generate_veg_counts(region, scenario, treatment_options, option):
    """ Display veg count graph """

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    counter = 0  # for color indices
    for treatment in treatment_options:

        dt = pd.DataFrame()
        hc = costs.loc[
            (costs["treatment"] == treatment)
            & (costs["scenario"] == scenario)
            & (costs["model"] == luts.MODEL_AVG)
            & (costs["option"] == option)
        ]
        hc["year"] = pd.to_numeric(hc.index)
        hc = hc[(hc.year >= 2020) & (hc.year <= 2100)]
        hc = hc.groupby(hc.index // 10 * 10)

        for key, values in hc:  # pylint: disable=unused-variable
            d = hc.get_group(key)
            d = d.assign(decade=key)
            dt = dt.append(d)

        fig.add_trace(
            go.Box(
                name="Total costs, " + luts.treatment_options[treatment],
                x=dt.decade,
                y=dt.cost,
                marker_color=luts.iav_colors[counter],
            ),
            secondary_y=False,
        )

        vc = veg_counts.loc[
            (veg_counts["treatment"] == treatment)
            & (veg_counts["scenario"] == scenario)
            & (veg_counts["model"] == luts.MODEL_AVG)
            & (veg_counts["region"] == luts.STATEWIDE)
        ]
        vc["year"] = pd.to_numeric(vc.index)
        vc = vc[(vc.year >= 2020) & (vc.year <= 2100)]
        fig.add_trace(
            go.Scatter(
                {
                    "x": vc.index.tolist(),
                    "y": vc["coniferous"] / vc["deciduous"],
                    "mode": "lines",
                    "name": ", ".join(
                        [
                            "Vegetation ratio",
                            luts.treatment_options[treatment],
                            luts.models[luts.MODEL_AVG],
                        ]
                    ),
                    "marker_color": luts.iav_colors[counter],
                }
            ),
            secondary_y=True,
        )

        counter += 1

    if option == "total":
        title_option = "Total Costs"
    else:
        title_option = luts.fmo_options[option] + " option costs"

    fig.update_layout(
        title=title_option
        + ", vegetation ratios, "
        + luts.regions[region]
        + ", "
        + luts.scenarios[scenario]
        + ", "
        + luts.models[luts.MODEL_AVG],
        font={"family": "Arial"},
        showlegend=True,
        legend={"font": {"family": "Arial", "size": 12}, "y": -0.15},
        xaxis={"title": "Year"},
        paper_bgcolor="#fff",
        plot_bgcolor="rgba(0,0,0,0)",
        height=550,
        legend_orientation="h",
        boxmode="group",
        yaxis={"title": "Coniferous/Deciduous"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )

    fig.update_yaxes(title_text="<br>Coniferous/deciduous ratio", secondary_y=True)
    fig.update_yaxes(title_text="Cost, $<br>&nbsp;", secondary_y=False)

    return fig


if __name__ == "__main__":
    application.run(debug=False, port=8080)
