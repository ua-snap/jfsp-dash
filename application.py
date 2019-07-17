# pylint: disable=C0103,E0401,R0913,C0330,too-many-locals
"""
JFSP app.

See gui.py for the Dash components and GUI.
See luts.py for the lookup tables which drive both the data ingest and GUI.
See preprocess.py for the data structure that this code assumes!

"""

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
        Input("region", "value"),
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "value"),
        Input("models_checklist", "value"),
        Input("treatment_options_checklist", "values"),
        Input("decadal_radio", "value"),
        Input("rolling_slider", "value"),
    ],
)
def generate_total_area_burned(
    region,
    show_historical,
    scenario,
    model,
    treatment_options,
    decadal_radio,
    rolling_slider,
):
    """ Regenerate plot data for area burned """
    show_historical = "show_historical" in show_historical
    data_traces = []

    interval = "annual" if decadal_radio == "annual" else "decadal"
    barmode = "group"

    # Subset historical data
    h = total_area_burned[
        (total_area_burned.region == region)
        & (total_area_burned.treatment == luts.historical_categories[1])
    ]
    if interval == "decadal":
        h = h.groupby(h.index // 10 * 10).mean()

    # Future!
    for treatment in treatment_options:
        t = total_area_burned[
            (total_area_burned.region == region)
            & (total_area_burned.scenario == scenario)
            & (total_area_burned.model == model)
            & (total_area_burned.treatment == treatment)
        ]

        if interval == "decadal":
            t = t.groupby(t.index // 10 * 10).mean()
            data_traces.extend(
                [
                    {
                        "x": t.index.tolist(),
                        "y": t.area.apply(luts.to_acres),
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

        merged = pd.concat([h.area, t.area])
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
                        "y": rolling.apply(luts.to_acres),
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
                        "y": rolling_std.apply(luts.to_acres),
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

    graph_layout = go.Layout(
        title="Total area burned",
        showlegend=True,
        barmode=barmode,
        legend={"font": {"family": "Open Sans", "size": 10}},
        xaxis={"title": "Year"},
        yaxis={"title": "Acres"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


@app.callback(
    Output("veg_counts", "figure"),
    inputs=[
        Input("region", "value"),
        Input("historical_checkbox", "values"),
        Input("scenarios_checklist", "value"),
        Input("models_checklist", "value"),
        Input("treatment_options_checklist", "values"),
    ],
)
def generate_veg_counts(region, show_historical, scenario, model, treatment_options):
    """ Display veg count graph """
    show_historical = "show_historical" in show_historical
    data_traces = []

    # Future!
    for treatment in treatment_options:
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
        Input("scenarios_checklist", "value"),
        Input("models_checklist", "value"),
        Input("treatment_options_checklist", "values"),
        Input("decadal_radio", "value"),
    ],
)
def generate_costs(
    scenario, model, treatment_options, decadal_radio
):
    """ Generate costs graph """
    data_traces = []

    for treatment in treatment_options:
        for option in luts.fmo_options:
            hc = costs.loc[
                (costs["treatment"] == treatment)
                & (costs["scenario"] == scenario)
                & (costs["model"] == model)
                & (costs["option"] == option)
            ]
            data_traces.extend(
                [
                    {
                        "x": hc.index.tolist(),
                        "y": hc["cost"],
                        "type": "bar",
                        "name": treatment
                        + scenario
                        + model
                        + luts.fmo_options[option],
                    }
                ]
            )

    graph_layout = go.Layout(
        title="Future Costs by Fire Management Option",
        showlegend=True,
        legend={"font": {"family": "Open Sans", "size": 10}},
        xaxis={"title": "Year"},
        yaxis={"title": "Cost ($)"},
        margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
    )
    return {"data": data_traces, "layout": graph_layout}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
