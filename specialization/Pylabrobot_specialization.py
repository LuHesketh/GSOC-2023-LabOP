import json
import logging
import os
from typing import Dict

import sbol3
import tyto
import xarray as xr

import labop
import uml
from labop_convert.behavior_specialization import BehaviorSpecialization
from labop_convert.plate_coordinates import get_sample_list

l = logging.getLogger(__file__)
l.setLevel(logging.ERROR)


container_ontology_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../../labop/container-ontology.ttl"
)
ContO = tyto.Ontology(
    path=container_ontology_path,
    uri="https://sift.net/container-ontology/container-ontology",
)

# Map pylabrobot pipette names to compatible tipracks
#left is for Pylabrobot names
#right is for LabOp names(container ontology)
COMPATIBLE_TIPS = {
    "p20_single_gen2": ["opentrons_96_tiprack_10ul", "opentrons_96_filtertiprack_10ul"],
    "p300_single_gen2": ["opentrons_96_tiprack_300ul"],
    "p1000_single_gen2": [
        "opentrons_96_tiprack_1000ul",
        "opentrons_96_filtertiprack_1000ul",
    ],
    "p300_multi_gen2": [],
    "p20_multi_gen2": [],
    "p10_single": ["opentrons_96_tiprack_10ul", "opentrons_96_filtertiprack_10ul"],
    "p10_multi": ["opentrons_96_tiprack_10ul", "opentrons_96_filtertiprack_10ul"],
    "p50_single": [],
    "p50_multi": [],
    "p300_single": ["opentrons_96_tiprack_300ul"],
    "p300_multi": [],
    "p1000_single": [
        "opentrons_96_tiprack_1000ul",
        "opentrons_96_filtertiprack_1000ul",
    ],
}

# Map terms in the Container ontology to Hamilton API names
#its taking a LabOp term and making a correspondence to a OPENTRONS term 
#left is LabOp
#right is container API name
LABWARE_MAP = {
    ContO["Opentrons 96 Tip Rack 10 µL"]: "opentrons_96_tiprack_10ul",
    ContO["Opentrons 96 Tip Rack 300 µL"]: "opentrons_96_tiprack_300ul",
    ContO["Opentrons 96 Tip Rack 1000 µL"]: "opentrons_96_tiprack_1000ul",
    ContO["Opentrons 96 Filter Tip Rack 10 µL"]: "opentrons_96_filtertiprack_10ul",
    ContO["Opentrons 96 Filter Tip Rack 200 µL"]: "opentrons_96_filtertiprack_200ul",
    ContO["Opentrons 96 Filter Tip Rack 1000 µL"]: "opentrons_96_filtertiprack_1000ul",
    ContO[
        "Opentrons 24 Tube Rack with Eppendorf 1.5 mL Safe-Lock Snapcap"
    ]: "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
    ContO["Corning 96 Well Plate"]: "corning_96_wellplate_360ul_flat",
    ContO["Bio-Rad 96 Well PCR Plate"]: "biorad_96_wellplate_200ul_pcr",
    ContO["NEST 96 Well Plate"]: "nest_96_wellplate_200ul_flat",
}

REVERSE_LABWARE_MAP = LABWARE_MAP.__class__(map(reversed, LABWARE_MAP.items()))
