"""
Produces and writes a file in the current working
directory, total_area_burned.pickle (and CSV).
"""
# pylint: disable=C0103,C0301,too-many-arguments,import-error

import os
import pandas as pd
import luts
from pprint import pprint
import pdb

def get_source_filename(data_dir, spatial_prefix, treatment, prefix, postfix, region):
    """ Given the parameters, return a filename to the source data. """
    input_file = os.path.join(
        data_dir,
        spatial_prefix,
        treatment,
        prefix,
        "total_area_burned",
        "_".join(["alfresco_totalareaburned", region, prefix, postfix]) + ".csv",
    )
    return input_file


def process(data_dir):
    """
    Total area burned: create a table structure with these columns:

    year(index), treatment, scenario, model, region, area
    """

    cols = ["treatment", "scenario", "model", "region", "area"]
    total_area_burned = pd.DataFrame(columns=cols)
    total_area_burned.index.name = "year"

    for spatial_prefix, regions in luts.spatial_prefix_map.items():
        for region in regions:
            # Historical
            t = pd.DataFrame(index=luts.historical_year_range, columns=cols)
            t = t.assign(treatment=luts.historical_categories[1], region=region)
            input_file = get_source_filename(
                data_dir,
                spatial_prefix,
                luts.historical_categories[1],
                luts.historical_fmo_prefix,
                luts.historical_date_postfix,
                region
            )
            d = pd.read_csv(input_file, index_col=0)
            t["area"] = d.mean(axis=1)
            total_area_burned = total_area_burned.append(t)

            # Future
            for treatment in luts.treatment_options:
                for scenario in luts.scenarios:
                    for model in luts.models:

                        prefix = "_".join([luts.fmo_prefix, scenario, model])
                        filename = "_".join(
                            [
                                "alfresco_totalareaburned",
                                region,
                                prefix,
                                luts.date_postfix,
                            ]
                        )
                        filename += ".csv"

                        input_file = get_source_filename(
                            data_dir,
                            spatial_prefix,
                            treatment,
                            prefix,
                            luts.date_postfix,
                            region
                        )

                        t = pd.DataFrame(index=luts.future_year_range, columns=cols)
                        t = t.assign(treatment=treatment, scenario=scenario, model=model, region=region)
                        d = pd.read_csv(input_file, index_col=0)
                        t["area"] = d.mean(axis=1)
                        total_area_burned = total_area_burned.append(t)

    # Precompute 5-model-averages.
    # Future only.
    # Create a dataframe with models as columns, then compute mean.
    for spatial_prefix, regions in luts.spatial_prefix_map.items():
        for region in regions:
            for treatment in luts.treatment_options:
                for scenario in luts.scenarios:
                    t = pd.DataFrame(index=luts.future_year_range, columns=cols)
                    t = t.assign(treatment=treatment, scenario=scenario, model="5modelavg", region=region)
                    z = pd.DataFrame(index=luts.future_year_range, columns=luts.models)
                    for model in luts.models:
                        z[model] = total_area_burned[
                            (total_area_burned.region == region)
                            & (total_area_burned.treatment == treatment)
                            & (total_area_burned.scenario == scenario)
                            & (total_area_burned.model == model)
                        ].area

                    t["area"] = z.mean(axis=1)
                    total_area_burned = total_area_burned.append(t)

    # Precompute "statewide" totals; for our scenario,
    # "statewide" is the sum of all fire management zones.
    # Create a dataframe with the FMZs as the columns, then sum.
    # Historical:
    t = pd.DataFrame(index=luts.historical_year_range, columns=cols)
    t = t.assign(treatment=luts.historical_categories[1], region="AllFMZs")
    z = pd.DataFrame(index=luts.historical_year_range, columns=luts.zones)
    for zone in luts.zones:
        z[zone] = total_area_burned[
            (total_area_burned.region == zone)
            & (total_area_burned.treatment == luts.historical_categories[1])
        ].area

    t["area"] = z.sum(axis=1)
    total_area_burned = total_area_burned.append(t)

    # Future "statewide" totals, adding in 5modelavg:
    models_with_5modelavg = luts.models.copy()
    models_with_5modelavg.update({"5modelavg": "5modelavg"})
    for treatment in luts.treatment_options:
        for scenario in luts.scenarios:
            for model in models_with_5modelavg:
                t = pd.DataFrame(index=luts.future_year_range, columns=cols)
                t = t.assign(treatment=treatment, scenario=scenario, model=model, region="AllFMZs")
                z = pd.DataFrame(index=luts.future_year_range, columns=luts.zones)
                for zone in luts.zones:
                    z[zone] = total_area_burned[
                        (total_area_burned.region == zone)
                        & (total_area_burned.treatment == treatment)
                        & (total_area_burned.scenario == scenario)
                        & (total_area_burned.model == model)
                    ].area

                t["area"] = z.sum(axis=1)
                total_area_burned = total_area_burned.append(t)

    total_area_burned.to_pickle("total_area_burned.pickle")
    total_area_burned.to_csv("total_area_burned.csv")
