"""
Lookup tables with key names and human-readable names
"""
# pylint: disable=C0103

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
    "AlaskaRangeTransition":"Alaska Range Transition",
    "AleutianMeadows":"Aleutian Meadows",
    "ArcticTundra":"Arctic Tundra",
    "BeringTaiga":"Bering Taiga",
    "BeringTundra":"Bering Tundra",
    "CoastalRainforests":"Coastal Rainforests",
    "CoastMountainsTransition":"Coast Mountains Transition",
    "IntermontaneBoreal":"Intermontane Boreal",
    "PacificMountainsTransition":"Pacific Mountains Transition"
}

scenarios = {"rcp45": "RCP 4.5", "rcp60": "RCP 6.0", "rcp85": "RCP 8.5"}

models = {
    "CCSM4": "CCSM4",
    "GFDL-CM3": "GFDL-CM3",
    "GISS-E2-R": "GISS-E2-R",
    "IPSL-CM5A-LR": "IPSL-CM5A-LR",
    "MRI-CGCM3": "MRI-CGCM3",
}

veg_types = {
    "deciduous": "Deciduous",
    "coniferous": "Coniferous"
}

# Only future
treatment_options = {"gcm_tx0":"Status quo", "gcm_tx1":"More FMO Full suppression", "gcm_tx2":"FMO Full suppression removed"}

