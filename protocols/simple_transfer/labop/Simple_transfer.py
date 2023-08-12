import argparse
import json
import os
import shutil
import subprocess
import sys

import sbol3
import labop
from labop.data import serialize_sample_format
from labop.strings import Strings
import xarray as xr
from tyto import OM
import tyto

from labop_convert.Pylabrobot import Pylabrobot_specialization

filename = "".join(__file__.split(".py")[0].split("/")[-1:])
OUT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

def generate_initialize_subprotocol(doc):
    protocol = labop.Protocol("initialize")
    doc.add(protocol)

    # create the materials to be provisioned
    PLASMID = sbol3.Component(
        "ddH2O", "https://identifiers.org/pubchem.substance:24901740"
    )
    PLASMID.name = "DNA TO BE PURIFIEd"

    doc.add(PLASMID)    
    
    PROTOCOL_NAME = "initialize_simple_transfer"
    PROTOCOL_LONG_NAME="initialize_simple_transfer"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
 protocol to initialize transfer plasmid and ethanol to a MPE container
    """
    
    doc.add(protocol)

	
    load_Tiprack_on_deck = protocol.primitive_step("LoadRackOnInstrument", 
        rack=labop.ContainerSpec("tiprack", queryString="cont:HTF_L"),
        coordinates="(x=100, y=100, z=100)"
    )

    PLASMID_plate = protocol.primitive_step("LoadContainerOnInstrument",
            specification=labop.ContainerSpec("PLASMID_plate",
            name="PLASMID_plate",
            queryString="cont:Cos_96_PCR",
            prefixMap={
                "cont": "https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/resources/corning_costar/plates.py"
            },
        ),
        slots="(x=200, y=100, z=100)"
    )

    MPE_plate = protocol.primitive_step("LoadContainerOnInstrument",
            specification=labop.ContainerSpec("MPE_plate",
            name="MPE_plate",
            queryString="cont:Cos_96_EZWash",
            prefixMap={
                "cont": "https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/resources/corning_costar/plates.py"
            },
        ),
        slots="(x=400, y=100, z=100)"
    )
    
    provision = protocol.primitive_step(
        "Provision",
        resource=PLASMID,
        destination=PLASMID_plate.output_pin("samples"),
        amount=sbol3.Measure(30, OM.microliter),
    )
        
    output1 = protocol.designate_output(
        "PLASMID_plate",
        "http://bioprotocols.org/labop#SampleArray",
        source=PLASMID_plate.output_pin("samples"),
    )

    output2 = protocol.designate_output(
        "MPE_plate",
        "http://bioprotocols.org/labop#SampleArray",
        source=MPE_plate.output_pin("samples"),
    )		


     ### the provision step creates the reagents as objects and attaches them to the containers where they'll be located


    return protocol


def generate_protocol():
    import labop
    from labop_convert import DefaultBehaviorSpecialization

    doc = sbol3.Document()
    sbol3.set_namespace("http://labop.io/")

    #############################################
    # Import the primitive libraries
    # print("Importing libraries")
    labop.import_library("liquid_handling")
    # print("... Imported liquid handling")
    labop.import_library("plate_handling")
    # print("... Imported plate handling")
    labop.import_library("sample_arrays")
    # print("... Imported sample arrays")


    
    PROTOCOL_NAME = "simple_transfer"
    PROTOCOL_LONG_NAME="simple_transfer"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
 protocol to transfer plasmid and ethanol to a MPE container
    """
    doc.add(protocol)
    
    initialize_subprotocol = generate_initialize_subprotocol(doc)

    initialization = protocol.primitive_step(
        initialize_subprotocol
    )


    plan_mapping = serialize_sample_format(
            xr.DataArray(
                [
                    [
                        [[(20.0 if source_aliquot == target_aliquot else 0.0) for target_aliquot in ["A1", "A2", "A3"]]]
                        for source_aliquot in ["A1", "A2", "A3"]
                    ]
                ],
                dims=(
                    f"source_{Strings.CONTAINER}",
                    f"source_{Strings.LOCATION}",
                    f"target_{Strings.CONTAINER}",
                    f"target_{Strings.LOCATION}",
                ),
                coords={
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("PLASMID_plate").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3"],
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_plate").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan = labop.SampleMap(
        sources=[initialization.output_pin("PLASMID_plate")],
        targets=[initialization.output_pin("MPE_plate")],
        values=plan_mapping,
    )

    # The outputs of the create_source and create_target calls will be identical
    # to the source_array and target_array.  They will not be on the output pin
    # until execution, but the SampleMap needs to reference them.
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("PLASMID_plate"),
        destination=initialization.output_pin("MPE_plate"),
        plan=plan,
        amount=sbol3.Measure(20, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

    protocol.to_dot().render(os.path.join(OUT_DIR, f"{filename}-protocol-graph"))

    protocol_file = os.path.join(OUT_DIR, f"{filename}-protocol.nt")
    with open(protocol_file, "w") as f:
        print(f"Saving protocol [{protocol_file}].")
        f.write(doc.write_string(sbol3.SORTED_NTRIPLES).strip())



    ee = labop.ExecutionEngine(
        out_dir=OUT_DIR,
        failsafe=False,
        specializations=[pylabrobotSpecialization()],
        sample_format="xarray"
    )

    execution = ee.execute(
        protocol,
        sbol3.Agent("test_agent"),
        id="test_execution",
        parameter_values=[],
    )
    # ee.prov_observer.to_dot().render(os.path.join(OUT_DIR, f"{filename}-sample-graph"))



if __name__ == "__main__":
    generate_protocol()
