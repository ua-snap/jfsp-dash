"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

# pylint: disable=invalid-name

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

total_area_burned = {}


def to_acres(km2):
    """ square KM to acres """
    return round(km2 * 247.11)


# Compute total area burned (historical)
total_area_burned["historical"] = pd.DataFrame()
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
    total_area_burned["historical"][zone] = to_acres(source_data.mean(axis=1))

total_area_burned["historical"][
    "statewide"
] = total_area_burned["historical"].sum(axis=1)

# Compute total area burned (future)
for category in treatment_options:
    total_area_burned[category] = {}
    for scenario in scenarios:
        total_area_burned[category][scenario] = {}
        for model in models:
            total_area_burned[category][scenario][model] = {}
            # Accumulate some totals as we go.
            total_area_burned[category][scenario][model] = pd.DataFrame()
            for zone in zones:
                fragment = "_".join([fmo_prefix, scenario, model])
                filename = "_".join(
                    ["alfresco_totalareaburned", zone, fragment, date_postfix]
                )
                filename += ".csv"

                input_file = os.path.join(
                    data_dir, category, fragment, "total_area_burned", filename
                )

                source_data = pd.read_csv(input_file, index_col=0)
                total_area_burned[category][scenario][model][zone] = to_acres(
                    source_data.mean(axis=1)
                )

            # Do average for all zones here?
            total_area_burned[category][scenario][model][
                "statewide"
            ] = total_area_burned[category][scenario][model].sum(axis=1)

with open("total_area_burned.pickle", "wb") as handle:
    pickle.dump(total_area_burned, handle)
