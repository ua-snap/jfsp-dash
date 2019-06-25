"""
Lookup tables with key names and human-readable names
"""
# pylint: disable=C0103,import-error

# Fragments used in the data preprocessing scripts.
import pandas as pd
import math
STATEWIDE = "AllFMZs"
MODEL_AVG = "5modelavg"
fmo_prefix = "fmo99s95i"
historical_fmo_prefix = "fmo99s95i_historical_CRU32"
date_postfix = "2014_2099"
historical_date_postfix = "1950_2013"
historical_categories = ["cru_none", "cru_tx0"]
historical_year_range = pd.RangeIndex(start=1950, stop=2014)
future_year_range = pd.RangeIndex(start=2014, stop=2100)
random_seed = 42  # random seed for reproducible random numbers

# Helper functions.
def to_acres(km2):
    """ square KM to acres """
    if math.isnan(km2):
        return 0
    return round(km2 * 247.11)


def from_acres(acres):
    """ return square KM """
    return round(acres / 247.11)


zones = {
    "ChugachNationalForest": "Chugach National Forest",
    "CopperRiverArea": "Copper River Area",
    "DeltaArea": "Delta Area",
    "FairbanksArea": "Fairbanks Area",
    "GalenaZone": "Galena Zone",
    "KenaiKodiakArea": "Kenai-Kodiak Area",
    "MatSuArea": "Mat-Su Area",
    "MilitaryZone": "Military Zone",
    "SouthwestArea": "Southwest Area",
    "TananaZone": "Tanana Zone",
    "TokArea": "Tok Area",
    "UpperYukonZone": "Upper Yukon Zone",
}

ecoregions = {
    "AlaskaRangeTransition": "Alaska Range Transition",
    "ArcticTundra": "Arctic Tundra",
    "BeringTaiga": "Bering Taiga",
    "BeringTundra": "Bering Tundra",
    "IntermontaneBoreal": "Intermontane Boreal",
    "PacificMountainsTransition": "Pacific Mountains Transition",
}

# Some static stuff we glue to make filenames
spatial_prefix_map = {
    "EcoregionsLevel2": ecoregions,
    "FireManagementZones": zones,
}

scenarios = {"rcp45": "RCP 4.5", "rcp60": "RCP 6.0", "rcp85": "RCP 8.5"}

models = {
    "CCSM4": "CCSM4",
    "GFDL-CM3": "GFDL-CM3",
    "GISS-E2-R": "GISS-E2-R",
    "IPSL-CM5A-LR": "IPSL-CM5A-LR",
    "MRI-CGCM3": "MRI-CGCM3",
}

veg_types = {"deciduous": "Deciduous", "coniferous": "Coniferous"}

# Only future
treatment_options = {
    "gcm_tx0": "No change (TX0)",
    "gcm_tx1": "More Full Suppression (TX1)",
    "gcm_tx2": "No Full Suppression (TX2)",
}

"""
Costs per acre broken down by FMO, 2011-2017.
"""
fmo_costs = {
    2011: {
        "C": 2459.09,
        "F": 350.73,
        "M": 16.32,
        "L": 13.90
    },
    2012: {
        "C": 473.14,
        "F": 257.41,
        "M": 22.10,
        "L": 0.30
    },
    2013: {
        "C": 12868.50,
        "F": 456.14,
        "M": 163.92,
        "L": 7.57
    },
    2014: {
        "C": 11159.65,
        "F": 76.36,
        "M": 356.08,
        "L": 92.00
    },
    2015: {
        "C": 198.39,
        "F": 88.92,
        "M": 31.28,
        "L": 10.62
    },
    2016: {
        "C": 6934.64,
        "F": 311.76,
        "M": 56.44,
        "L": 8.07
    },
    2017: {
        "C": 8439.06,
        "F": 119.61,
        "M": 534.23,
        "L": 12.04
    }
}

fmo_options = {
    "C": "Critical",
    "F": "Full",
    "M": "Modified",
    "L": "Limited"
}
