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

    Ethanol = sbol3.Component(
        "silica_beads",
        "https://nanocym.com/wp-content/uploads/2018/07/NanoCym-All-Datasheets-.pdf",
    )
    Ethanol.name = "Ethanol 70%, ideal for PCR/PLASMID PUTIFICATION"
    

    

    doc.add(PLASMID)
    doc.add(Ethanol)
    
    
    PROTOCOL_NAME = "initialize_simple_transfer"
    PROTOCOL_LONG_NAME="initialize_simple_transfer"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
 protocol to initialize transfer plasmid and ethanol to a MPE container
    """
    
    doc.add(protocol)
    
        
    PLASMID_container = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "PLASMID",
            name="PLASMID",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )


    Ethanol_container = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "sulforhodamine_calibrant",
            name="Sulforhodamine 101 calibrant",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )
        
    MPE_container = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "PLASMID_container",
            name="LASMID_container",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )

     ### the provision step creates the reagents as objects and attaches them to the containers where they'll be located

    provision = protocol.primitive_step(
        "Provision",
        resource=PLASMID,
        destination=PLASMID_container.output_pin("samples"),
        amount=sbol3.Measure(5000, OM.microliter),
        
        
    )
    provision = protocol.primitive_step(
        "Provision",
        resource=Ethanol,
        destination=Ethanol_container.output_pin("samples"),
        amount=sbol3.Measure(5000, OM.microliter),
    )

    output1 = protocol.designate_output(
        "PLASMID_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=PLASMID_container.output_pin("samples"),
    )

    output2 = protocol.designate_output(
        "MPE_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=MPE_container.output_pin("samples"),
    )

    output3 = protocol.designate_output(
        "Ethanol_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=Ethanol_container.output_pin("samples"),
    )
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
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("PLASMID_container").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3"],
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_container").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan = labop.SampleMap(
        sources=[initialization.output_pin("PLASMID_container")],
        targets=[initialization.output_pin("MPE_container")],
        values=plan_mapping,
    )

    # The outputs of the create_source and create_target calls will be identical
    # to the source_array and target_array.  They will not be on the output pin
    # until execution, but the SampleMap needs to reference them.
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("PLASMID_container"),
        destination=initialization.output_pin("MPE_container"),
        plan=plan,
        amount=sbol3.Measure(20, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )


    ### Now that you have the containers and reagents to be used you provide the locations in the labware(we used a 96 well plate)
    # PLASMID_plate = protocol.primitive_step(
    #     "PlateCoordinates",
    #     source=initialization.output_pin("PLASMID_container"),
    #     coordinates="A1:A3",
    # )
    # MPE2_pressure_pump = protocol.primitive_step(
    #     "PlateCoordinates",
    #     source=initialization.output_pin("MPE_container"),
    #     coordinates="A1:A3",
    # )

    # Ethanol_plate = protocol.primitive_step(
    #     "PlateCoordinates",
    #     source=initialization.output_pin("Ethanol_container"),
    #     coordinates="A1:A3",
    # )

    # ### Transfer PLASMID from source plate to MPE2 plate
    # transfer_PLASMID = protocol.primitive_step(
    #     "Transfer",
    #     source=PLASMID_plate.output_pin("samples"),
    #     destination=MPE2_pressure_pump.output_pin("samples"),
    #     amount=sbol3.Measure(20, OM.microlitre),


    # ### Transfer Ethanol from source plate to MPE2 plate for Ethanol washes

    # )
    # transfer_ethanol = protocol.primitive_step(
    #     "Transfer",
    #     source=Ethanol_plate.output_pin("samples"),
    #     destination=MPE2_pressure_pump.output_pin("samples"),
    #     amount=sbol3.Measure(200, OM.microlitre),
    # )

    protocol.to_dot().render(os.path.join(OUT_DIR, f"{filename}-protocol-graph"))

    protocol_file = os.path.join(OUT_DIR, f"{filename}-protocol.nt")
    with open(protocol_file, "w") as f:
        print(f"Saving protocol [{protocol_file}].")
        f.write(doc.write_string(sbol3.SORTED_NTRIPLES).strip())



    ee = labop.ExecutionEngine(
        out_dir=OUT_DIR,
        failsafe=False,
        # specializations=[PyHamiltonSpecialization()]
        sample_format="xarray"
    )

    execution = ee.execute(
        protocol,
        sbol3.Agent("test_agent"),
        id="test_execution",
        parameter_values=[],
    )
    ee.prov_observer.to_dot().render(os.path.join(OUT_DIR, f"{filename}-sample-graph"))



if __name__ == "__main__":
    generate_protocol()
