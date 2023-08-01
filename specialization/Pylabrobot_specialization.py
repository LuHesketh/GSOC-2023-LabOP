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

# Map terms in the Container ontology of pylabrobot and assign them to LabOP container onthology
#its taking a LabOp term and making a correspondence to a Pylabrobot term 
#left is LabOp
#right is container API name on MIcro lab star and starlet (pylabrobot)
#this is for tip carriers, tipracks and 96 well plates of various dimensions
LABWARE_MAP = {
    ContO["ML STAR Tip carrier with 5 4ml tip with filter racks landscape"]: "TIP_CAR_120BC_4mlTF_A00",
    ContO["ML STAR Tip carrier with 5 5ml tip racks landscape"]: "TIP_CAR_120BC_5mlT_A00",
    ContO["ML STAR Tip carrier for 3 Racks with 96 Tips portrait [revision A00]"]: "TIP_CAR_288_A00",
    ContO["ML STAR Tip carrier for 3 Racks with 96 Tips portrait [revision B00]"]: "TIP_CAR_288_B00",
    ContO["ML STAR Tip carrier for 3 Racks with 96 Tips portrait [revision C00]"]: "TIP_CAR_288_C00",
    ContO["ML STAR Tip carrier with 3 high volume tip with filter racks portrait [revision A00]"]: "TIP_CAR_288_HTF_A00",
    ContO["ML STAR Tip carrier with 3 high volume tip with filter racks portrait [revision B00]"]: "TIP_CAR_288_HTF_B00",
    ContO["ML STAR Tip carrier with 3 high volume tip with filter racks portrait [revision C00]"]: "TIP_CAR_288_HTF_C00",
    ContO["ML STAR Tip carrier with 3 high volume tip racks portrait [revision A00]"]: "TIP_CAR_288_HT_A00",
    ContO["ML STAR Tip carrier with 3 high volume tip racks portrait [revision B00]"]: "TIP_CAR_288_HT_B00",
    ContO["ML STAR Tip carrier with 3 high volume tip racks portrait [revision C00]"]: "TIP_CAR_288_HT_C00",
    ContO["ML STAR Tip carrier with 3 low volume tip with filter racks portrait [revision A00]"]: "TIP_CAR_288_LTF_A00",
    ContO["ML STAR Tip carrier with 3 low volume tip with filter racks portrait [revision B00]"]: "TIP_CAR_288_LTF_B00",
    ContO["ML STAR Tip carrier with 3 low volume tip with filter racks portrait [revision C00]"]: "TIP_CAR_288_LTF_C00",
    ContO["ML STAR Tip carrier with 3 low volume tip racks portrait [revision A00]"]: "TIP_CAR_288_LT_A00",
    ContO["ML STAR Tip carrier with 3 low volume tip racks portrait [revision B00]"]: "TIP_CAR_288_LT_B00",
    ContO["ML STAR Tip carrier with 3 low volume tip racks portrait [revision C00]"]: "TIP_CAR_288_LT_C00",
    ContO["ML STAR Tip carrier with 3 standard volume tip with filter racks portrait [revision A00]"]: "TIP_CAR_288_STF_A00",
    ContO["ML STAR Tip carrier with 3 standard volume tip with filter racks portrait [revision B00]"]: "TIP_CAR_288_STF_B00",
    ContO["ML STAR Tip carrier with 3 standard volume tip with filter racks portrait [revision C00]"]: "TIP_CAR_288_STF_C00",
    ContO["ML STAR Tip carrier with 3 standard volume tip racks portrait [revision A00]"]: "TIP_CAR_288_ST_A00",
    ContO["ML STAR Tip carrier with 3 standard volume tip racks portrait [revision B00]"]: "TIP_CAR_288_ST_B00",
    ContO["ML STAR Tip carrier with 3 standard volume tip racks portrait [revision C00]"]: " TIP_CAR_288_ST_C00",
    ContO["ML STAR Tip carrier with 3 50ul tip with filter racks portrait [revision C00]"]: "TIP_CAR_288_TIP_50ulF_C00",
    ContO["ML STAR Tip carrier with 3 50ul tip racks portrait [revision C00]"]: "TIP_CAR_288_TIP_50ul_C00",
    ContO["ML STAR Tip carrier with 4 empty tip rack positions landscape, with Barcode Identification [revision A00]"]: "TIP_CAR_384BC_A00",
    ContO["ML STAR Tip carrier with 4 high volume tip with filter racks for 12/16 channel instruments"]: "TIP_CAR_384BC_HTF_A00",
    ContO["ML STAR Tip carrier with 4 high volume tip racks for 12/16 channel instruments"]: "TIP_CAR_384BC_HT_A00",
    ContO["ML STAR Tip carrier with 4 low volume tip with filter racks for 12/16 channel instruments"]: "TIP_CAR_384BC_LTF_A00",
    ContO["ML STAR Tip carrier with 4 low volume tip racks for 12/16 channel instruments"]: "TIP_CAR_384BC_LT_A00",
    ContO["ML STAR Tip carrier with 4 standard volume tip with filter racks for 12/16 channel instruments"]: "TIP_CAR_384BC_STF_A00",
    ContO["ML STAR Tip carrier with 4 standard volume tip with filter racks for 12/16 channel instruments"]: "TIP_CAR_384BC_ST_A00",
    ContO["ML STAR Tip carrier with 4 50ul tip with filter racks landscape [revision A00]"]: "TIP_CAR_384BC_TIP_50ulF_A00",
    ContO["ML STAR Tip carrier with 4 50ul tip racks landscape [revision A00]"]: "TIP_CAR_384BC_TIP_50ul_A00",
    ContO["ML STAR TIP Carrier for 4 Racks with 96 Tips landscape [revision A00]"]: "TIP_CAR_384_A00",
    ContO["ML STAR Tip carrier with 4 high volume tip racks for 12/16 channel instruments, no barcode identification"]: "TIP_CAR_384_HT_A00",
    ContO["ML STAR Tip carrier with 4 low volume tip with filter racks for 12/16 channel instruments, no barcode identification"]: "TIP_CAR_384_LTF_A00",
    ContO["ML STAR Tip carrier with 4 low volume tip racks for 12/16 channel instruments, no barcode identification"]: "TIP_CAR_384_LT_A00",
    ContO["ML STAR Tip carrier with 4 standard volume tip with filter racks for 12/16 channel instruments, no barcode identification  [revision A00] "]: "TIP_CAR_384_STF_A00",
    ContO["ML STAR Tip carrier with 4 standard volume tip racks for 12/16 channel instruments, no barcode identification  [revision A00]"]: "TIP_CAR_384_ST_A00",
    ContO["ML STAR Tip carrier with 4 50ul tip with filter racks landscape [revision A00]"]: "TIP_CAR_384_TIP_50ulF_A00",
    ContO["ML STAR Tip carrier with 4 50ul tip racks landscape [revision A00]"]: "TIP_CAR_384_TIP_50ul_A00",
    ContO["ML STAR Tip Carrier for 5 Racks with 96 Tips landscape [revision A00]"]: "TIP_CAR_480",
    ContO["NEST 96 Well Plate"]: "nest_96_wellplate_200ul_flat",





}

REVERSE_LABWARE_MAP = LABWARE_MAP.__class__(map(reversed, LABWARE_MAP.items()))

#this class serves for channels and modules that the machine has
class pylabrobotSpecialization(BehaviorSpecialization):

    EQUIPMENT = {
        "p20_single_gen2": sbol3.Agent("p20_single_gen2", name="P20 Single GEN2"),
        "p300_single_gen2": sbol3.Agent("p300_single_gen2", name="P300 Single GEN2"),
        "p1000_single_gen2": sbol3.Agent("p1000_single_gen2", name="P1000 Single GEN2"),
        "p300_multi_gen2": sbol3.Agent("p300_multi_gen2", name="P300 Multi GEN2"),
        "p20_multi_gen2": sbol3.Agent("p20_multi_gen2", name="P20 Multi GEN2"),
        "p10_single": sbol3.Agent("p10_single", name="P10 Single"),
        "p10_multi": sbol3.Agent("p10_multi", name="P10 Multi"),
        "p50_single": sbol3.Agent("p50_single", name="P50 Single"),
        "p50_multi": sbol3.Agent("p50_multi", name="P50 Multi"),
        "p300_single": sbol3.Agent("p300_single", name="P300 Single"),
        "p300_multi": sbol3.Agent("p300_multi", name="P300 Multi"),
        "p1000_single": sbol3.Agent("p1000_single", name="P1000 Single"),
        "temperature_module": sbol3.Agent(
            "temperature_module", name="Temperature Module GEN1"
        ),
        "tempdeck": sbol3.Agent(
            "temperature_module", name="Temperature Module GEN1"
        ),

        "temperature_module_gen2": sbol3.Agent(
            "temperature_module_gen2", name="Temperature Module GEN2"
        ),
        "magnetic_module": sbol3.Agent(
            "magdeck", name="Magnetic Module GEN1"
        ),
        "magnetic_module_gen2": sbol3.Agent(
            "magnetic_module_gen2", name="Magnetic Module GEN2"
        ),
        "thermocycler_module": sbol3.Agent(
            "thermocycler_module", name="Thermocycler Module"
        ),
        "thermocycler": sbol3.Agent(
            "thermocycler_module", name="Thermocycler Module"
        ),
        "MPE2": sbol3.Agent(
            "MPE2_module", name="MPE pressure pump module"
        ),
        
    }
        

    def __init__(
        self, filename, resolutions: Dict[sbol3.Identified, str] = None
    ) -> None:
        super().__init__()
        self.resolutions = resolutions
        self.var_to_entity = {}
        self.script = ""
        self.script_steps = []
        self.markdown = ""
        self.markdown_steps = []
        self.apilevel = "2.11"
        self.configuration = {}
        self.filename = filename

        # Needed for using container ontology
        self.container_api_addl_conditions = "(cont:availableAt value <https://sift.net/container-ontology/strateos-catalog#Strateos>)"
