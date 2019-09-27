# pylint: disable=C0103,E0401,R0913,C0330,too-many-locals
"""
JFSP app.

See gui.py for the Dash components and GUI.
See luts.py for the lookup tables which drive both the data ingest and GUI.
See preprocess.py for the data structure that this code assumes!

"""

import math
import plotly.graph_objs as go
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
app.config.requests_pathname_prefix = os.environ["REQUESTS_PATHNAME_PREFIX"]

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = "Alaska Wildfire Management - Possible Futures"
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
    """ Regenerate plot data for area burned """
    data_traces = []

    # Subset historical data
    h = total_area_burned[
        (total_area_burned.region == region)
        & (total_area_burned.treatment == luts.historical_categories[1])
    ]

    # For each trace, draw a box plot but don't repeat the
    # plots for historical stuff.  Use a counter to decide
    # if to trim the data set.
    counter = 0
    for treatment in treatment_options:
        dt = pd.DataFrame()
        t = total_area_burned[
            (total_area_burned.region == region)
            & (total_area_burned.scenario == scenario)
            & (total_area_burned.model == luts.MODEL_AVG)
            & (total_area_burned.treatment == treatment)
        ]

        t = t.append(h)
        if counter > 0:
            t["year"] = pd.to_numeric(t.index)
            t = t[(t.year >= 2010) & (t.year <= 2100)]

        # Trick to group the data into decadal buckets,
        # to match what Dash wants for box plots.
        t = t.groupby(t.index // 10 * 10)
        for key, values in t:  # pylint: disable=unused-variable
            a = t.get_group(key)
            a = a.assign(decade=key)
            dt = dt.append(a)

        data_traces.extend(
            [
                go.Box(
                    name="Area burned, " + luts.treatment_options[treatment],
                    x=dt.decade,
                    y=dt.area.apply(luts.to_acres),
                )
            ]
        )
        counter += 1

    graph_layout = go.Layout(
        title="Total area burned, "
        + luts.regions[region]
        + ", "
        + luts.scenarios[scenario]
        + ", "
        + luts.models[luts.MODEL_AVG],
        showlegend=True,
        legend_orientation="h",
        boxmode="group",
        legend={"font": {"family": "Open Sans", "size": 10}, "y": -0.15},
        xaxis={"title": "Year"},
        yaxis={"title": "Acres", "range": [0, 1900000]},
        height=550,
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


@app.callback(
    Output("ia", "figure"),
    inputs=[
        Input("region", "value"),
        Input("scenarios_checklist", "value"),
        Input("treatment_options_checklist", "value"),
    ],
)
def generate_ia(region, scenario, treatment_options):
    """ Regenerate plot data for area burned """
    data_traces = []

    for treatment in treatment_options:
        t = total_area_burned[
            (total_area_burned.region == region)
            & (total_area_burned.scenario == scenario)
            & (total_area_burned.model == luts.MODEL_AVG)
            & (total_area_burned.treatment == treatment)
        ]

        # Always merge the historical data for computing the
        # rolling std so we get meaningful results for the 2010s.
        rolling_std = t.area.rolling(rolling_window, center=True).std()
        rolling_std = rolling_std.loc[2019:2095]

        data_traces.extend(
            [
                {
                    "x": rolling_std.index.tolist(),
                    "y": rolling_std.apply(luts.to_acres),
                    "type": "line",
                    "name": ", ".join(
                        [
                            "10-year rolling standard deviation, "
                            + luts.treatment_options[treatment]
                        ]
                    ),
                },
            ]
        )

    graph_layout = go.Layout(
        title="Inter-annual variability, "
        + luts.regions[region]
        + ", "
        + luts.scenarios[scenario]
        + ", "
        + luts.models[luts.MODEL_AVG],
        showlegend=True,
        legend_orientation="h",
        boxmode="group",
        legend={"font": {"family": "Open Sans", "size": 10}, "y": -0.15},
        xaxis={"title": "Year"},
        yaxis={"title": "Acres"},
        height=550,
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


@app.callback(
    Output("veg_counts", "figure"),
    inputs=[
        Input("region", "value"),
        Input("scenarios_checklist", "value"),
        Input("treatment_options_checklist", "value"),
    ],
)
def generate_veg_counts(region, scenario, treatment_options):
    """ Display veg count graph """
    data_traces = []

    # Future!
    for treatment in treatment_options:
        vc = veg_counts.loc[
            (veg_counts["treatment"] == treatment)
            & (veg_counts["scenario"] == scenario)
            & (veg_counts["model"] == luts.MODEL_AVG)
            & (veg_counts["region"] == region)
        ]
        data_traces.extend(
            [
                {
                    "x": vc.index.tolist(),
                    "y": vc["coniferous"] / vc["deciduous"],
                    "type": "line",
                    "name": ", ".join(
                        [
                            luts.treatment_options[treatment],
                            luts.scenarios[scenario],
                            luts.models[luts.MODEL_AVG],
                        ]
                    ),
                }
            ]
        )

    graph_layout = go.Layout(
        title="Ratio of Coniferous to Deciduous, by area, "
        + luts.regions[region]
        + ", "
        + luts.scenarios[scenario]
        + ", "
        + luts.models[luts.MODEL_AVG],
        showlegend=True,
        legend={"font": {"family": "Open Sans", "size": 10}, "y": -0.15},
        xaxis={"title": "Year"},
        height=550,
        legend_orientation="h",
        yaxis={"title": "Coniferous/Deciduous"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


@app.callback(
    Output("costs", "figure"),
    inputs=[
        Input("scenarios_checklist", "value"),
        Input("treatment_options_checklist", "value"),
        Input("fmo_radio", "value"),
    ],
)
def generate_costs(scenario, treatment_options, option):
    """ Generate costs graph """
    data_traces = []

    for treatment in treatment_options:
        dt = pd.DataFrame()
        hc = costs.loc[
            (costs["treatment"] == treatment)
            & (costs["scenario"] == scenario)
            & (costs["model"] == luts.MODEL_AVG)
            & (costs["option"] == option)
        ]
        hc = hc.groupby(hc.index // 10 * 10)

        for key, values in hc:  # pylint: disable=unused-variable
            d = hc.get_group(key)
            d = d.assign(decade=key)
            dt = dt.append(d)

        data_traces.extend(
            [go.Box(name=luts.treatment_options[treatment], x=dt.decade, y=dt.cost)]
        )

    if option == "total":
        title_option = "Total Costs"
    else:
        title_option = luts.fmo_options[option] + " Option"

    graph_layout = go.Layout(
        title="Future Costs, Full Model Domain, " + title_option,
        showlegend=True,
        height=550,
        legend_orientation="h",
        boxmode="group",
        legend={"font": {"family": "Open Sans", "size": 10}, "y": -0.15},
        xaxis={"title": "Year"},
        yaxis={"title": "Cost ($)"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
