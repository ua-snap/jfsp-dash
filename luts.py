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

# Zones and ecoregions together for now
# Add additional region keys for items exposed via gui
regions = {**zones, **ecoregions}
regions["AllFMZs"] = "Full Model Extent"

# Some static stuff we glue to make filenames
spatial_prefix_map = {"EcoregionsLevel2": ecoregions, "FireManagementZones": zones}

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
    2011: {"C": 2459.09, "F": 350.73, "L": 13.98},
    2012: {"C": 473.14, "F": 257.41, "L": 1.54},
    2013: {"C": 12868.50, "F": 456.14, "L": 14.87},
    2014: {"C": 11159.65, "F": 76.36, "L": 295.43},
    2015: {"C": 198.39, "F": 88.92, "L": 13.76},
    2016: {"C": 6934.64, "F": 311.76, "L": 16.00}
}

fmo_options = {"C": "Critical", "F": "Full", "L": "Limited"}
