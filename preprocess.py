"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

# pylint: disable=invalid-name,import-error,line-too-long

import os
import pickle
import pandas as pd
from pprint import pprint
from luts import zones, scenarios, models, treatment_options

data_dir = "data"

# Some static stuff we glue to make filenames
fmo_prefix = "fmo99s95i"
historical_fmo_prefix = "fmo99s95i_historical_CRU32"
date_postfix = "2014_2099"
historical_date_postfix = "1950_2013"
historical_categories = ["cru_none", "cru_tx0"]
rolling_window = 30  # years for rolling window computations
total_area_burned = {}
zones_with_statewide = zones.copy()
zones_with_statewide.update({"statewide": "statewide"})


def to_acres(km2):
    """ square KM to acres """
    return round(km2 * 247.11)


""" Data structures to build:

total_area_burned, decadal_area_burned
    historical
        annual: DataFrame(cols = zones)
        rolling: DataFrame(cols = zones)
        decadal: DataFrame(cols = zones)
    future
        treatment
            scenario
                model
                    annual: DataFrame(cols = zones)
                    rolling: DataFrame(cols = zones)
                    decadal: DataFrame(cols = zones)

"""

# Compute total area burned (historical)
total_area_burned["historical"] = {"annual": pd.DataFrame(), "rolling": pd.DataFrame(), "decadal": pd.DataFrame()}

for zone in zones:
    input_file = os.path.join(
        data_dir,
        historical_categories[1],
        historical_fmo_prefix,
        "total_area_burned",
        "_".join(
            [
                "alfresco_totalareaburned",
                zone,
                historical_fmo_prefix,
                historical_date_postfix,
            ]
        )
        + ".csv",
    )
    source_data = pd.read_csv(input_file, index_col=0)
    total_area_burned["historical"]["annual"][zone] = to_acres(source_data.mean(axis=1))
    total_area_burned["historical"]["decadal"][zone] = (
        total_area_burned["historical"]["annual"][zone]
        .groupby(total_area_burned["historical"]["annual"][zone].index // 10 * 10)
        .mean()
    )
    total_area_burned["historical"]["rolling"][zone] = (
        total_area_burned["historical"]["annual"][zone].rolling(rolling_window).mean()
    )

total_area_burned["historical"]["annual"]["statewide"] = total_area_burned[
    "historical"
]["annual"].sum(axis=1)
total_area_burned["historical"]["decadal"]["statewide"] = (
    total_area_burned["historical"]["annual"]["statewide"]
    .groupby(total_area_burned["historical"]["annual"]["statewide"].index // 10 * 10)
    .mean()
)
total_area_burned["historical"]["rolling"]["statewide"] = (
    total_area_burned["historical"]["annual"]["statewide"]
    .rolling(rolling_window)
    .mean()
)

# Compute total area burned (future)
total_area_burned["future"] = {}
for treatment in treatment_options:
    total_area_burned["future"][treatment] = {}
    for scenario in scenarios:
        total_area_burned["future"][treatment][scenario] = {}
        for model in models:

            total_area_burned["future"][treatment][scenario][model] = {
                "annual": pd.DataFrame(),
                "rolling": pd.DataFrame(),
                "decadal": pd.DataFrame(),
            }

            for zone in zones:
                fragment = "_".join([fmo_prefix, scenario, model])
                filename = "_".join(
                    ["alfresco_totalareaburned", zone, fragment, date_postfix]
                )
                filename += ".csv"

                input_file = os.path.join(
                    data_dir, treatment, fragment, "total_area_burned", filename
                )

                source_data = pd.read_csv(input_file, index_col=0)
                # Annual mean across ALFRESCO reps
                total_area_burned["future"][treatment][scenario][model]["annual"][
                    zone
                ] = to_acres(source_data.mean(axis=1))
                # Rolling mean
                total_area_burned["future"][treatment][scenario][model]["rolling"][
                    zone
                ] = (
                    total_area_burned["future"][treatment][scenario][model]["annual"][
                        zone
                    ]
                    .rolling(rolling_window)
                    .mean()
                )

                # Decadal mean
                total_area_burned["future"][treatment][scenario][model]["decadal"][
                    zone
                ] = (
                    total_area_burned["future"][treatment][scenario][model]["annual"][
                        zone
                    ]
                    .groupby(
                        total_area_burned["future"][treatment][scenario][model][
                            "annual"
                        ][zone].index
                        // 10
                        * 10
                    )
                    .mean()
                )

            # Statewide sum
            total_area_burned["future"][treatment][scenario][model]["annual"][
                "statewide"
            ] = total_area_burned["future"][treatment][scenario][model]["annual"].sum(
                axis=1
            )
            total_area_burned["future"][treatment][scenario][model]["decadal"][
                "statewide"
            ] = total_area_burned["future"][treatment][scenario][model]["decadal"].sum(
                axis=1
            )
            total_area_burned["future"][treatment][scenario][model]["rolling"][
                "statewide"
            ] = (
                total_area_burned["future"][treatment][scenario][model]["annual"][
                    "statewide"
                ]
                .rolling(rolling_window)
                .mean()
            )

        # Compute 5-model averages
        total_area_burned["future"][treatment][scenario]["5modelavg"] = {
            "annual": pd.DataFrame(),
            "rolling": pd.DataFrame(),
            "decadal": pd.DataFrame(),
        }

        for zone in zones_with_statewide:
            model_averages = pd.DataFrame()
            for model in models:
                model_averages[model] = total_area_burned["future"][treatment][
                    scenario
                ][model]["annual"][zone]

            total_area_burned["future"][treatment][scenario]["5modelavg"]["annual"][
                zone
            ] = model_averages.mean(axis=1)

            # Decadal mean
            total_area_burned["future"][treatment][scenario]["5modelavg"]["decadal"][
                zone
            ] = (
                total_area_burned["future"][treatment][scenario]["5modelavg"]["annual"][
                    zone
                ]
                .groupby(
                    total_area_burned["future"][treatment][scenario]["5modelavg"][
                        "annual"
                    ][zone].index
                    // 10
                    * 10
                )
                .mean()
            )

            total_area_burned["future"][treatment][scenario]["5modelavg"]["rolling"][
                zone
            ] = (
                total_area_burned["future"][treatment][scenario]["5modelavg"]["annual"][
                    zone
                ]
                .rolling(rolling_window)
                .mean()
            )

with open("total_area_burned.pickle", "wb") as handle:
    pickle.dump(total_area_burned, handle)
