"""

Preprocess Alfresco data into shapes that can
be easily used by JFSP app.

"""

# pylint: disable=invalid-name

import os
import pandas as pd
from pprint import pprint

data_dir = "data"

# Some static stuff we glue to make filenames
fmo_prefix = "fmo99s95i"
date_postfix = "2014_2099"

historical_categories = ["cru_none", "cru_tx0"]
modelled_categories = ["gcm_tx0", "gcm_tx1", "gcm_tx2"]

scenarios = ["rcp45", "rcp60", "rcp85"]

models = ["CCSM4", "GFDL-CM3", "GISS-E2-R", "IPSL-CM5A-LR", "MRI-CGCM3"]

zones = [
    "ChugachNationalForest",
    "CopperRiverArea",
    "DeltaArea",
    "FairbanksArea",
    "GalenaZone",
    "InteriorBoreal",
    "KenaiKodiakArea",
    "MatSuArea",
    "MilitaryZone",
    "SouthcentralBoreal",
    "SouthwestArea",
    "TananaZone",
    "TokArea",
    "UpperYukonZone",
]

total_area_burned = {}

for category in modelled_categories:
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
                total_area_burned[category][scenario][model][zone] = source_data.mean(
                    axis=1
                )

            # Do average for all zones here?
            total_area_burned[category][scenario][model][
                "statewide"
            ] = total_area_burned[category][scenario][model].sum(axis=1)
            pprint(total_area_burned[category][scenario][model])
