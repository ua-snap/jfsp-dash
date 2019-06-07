"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

# pylint: disable=invalid-name,import-error,line-too-long

import os
import pickle
from pprint import pprint
import pandas as pd
from luts import zones, scenarios, models, treatment_options, ecoregions

data_dir = "data"

# Some static stuff we glue to make filenames
spatial_prefix_map = {"EcoregionsLevel2": ecoregions, "FireManagementZones": zones}

fmo_prefix = "fmo99s95i"
historical_fmo_prefix = "fmo99s95i_historical_CRU32"
date_postfix = "2014_2099"
historical_date_postfix = "1950_2013"
historical_categories = ["cru_none", "cru_tx0"]

rolling_window = 30  # years for rolling window computations
total_area_burned = {}


def to_acres(km2):
    """ square KM to acres """
    return round(km2 * 247.11)


""" Veg counts: data structure

Tidy table.  Columns:
year (index), treatment, scenario, RCP, Region, DeciduousArea, ConiferousArea

"""
forest_types = ["Deciduous", "BlackSpruce", "WhiteSpruce"]
veg_counts = pd.DataFrame(
    columns=[
        "year",
        "treatment",
        "scenario",
        "rcp",
        "region",
        "deciduous",
        "coniferous",
    ]
)
for spatial_prefix, regions in spatial_prefix_map.items():
    for zone in regions:
        for forest in forest_types:
            input_file = os.path.join(
                data_dir,
                spatial_prefix,
                historical_categories[1],
                historical_fmo_prefix,  # cru_tx0 only
                "veg_counts",
                "_".join(
                    [
                        "alfresco_vegcounts",
                        zone,
                        forest,
                        historical_fmo_prefix,
                        historical_date_postfix,
                    ]
                )
                + ".csv",
            )
            if os.path.isfile(input_file):
                source_data = pd.read_csv(input_file, index_col=0)

                pprint(source_data)

exit()

""" Total area burned: Data structures to build:

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
total_area_burned["historical"] = {
    "annual": pd.DataFrame(),
    "rolling": pd.DataFrame(),
    "decadal": pd.DataFrame(),
}
total_area_burned["future"] = {}

# Keep these loosely bound for the moment, not sure
# if we'll need to iterate the incoming data more,
# so keep it dumb-simple here.
needs_init = True
for spatial_prefix, regions in spatial_prefix_map.items():
    for zone in regions:
        input_file = os.path.join(
            data_dir,
            spatial_prefix,
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
        total_area_burned["historical"]["annual"][zone] = to_acres(
            source_data.mean(axis=1)
        )
        total_area_burned["historical"]["decadal"][zone] = (
            total_area_burned["historical"]["annual"][zone]
            .groupby(total_area_burned["historical"]["annual"][zone].index // 10 * 10)
            .mean()
        )
        total_area_burned["historical"]["rolling"][zone] = (
            total_area_burned["historical"]["annual"][zone]
            .rolling(rolling_window)
            .mean()
        )

    statewide_name = "statewide_" + spatial_prefix
    total_area_burned["historical"]["annual"][statewide_name] = total_area_burned[
        "historical"
    ]["annual"].sum(axis=1)
    total_area_burned["historical"]["decadal"][statewide_name] = (
        total_area_burned["historical"]["annual"][statewide_name]
        .groupby(
            total_area_burned["historical"]["annual"][statewide_name].index // 10 * 10
        )
        .mean()
    )
    total_area_burned["historical"]["rolling"][statewide_name] = (
        total_area_burned["historical"]["annual"][statewide_name]
        .rolling(rolling_window)
        .mean()
    )

    # Compute total area burned (future)

    for treatment in treatment_options:
        if needs_init:
            total_area_burned["future"][treatment] = {}
        for scenario in scenarios:
            if needs_init:
                total_area_burned["future"][treatment][scenario] = {}
            for model in models:
                if needs_init:
                    total_area_burned["future"][treatment][scenario][model] = {
                        "annual": pd.DataFrame(),
                        "rolling": pd.DataFrame(),
                        "decadal": pd.DataFrame(),
                    }

                for zone in regions:
                    fragment = "_".join([fmo_prefix, scenario, model])
                    filename = "_".join(
                        ["alfresco_totalareaburned", zone, fragment, date_postfix]
                    )
                    filename += ".csv"

                    input_file = os.path.join(
                        data_dir,
                        spatial_prefix,
                        treatment,
                        fragment,
                        "total_area_burned",
                        filename,
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
                        total_area_burned["future"][treatment][scenario][model][
                            "annual"
                        ][zone]
                        .rolling(rolling_window)
                        .mean()
                    )

                    # Decadal mean
                    total_area_burned["future"][treatment][scenario][model]["decadal"][
                        zone
                    ] = (
                        total_area_burned["future"][treatment][scenario][model][
                            "annual"
                        ][zone]
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
                statewide_name = "statewide_" + spatial_prefix
                total_area_burned["future"][treatment][scenario][model]["annual"][
                    statewide_name
                ] = total_area_burned["future"][treatment][scenario][model][
                    "annual"
                ].sum(
                    axis=1
                )
                total_area_burned["future"][treatment][scenario][model]["decadal"][
                    statewide_name
                ] = total_area_burned["future"][treatment][scenario][model][
                    "decadal"
                ].sum(
                    axis=1
                )
                total_area_burned["future"][treatment][scenario][model]["rolling"][
                    statewide_name
                ] = (
                    total_area_burned["future"][treatment][scenario][model]["annual"][
                        statewide_name
                    ]
                    .rolling(rolling_window)
                    .mean()
                )

            # Compute 5-model averages
            if needs_init:
                total_area_burned["future"][treatment][scenario]["5modelavg"] = {
                    "annual": pd.DataFrame(),
                    "rolling": pd.DataFrame(),
                    "decadal": pd.DataFrame(),
                }

            # Add statewide to complete iteration of all regions
            regions_with_statewide = regions.copy()
            regions_with_statewide.update({statewide_name: statewide_name})

            for zone in regions_with_statewide:
                model_averages = pd.DataFrame()
                for model in models:
                    model_averages[model] = total_area_burned["future"][treatment][
                        scenario
                    ][model]["annual"][zone]

                total_area_burned["future"][treatment][scenario]["5modelavg"]["annual"][
                    zone
                ] = model_averages.mean(axis=1)

                # Decadal mean
                total_area_burned["future"][treatment][scenario]["5modelavg"][
                    "decadal"
                ][zone] = (
                    total_area_burned["future"][treatment][scenario]["5modelavg"][
                        "annual"
                    ][zone]
                    .groupby(
                        total_area_burned["future"][treatment][scenario]["5modelavg"][
                            "annual"
                        ][zone].index
                        // 10
                        * 10
                    )
                    .mean()
                )

                total_area_burned["future"][treatment][scenario]["5modelavg"][
                    "rolling"
                ][zone] = (
                    total_area_burned["future"][treatment][scenario]["5modelavg"][
                        "annual"
                    ][zone]
                    .rolling(rolling_window)
                    .mean()
                )
    needs_init = False

with open("total_area_burned.pickle", "wb") as handle:
    pickle.dump(total_area_burned, handle)
