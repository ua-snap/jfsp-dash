# pylint: disable=C0103,E0401
"""
JFSP app.

See gui.py for the Dash components and GUI.
See luts.py for the lookup tables which drive both the data ingest and GUI.
See preprocess.py for the data structure that this code assumes!

"""

import pickle
from pprint import pprint
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
from luts import zones, scenarios, models, treatment_options
from gui import layout

# Load data
with open("total_area_burned.pickle", "rb") as handle:
    total_area_burned = pickle.load(handle)

# TEMP todo remove this elsewhere downstream
df = total_area_burned

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
    ],
)
def generate_total_area_burned(
    zone, show_historical, scenarios, models, treatment_options, decadal_radio
):
    show_historical = "show_historical" in show_historical
    data_traces = []

    interval = "annual" if decadal_radio == "annual" else "decadal"

    # Future!
    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                data_traces.extend(
                    [
                        {
                            "x": df["future"][treatment][scenario][model][
                                interval
                            ].index.tolist(),
                            "y": df["future"][treatment][scenario][model][interval][
                                zone
                            ],
                            "type": "bar",
                            "name": treatment + scenario + model,
                        }
                    ]
                )

                if interval == "annual":
                    data_traces.extend(
                        [
                            {
                                "x": df["future"][treatment][scenario][model][
                                    "rolling"
                                ].index.tolist(),
                                "y": df["future"][treatment][scenario][model][
                                    "rolling"
                                ][zone],
                                "type": "bar",
                                "name": "30yr rolling " + treatment + scenario + model,
                            }
                        ]
                    )

    # Past!
    if show_historical:
        data_traces.extend(
            [
                {
                    "x": df["historical"][interval].index.tolist(),
                    "y": df["historical"][interval][zone],
                    "type": "bar",
                    "name": "historical",
                }
            ]
        )
        if interval == "annual":
            data_traces.extend(
                [
                    {
                        "x": df["historical"]["rolling"].index.tolist(),
                        "y": df["historical"]["rolling"][zone],
                        "type": "bar",
                        "name": "30yr rolling historical"
                    }
                ]
            )

    graph_layout = go.Layout(
        title="Total area burned",
        showlegend=True,
        xaxis={"title": "Year"},
        yaxis={"title": "Acres"},
    )
    return {"data": data_traces, "layout": graph_layout}


if __name__ == "__main__":
    application.run(debug=False, port=8080)
