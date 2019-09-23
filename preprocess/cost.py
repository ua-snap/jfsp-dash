"""
Compute fire cost estimates.

Costs: data structure definition -- tidy table.  Columns:

year
treatment option (tx0, tx1, tx2)
scenario
fire management option (c, f, l, m, total = sum)
area (square km)
cost (computed/documented below)

"""
# pylint: disable=invalid-name,import-error

import os
import numpy as np
import pandas as pd
import luts

# Create seeded pseudorandom map of years to [2011...2016]
# Save to CSV so this mapping can be checked.
np.random.seed(luts.random_seed)
random_cost_map = pd.DataFrame(index=pd.RangeIndex(start=1950, stop=2100))
random_cost_map["year"] = np.random.randint(2011, 2017, random_cost_map.shape[0])
random_cost_map.to_csv("random_year_map.csv")


def get_cost_filename(data_dir, treatment, scenario, model, option):
    """
    Returns the filename for a given place/zone/forest type.
    """
    if scenario == "historical":
        return os.path.join(
            data_dir,
            "FireManagementOptions",
            luts.historical_categories[1],  # cru_tx0 only
            luts.historical_fmo_prefix,
            "total_area_burned",
            "_".join(
                [
                    "alfresco_totalareaburned",
                    option,
                    luts.historical_fmo_prefix,
                    luts.historical_date_postfix,
                ]
            )
            + ".csv",
        )

    # Future
    fragment = "_".join([luts.fmo_prefix, scenario, model])
    filename = "_".join(
        ["alfresco_totalareaburned", option, fragment, luts.date_postfix]
    )
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
    return round(luts.to_acres(row.area) * cost_factor)


def get_cost_df(data_dir, year_range, treatment, scenario, model):
    """ Return a clean dataframe of costs """
    tidied_costs = []
    for option in luts.fmo_options:
        filename = get_cost_filename(data_dir, treatment, scenario, model, option)
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
            # Continue, ignoring missing values

    return tidied_costs


def process(data_dir):
    """ Produce cost estimates. """

    cost_columns = ["treatment", "scenario", "model", "option", "area", "cost"]
    costs = pd.DataFrame(columns=cost_columns)

    # Historical
    costs = costs.append(
        get_cost_df(data_dir, luts.historical_year_range, "cru_tx0", "historical", "")
    )

    # Future
    for treatment in luts.treatment_options:
        for scenario in luts.scenarios:
            for model in luts.models:
                costs = costs.append(
                    get_cost_df(
                        data_dir, luts.future_year_range, treatment, scenario, model
                    )
                )

    # Compute 5-model averages
    costs.index.name = "year"
    for treatment in luts.treatment_options:
        for scenario in luts.scenarios:
            for option in luts.fmo_options:
                tidied = pd.DataFrame(index=luts.future_year_range)
                tidied.index.name = "year"
                tidied = tidied.assign(
                    treatment=treatment,
                    scenario=scenario,
                    model="5modelavg",
                    option=option,
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

    models_with_5modelavg = luts.models.copy()
    models_with_5modelavg.update({"5modelavg": "5modelavg"})

    for treatment in luts.treatment_options:
        for scenario in luts.scenarios:
            for model in models_with_5modelavg:
                tidied = pd.DataFrame(index=luts.future_year_range)
                tidied.index.name = "year"
                tidied = tidied.assign(
                    treatment=treatment, scenario=scenario, model=model, option="total"
                )
                temp_costs_column = (
                    costs[
                        (costs.treatment == treatment)
                        & (costs.scenario == scenario)
                        & (costs.model == model)
                    ]
                    .groupby("year")
                    .sum(axis=1)
                )
                tidied["area"] = temp_costs_column["area"]
                tidied["cost"] = temp_costs_column["cost"]
                costs = costs.append(tidied)

    costs.to_csv("costs.csv")
    costs.to_pickle("costs.pickle")
