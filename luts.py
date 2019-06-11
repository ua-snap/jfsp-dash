"""
Lookup tables with key names and human-readable names
"""
# pylint: disable=C0103

zones = {
    "ChugachNationalForest": "ChugachNationalForest",
    "CopperRiverArea": "CopperRiverArea",
    "DeltaArea": "DeltaArea",
    "FairbanksArea": "FairbanksArea",
    "GalenaZone": "GalenaZone",
    "KenaiKodiakArea": "KenaiKodiakArea",
    "MatSuArea": "MatSuArea",
    "MilitaryZone": "MilitaryZone",
    "SouthwestArea": "SouthwestArea",
    "TananaZone": "TananaZone",
    "TokArea": "TokArea",
    "UpperYukonZone": "UpperYukonZone",
}

ecoregions = {
    "AlaskaRangeTransition":"AlaskaRangeTransition",
    "AleutianMeadows":"AleutianMeadows",
    "ArcticTundra":"ArcticTundra",
    "BeringTaiga":"BeringTaiga",
    "BeringTundra":"BeringTundra",
    "CoastalRainforests":"CoastalRainforests",
    "CoastMountainsTransition":"CoastMountainsTransition",
    "IntermontaneBoreal":"IntermontaneBoreal",
    "PacificMountainsTransition":"PacificMountainsTransition"
}

scenarios = {"rcp45": "rcp45", "rcp60": "rcp60", "rcp85": "rcp85"}

models = {
    "CCSM4": "CCSM4",
    "GFDL-CM3": "GFDL-CM3",
    "GISS-E2-R": "GISS-E2-R",
    "IPSL-CM5A-LR": "IPSL-CM5A-LR",
    "MRI-CGCM3": "MRI-CGCM3",
}

# Only future
treatment_options = {"gcm_tx0":"Status quo", "gcm_tx1":"More FMO Full suppression", "gcm_tx2":"FMO Full suppression removed"}

