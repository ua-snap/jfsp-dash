# pylint: disable=C0103,E0401,R0913,C0330,too-many-locals
"""
JFSP app.

See gui.py for the Dash components and GUI.
See luts.py for the lookup tables which drive both the data ingest and GUI.
See preprocess.py for the data structure that this code assumes!

"""

from pprint import pprint
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash
import pandas as pd
import luts
from gui import layout

total_area_burned = pd.read_pickle("total_area_burned.pickle")
veg_counts = pd.read_pickle("veg_counts.pickle")
costs = pd.read_pickle("costs.pickle")

app = dash.Dash(__name__)
# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = "JFSP"
app.layout = layout


@app.callback(
    Output("total_area_burned", "figure"),
    inputs=[
        Input("zone", "value"),
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "values"),
        Input("models_checklist", "values"),
        Input("treatment_options_checklist", "values"),
        Input("decadal_radio", "value"),
        Input("rolling_slider", "value"),
    ],
)
def generate_total_area_burned(
    zone,
    show_historical,
    scenarios,
    models,
    treatment_options,
    decadal_radio,
    rolling_slider,
):
    """ Regenerate plot data for area burned """
    show_historical = "show_historical" in show_historical
    data_traces = []

    interval = "annual" if decadal_radio == "annual" else "decadal"

    # Stack the bar for the 2010s only when it's historical/decadal
    barmode = "group"
    if show_historical and interval == "decadal":
        barmode = "stack"

    # Future!
    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                data_traces.extend(
                    [
                        {
                            "x": total_area_burned["future"][treatment][scenario][model][
                                interval
                            ].index.tolist(),
                            "y": total_area_burned["future"][treatment][scenario][model][interval][
                                zone
                            ],
                            "type": "bar",
                            "barmode": barmode,
                            "name": ", ".join(
                                [
                                    luts.treatment_options[treatment],
                                    luts.scenarios[scenario],
                                    luts.models[model],
                                ]
                            ),
                        }
                    ]
                )

                merged = pd.concat(
                    [
                        total_area_burned["historical"]["annual"][zone],
                        total_area_burned["future"][treatment][scenario][model]["annual"][zone],
                    ]
                )
                rolling = merged.rolling(rolling_slider, center=True).mean()
                rolling_std = merged.rolling(rolling_slider, center=True).std()

                # Trim if not also showing historical values
                if not show_historical:
                    rolling = rolling.loc[2014:2099]
                    rolling_std = rolling_std.loc[2014:2099]

                if interval == "annual":
                    data_traces.extend(
                        [
                            {
                                "x": rolling.index.tolist(),
                                "y": rolling,
                                "type": "line",
                                "name": ", ".join(
                                    [
                                        str(rolling_slider)
                                        + "yr avg "
                                        + luts.treatment_options[treatment],
                                        luts.scenarios[scenario],
                                        luts.models[model],
                                    ]
                                ),
                            },
                            {
                                "x": rolling_std.index.tolist(),
                                "y": rolling_std,
                                "type": "line",
                                "name": ", ".join(
                                    [
                                        str(rolling_slider)
                                        + "yr avg std"
                                        + luts.treatment_options[treatment],
                                        luts.scenarios[scenario],
                                        luts.models[model],
                                    ]
                                ),
                            },
                        ]
                    )

    # Past!
    if show_historical:
        data_traces.extend(
            [
                {
                    "x": total_area_burned["historical"][interval].index.tolist(),
                    "y": total_area_burned["historical"][interval][zone],
                    "type": "bar",
                    "barmode": barmode,
                    "name": "historical",
                }
            ]
        )

    graph_layout = go.Layout(
        title="Total area burned",
        showlegend=True,
        barmode=barmode,
        legend={"font": {"family": "Open Sans", "size": 10}},
        xaxis={"title": "Year"},
        yaxis={"title": "Acres", "type": "log"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


@app.callback(
    Output("veg_counts", "figure"),
    inputs=[
        Input("zone", "value"),
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "values"),
        Input("models_checklist", "values"),
        Input("treatment_options_checklist", "values"),
        Input("decadal_radio", "value"),
    ],
)
def generate_veg_counts(
    region, show_historical, scenarios, models, treatment_options, decadal_radio
):
    show_historical = "show_historical" in show_historical
    data_traces = []

    # Future!
    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                vc = veg_counts.loc[
                    (veg_counts["treatment"] == treatment)
                    & (veg_counts["scenario"] == scenario)
                    & (veg_counts["model"] == model)
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
                                    luts.models[model],
                                ]
                            ),
                        }
                    ]
                )

    # Past!
    if show_historical:
        vc = veg_counts.loc[
            (veg_counts["treatment"] == "cru_tx0") & (veg_counts["region"] == region)
        ]
        data_traces.extend(
            [
                {
                    "x": vc.index.tolist(),
                    "y": vc["coniferous"] / vc["deciduous"],
                    "type": "line",
                    "name": "Historical",
                }
            ]
        )

    graph_layout = go.Layout(
        title="Ratio of Coniferous to Deciduous, by area",
        showlegend=True,
        legend={"font": {"family": "Open Sans", "size": 10}},
        xaxis={"title": "Year"},
        yaxis={"title": "Coniferous/Deciduous"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}

@app.callback(
    Output("costs", "figure"),
    inputs=[
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "values"),
        Input("models_checklist", "values"),
        Input("treatment_options_checklist", "values"),
        Input("decadal_radio", "value"),
    ],
)
def generate_costs(
    show_historical, scenarios, models, treatment_options, decadal_radio
):
    """ Generate costs graph """
    show_historical = "show_historical" in show_historical
    data_traces = []

    if show_historical:
        for option in luts.fmo_options:
            hc = costs.loc[
                (costs["treatment"] == "cru_tx0") & (costs["option"] == option)
            ]
            data_traces.extend(
                [
                    {
                        "x": hc.index.tolist(),
                        "y": hc["cost"],
                        "type": "bar",
                        "name": "Historical " + luts.fmo_options[option],
                    }
                ]
            )

    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                for option in luts.fmo_options:
                    hc = costs.loc[
                        (costs["treatment"] == treatment) &
                        (costs["scenario"] == scenario) &
                        (costs["model"] == model) &
                        (costs["option"] == option)
                    ]
                    pprint(hc)
                    data_traces.extend(
                        [
                            {
                                "x": hc.index.tolist(),
                                "y": hc["cost"],
                                "type": "bar",
                                "name": treatment + scenario + model + luts.fmo_options[option],
                            }
                        ]
                    )

    graph_layout = go.Layout(
        title="Costs by Fire Management Option",
        showlegend=True,
        legend={"font": {"family": "Open Sans", "size": 10}},
        xaxis={"title": "Year"},
        yaxis={"title": "Cost ($)"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
