"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

# pylint: disable=invalid-name,import-error,line-too-long
# pylint: disable=W0621,W0105

import os
import pickle
import pdb
from pprint import pprint
import numpy as np
import pandas as pd
from luts import zones, scenarios, models, treatment_options, ecoregions, fmo_options, fmo_costs

data_dir = "data"

# Some static stuff we glue to make filenames
spatial_prefix_map = {"EcoregionsLevel2": ecoregions, "FireManagementZones": zones}

fmo_prefix = "fmo99s95i"
historical_fmo_prefix = "fmo99s95i_historical_CRU32"
date_postfix = "2014_2099"
historical_date_postfix = "1950_2013"
historical_categories = ["cru_none", "cru_tx0"]
historical_year_range = pd.RangeIndex(start=1950, stop=2014)
future_year_range = pd.RangeIndex(start=2014, stop=2100)
random_seed = 42 # random seed for reproducible random numbers

def to_acres(km2):
    """ square KM to acres """
    return round(km2 * 247.11)


def from_acres(acres):
    """ return square KM """
    return round(acres / 247.11)


""" Costs: data structure definition
Tidy table.  Columns:
year (index), treatment, scenario, rcp, region, fmo, area burned, cost

"""
cost_columns = ["treatment", "scenario", "model", "option", "area", "cost"]
costs = pd.DataFrame(columns=cost_columns)
random_cost_map = pd.DataFrame(index=pd.RangeIndex(start=1950, stop=2100))

# Create seeded pseudorandom map of years to [2011...2017]
# Save to CSV so this mapping can be checked.
np.random.seed(random_seed)
random_cost_map["year"] = np.random.randint(2011, 2018, random_cost_map.shape[0])
random_cost_map.to_csv("random_year_map.csv")

def get_cost_filename(treatment, scenario, model, option):
    """
    Returns the filename for a given place/zone/forest type.
    """
    if scenario == "historical":
        return os.path.join(
            data_dir,
            "FireManagementOptions",
            historical_categories[1],  # cru_tx0 only
            historical_fmo_prefix,
            "total_area_burned",
            "_".join(
                [
                    "alfresco_totalareaburned",
                    option,
                    historical_fmo_prefix,
                    historical_date_postfix,
                ]
            )
            + ".csv",
        )

    # Future
    fragment = "_".join([fmo_prefix, scenario, model])
    filename = "_".join(["alfresco_totalareaburned", option, fragment, date_postfix])
    filename += ".csv"

    input_file = os.path.join(
        data_dir,
        "FireManagementOptions",
        treatment,
        fragment,
        "total_area_burned",
        filename,
    )
    return input_file

def compute_row_cost(row):
    """
    Broken out here for clarity.

    Given a row with year (as index), option, and area burned,
    look up the corresponding year in the random_cost_map
    dataframe and use that to fetch the costs from the
    luts.fmo_costs dict.  Each year is assigned a random
    map to a prior year of known costs.
    """
    mapped_year = random_cost_map.loc[row.name].year
    cost_factor = luts.fmo_costs[mapped_year][row.option]
    return round(row.area * cost_factor)


def get_cost_df(year_range, treatment, scenario, model):
    """ Return a clean dataframe of costs """
    tidied_costs = []
    for option in luts.fmo_options:
        filename = get_cost_filename(treatment, scenario, model, option)
        if os.path.isfile(filename):
            tidied = pd.DataFrame(index=year_range)
            tidied = tidied.assign(
                treatment=treatment, scenario=scenario, model=model, option=option
            )
            temp_costs = pd.read_csv(filename, index_col=0)
            reps_mean = temp_costs.mean(axis=1)  # compute mean of reps
            tidied = tidied.assign(area=reps_mean)
            tidied["cost"] = tidied.apply(compute_row_cost, axis=1)
            tidied_costs.append(tidied)
        else:
            print("No FMO file found {}".format(filename))
            exit()

    return tidied_costs


# Historical
costs = costs.append(get_cost_df(historical_year_range, "cru_tx0", "historical", ""))

# Future
for treatment in luts.treatment_options:
    for scenario in luts.scenarios:
        for model in luts.models:
            costs = costs.append(
                get_cost_df(future_year_range, treatment, scenario, model)
            )

# Compute 5-model averages
costs.index.name = "year"
for treatment in luts.treatment_options:
    for scenario in luts.scenarios:
        for option in luts.fmo_options:
            tidied = pd.DataFrame(index=future_year_range)
            tidied.index.name = "year"
            tidied = tidied.assign(
                treatment=treatment, scenario=scenario, model="5modelavg", option=option
            )
            temp_costs_column = (
                costs[
                    (costs.treatment == treatment)
                    & (costs.scenario == scenario)
                    & (costs.option == option)
                ]
                .groupby("year")
                .mean()["area"]
            )
            tidied["area"] = temp_costs_column
            tidied["cost"] = tidied.apply(compute_row_cost, axis=1)
            costs = costs.append(tidied)

costs.to_csv("costs.csv")
costs.to_pickle("costs.pickle")
exit()

""" Veg counts: data structure definition

Tidy table.  Columns:
year (index), treatment, scenario, RCP, Region, DeciduousArea, ConiferousArea

"""
forest_types = ["Deciduous", "BlackSpruce", "WhiteSpruce"]
veg_columns = ["treatment", "scenario", "model", "region", "deciduous", "coniferous"]

def get_veg_filename(spatial_prefix, treatment, scenario, model, region, forest):
    """
    Returns the filename for a given place/zone/forest type.
    """
    if scenario is "historical":
        return os.path.join(
            data_dir,
            spatial_prefix,
            historical_categories[1],  # cru_tx0 only
            historical_fmo_prefix,
            "veg_counts",
            "_".join(
                [
                    "alfresco_vegcounts",
                    region,
                    forest,
                    historical_fmo_prefix,
                    historical_date_postfix,
                ]
            )
            + ".csv",
        )

    fragment = "_".join([fmo_prefix, scenario, model])
    filename = "_".join(["alfresco_vegcounts", region, forest, fragment, date_postfix])
    filename += ".csv"

    input_file = os.path.join(
        data_dir, spatial_prefix, treatment, fragment, "veg_counts", filename
    )
    return input_file


def print_vegcount_log(note, spatial_prefix, treatment, scenario, model, region):
    """
    Tiny helper to report missing files in the veg counts.
    """
    print(
        "Exception, {} {} {} {} {} {}".format(
            note, spatial_prefix, treatment, scenario, model, region
        )
    )


def get_tidied_veg_count_df(
    year_range, spatial_prefix, treatment, scenario, model, region
):
    tidied = pd.DataFrame(index=year_range)
    tidied = tidied.assign(
        treatment=treatment, scenario=scenario, model=model, region=region
    )
    deciduous_filename = get_veg_filename(
        spatial_prefix, treatment, scenario, model, region, "Deciduous"
    )
    white_spruce_filename = get_veg_filename(
        spatial_prefix, treatment, scenario, model, region, "WhiteSpruce"
    )
    black_spruce_filename = get_veg_filename(
        spatial_prefix, treatment, scenario, model, region, "BlackSpruce"
    )

    if os.path.isfile(deciduous_filename):
        deciduous = pd.read_csv(deciduous_filename, index_col=0)
        tidied = tidied.assign(deciduous=deciduous.mean(axis=1))
    else:
        print_vegcount_log(
            "NO DECIDUOUS found", spatial_prefix, treatment, scenario, model, region
        )

    # Handle cases where either black or white spruce
    # may be missing in data
    if os.path.isfile(white_spruce_filename) and os.path.isfile(black_spruce_filename):
        white_spruce = pd.read_csv(white_spruce_filename, index_col=0)
        black_spruce = pd.read_csv(black_spruce_filename, index_col=0)
        tidied = tidied.assign(
            coniferous=white_spruce.mean(axis=1) + black_spruce.mean(axis=1)
        )
    elif os.path.isfile(white_spruce_filename):
        print_vegcount_log(
            "Only WHITE spruce found",
            spatial_prefix,
            treatment,
            scenario,
            model,
            region,
        )
        white_spruce = pd.read_csv(white_spruce_filename, index_col=0)
        tidied = tidied.assign(coniferous=white_spruce.mean(axis=1))
    elif os.path.isfile(black_spruce_filename):
        print_vegcount_log(
            "Only BLACK spruce found",
            spatial_prefix,
            treatment,
            scenario,
            model,
            region,
        )
        black_spruce = pd.read_csv(black_spruce_filename, index_col=0)
        tidied = tidied.assign(coniferous=black_spruce.mean(axis=1))
    else:
        print_vegcount_log(
            "NEITHER black or white spruce found",
            spatial_prefix,
            treatment,
            scenario,
            model,
            region,
        )
        exit()

    return tidied


# Read and combine
veg_counts = pd.DataFrame(columns=veg_columns)
temp_veg_dfs = []

# Process counts for all historical/modelled data
for spatial_prefix, regions in spatial_prefix_map.items():
    # Historical
    for region in regions:
        temp_veg_dfs.append(
            get_tidied_veg_count_df(
                historical_year_range,
                spatial_prefix,
                "cru_tx0",
                "historical",
                "",
                region,
            )
        )

    # Future
    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models:
                for region in regions:
                    temp_veg_dfs.append(
                        get_tidied_veg_count_df(
                            future_year_range,
                            spatial_prefix,
                            treatment,
                            scenario,
                            model,
                            region,
                        )
                    )

veg_counts = pd.concat(temp_veg_dfs)
veg_counts.index.name = "year"

# Compute 5-model averages
temp_veg_dfs = []
for spatial_prefix, regions in spatial_prefix_map.items():
    for treatment in treatment_options:
        for scenario in scenarios:
            for region in regions:
                tidied = pd.DataFrame(index=future_year_range)
                tidied = tidied.assign(
                    treatment=treatment,
                    scenario=scenario,
                    model="5modelavg",
                    region=region,
                )
                tidied["deciduous"] = (
                    veg_counts[
                        (veg_counts.treatment == treatment)
                        & (veg_counts.scenario == scenario)
                        & (veg_counts.region == region)
                    ]
                    .groupby("year")
                    .mean()["deciduous"]
                )
                tidied["coniferous"] = (
                    veg_counts[
                        (veg_counts.treatment == treatment)
                        & (veg_counts.scenario == scenario)
                        & (veg_counts.region == region)
                    ]
                    .groupby("year")
                    .mean()["coniferous"]
                )
                temp_veg_dfs.append(tidied)

veg_counts = veg_counts.append(temp_veg_dfs)

models_with_statewide = models.copy()
models_with_statewide.update({"5modelavg": "5modelavg"})

# Statewide sums
for spatial_prefix, regions in spatial_prefix_map.items():
    tidied = pd.DataFrame(index=historical_year_range)
    tidied = tidied.assign(
        treatment="cru_tx0",
        scenario="historical",
        model="",
        region="statewide_" + spatial_prefix,
    )
    t = veg_counts.loc[veg_counts["region"].isin(regions)]
    for year in historical_year_range:
        tidied.at[year, "deciduous"] = t.loc[year].sum()["deciduous"]
        tidied.at[year, "coniferous"] = t.loc[year].sum()["coniferous"]

    veg_counts = veg_counts.append(tidied)

    for treatment in treatment_options:
        for scenario in scenarios:
            for model in models_with_statewide:
                tidied = pd.DataFrame(index=future_year_range)
                tidied = tidied.assign(
                    treatment=treatment,
                    scenario=scenario,
                    model=model,
                    region="statewide_" + spatial_prefix,
                )
                t = veg_counts.loc[
                    (veg_counts["region"].isin(regions))
                    & (veg_counts["treatment"] == treatment)
                    & (veg_counts["scenario"] == scenario)
                    & (veg_counts["model"] == model)
                ]
                for year in future_year_range:
                    tidied.at[year, "deciduous"] = t.loc[year].sum()["deciduous"]
                    tidied.at[year, "coniferous"] = t.loc[year].sum()["coniferous"]

                veg_counts = veg_counts.append(tidied)

veg_counts.to_pickle("./veg_counts.pickle")
veg_counts.to_csv("./veg_counts.csv")

""" Total area burned: Data structures to build:

total_area_burned, decadal_area_burned
    historical
        annual: DataFrame(cols = zones)
        decadal: DataFrame(cols = zones)
    future
        treatment
            scenario
                model
                    annual: DataFrame(cols = zones)
                    decadal: DataFrame(cols = zones)

"""

# Compute total area burned (historical)
total_area_burned = {}
total_area_burned["historical"] = {"annual": pd.DataFrame(), "decadal": pd.DataFrame()}
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

            # Compute 5-model averages
            if needs_init:
                total_area_burned["future"][treatment][scenario]["5modelavg"] = {
                    "annual": pd.DataFrame(),
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

    needs_init = False

with open("total_area_burned.pickle", "wb") as handle:
    pickle.dump(total_area_burned, handle)
