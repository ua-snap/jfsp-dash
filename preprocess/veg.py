""" Veg counts: data structure definition

Tidy table.  Columns:
year (index), treatment, scenario, RCP, Region, DeciduousArea, ConiferousArea

"""
# pylint: disable=invalid-name,import-error

import os
import pandas as pd
import luts

forest_types = ["Deciduous", "BlackSpruce", "WhiteSpruce"]
veg_columns = ["treatment", "scenario", "model", "region", "deciduous", "coniferous"]


def get_veg_filename(
    data_dir, spatial_prefix, treatment, scenario, model, region, forest
):
    """
    Returns the filename for a given place/zone/forest type.
    """
    if scenario == "historical":
        return os.path.join(
            data_dir,
            spatial_prefix,
            luts.historical_categories[1],  # cru_tx0 only
            luts.historical_fmo_prefix,
            "veg_counts",
            "_".join(
                [
                    "alfresco_vegcounts",
                    region,
                    forest,
                    luts.historical_fmo_prefix,
                    luts.historical_date_postfix,
                ]
            )
            + ".csv",
        )

    fragment = "_".join([luts.fmo_prefix, scenario, model])
    filename = "_".join(
        ["alfresco_vegcounts", region, forest, fragment, luts.date_postfix]
    )
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
    data_dir, year_range, spatial_prefix, treatment, scenario, model, region
):
    """ Read and parse veg count data """
    tidied = pd.DataFrame(index=year_range)
    tidied = tidied.assign(
        treatment=treatment, scenario=scenario, model=model, region=region
    )
    deciduous_filename = get_veg_filename(
        data_dir, spatial_prefix, treatment, scenario, model, region, "Deciduous"
    )
    white_spruce_filename = get_veg_filename(
        data_dir, spatial_prefix, treatment, scenario, model, region, "WhiteSpruce"
    )
    black_spruce_filename = get_veg_filename(
        data_dir, spatial_prefix, treatment, scenario, model, region, "BlackSpruce"
    )

    if os.path.isfile(deciduous_filename):
        deciduous = pd.read_csv(deciduous_filename, index_col=0)
        tidied = tidied.assign(deciduous=deciduous.median(axis=1))
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
            coniferous=white_spruce.median(axis=1) + black_spruce.median(axis=1)
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
        tidied = tidied.assign(coniferous=white_spruce.median(axis=1))
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
        tidied = tidied.assign(coniferous=black_spruce.median(axis=1))
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


def process(data_dir):
    """ Read source files and produce combined veg count tidied df """
    # Read and combine
    veg_counts = pd.DataFrame(columns=veg_columns)
    temp_veg_dfs = []

    # Process counts for all historical/modelled data
    for spatial_prefix, regions in luts.spatial_prefix_map.items():
        # Historical
        for region in regions:
            temp_veg_dfs.append(
                get_tidied_veg_count_df(
                    data_dir,
                    luts.historical_year_range,
                    spatial_prefix,
                    "cru_tx0",
                    "historical",
                    "",
                    region,
                )
            )

        # Future
        for treatment in luts.treatment_options:
            for scenario in luts.scenarios:
                for model in luts.models:
                    for region in regions:
                        temp_veg_dfs.append(
                            get_tidied_veg_count_df(
                                data_dir,
                                luts.future_year_range,
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
    for spatial_prefix, regions in luts.spatial_prefix_map.items():
        for treatment in luts.treatment_options:
            for scenario in luts.scenarios:
                for region in regions:
                    tidied = pd.DataFrame(index=luts.future_year_range)
                    tidied = tidied.assign(
                        treatment=treatment,
                        scenario=scenario,
                        model=luts.MODEL_AVG,
                        region=region,
                    )
                    tidied["deciduous"] = (
                        veg_counts[
                            (veg_counts.treatment == treatment)
                            & (veg_counts.scenario == scenario)
                            & (veg_counts.region == region)
                        ]
                        .groupby("year")
                        .median()["deciduous"]
                    )
                    tidied["coniferous"] = (
                        veg_counts[
                            (veg_counts.treatment == treatment)
                            & (veg_counts.scenario == scenario)
                            & (veg_counts.region == region)
                        ]
                        .groupby("year")
                        .median()["coniferous"]
                    )
                    temp_veg_dfs.append(tidied)

    veg_counts = veg_counts.append(temp_veg_dfs)

    models_with_statewide = luts.models.copy()
    models_with_statewide.update({luts.MODEL_AVG: luts.MODEL_AVG})

    # Statewide sums -- all FMZs
    tidied = pd.DataFrame(index=luts.historical_year_range)
    tidied = tidied.assign(
        treatment="cru_tx0", scenario="historical", model="", region=luts.STATEWIDE
    )
    t = veg_counts.loc[veg_counts["region"].isin(luts.zones)]
    for year in luts.historical_year_range:
        tidied.at[year, "deciduous"] = t.loc[year].sum()["deciduous"]
        tidied.at[year, "coniferous"] = t.loc[year].sum()["coniferous"]

    veg_counts = veg_counts.append(tidied)

    for treatment in luts.treatment_options:
        for scenario in luts.scenarios:
            for model in models_with_statewide:
                tidied = pd.DataFrame(index=luts.future_year_range)
                tidied = tidied.assign(
                    treatment=treatment,
                    scenario=scenario,
                    model=model,
                    region=luts.STATEWIDE,
                )
                t = veg_counts.loc[
                    (veg_counts["region"].isin(luts.zones))
                    & (veg_counts["treatment"] == treatment)
                    & (veg_counts["scenario"] == scenario)
                    & (veg_counts["model"] == model)
                ]
                for year in luts.future_year_range:
                    tidied.at[year, "deciduous"] = t.loc[year].sum()["deciduous"]
                    tidied.at[year, "coniferous"] = t.loc[year].sum()["coniferous"]

                veg_counts = veg_counts.append(tidied)

    veg_counts.to_pickle("./veg_counts.pickle")
    veg_counts.to_csv("./veg_counts.csv")
