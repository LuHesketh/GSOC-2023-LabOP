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
from labop_convert.pylabrobot.pylabrobot_specialization import PylabrobotSpecialization


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
    
    water = sbol3.Component(
        "MLQ_water", "https://identifiers.org/pubchem.substance:24901740"
    )
    water.name = "MLQ water for plasmid retrieving"

    doc.add(PLASMID)
    doc.add(Ethanol)
    doc.add(water)
    
    
    PROTOCOL_NAME = "initialize_PCR_PURIFICATION_PROTOCOL"
    PROTOCOL_LONG_NAME="initialize_PCR_PURIFICATION_PROTOCOL"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
 protocol to initialize transfer plasmid and ethanol to a MPE container for ethanol washes
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
            "ethanol_for_DNA_washes",
            name="ethanol for DNA washes",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )

    water_container = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "WATER_For_cleanup_after_ethanol_washing_steps",
            name="water_container",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )


    MPE_container = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "MPE_container",
            name="MPE_container",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"
            },
        ),
    )
    shaking_incubator = sbol3.Component("shaking_incubator", "")
    shaking_incubator.name = "Shaking incubator"   
    shaking_incubator = protocol.primitive_step(
        "EmptyContainer",
        specification=labop.ContainerSpec(
            "shaking_incubator",
            name="shaking_incubator",
            queryString="cont:StockReagent",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#"

            },
            
        ),
    )

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

    provision = protocol.primitive_step(
        "Provision",
        resource=water,
        destination=water_container.output_pin("samples"),
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

    output4 = protocol.designate_output(
        "shaking_incubator",
        "http://bioprotocols.org/labop#SampleArray",
        source=shaking_incubator.output_pin("samples"),

    )

    output5 = protocol.designate_output(
        "water_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=water_container.output_pin("samples"),

    )
    return protocol

#here the PLASMID would already be inside the MPE2 and the pressure pump would be activated
#pushing the PLASMID through the collumns inside the container
#a sub-protocol should be made to represent this step
def generate_MPE_subprotocol(doc):
    protocol = labop.Protocol("MPE_overpressure")
    doc.add(protocol)
    # mpe2_filter_plate_placed,
    #         mpe2_clamp_filter_plate,
    #         mpe2_start_mpe_vacuum,
    #         mpe2_process_filter_to_waste_container,
    #         mpe2_stop_vacuum,
    #         mpe2_filter_plate_removed
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


    
    PROTOCOL_NAME = "PCR_purification"
    PROTOCOL_LONG_NAME="PCR_purification_with_pressurepump_MPE2"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
This DNA cleanup/purification protocol is to be executed using 2 HAMILTON modules. They are:
       
   *# MPE2- Air pressure module. to be used to push/process the liquids through a filter
   *# HHS/Heater shaker - to shake the final product at 30 celcius (necessary final step)    
            
    #    - robot grab tip
    #    - use tip to transport DNA from DNA plate to sample filter plate (later ejecting the tip)
    #    - process DNA through filter 
    #     - Add ethanol and do 2 washing steps through filter plate using the MPE2
    #     - add water to the filter plate
    #     - move filter plate to heater shaker using robotic grippers
    #     - do shaking steps
    #     - retrieve plate manually from heater shaker    """
    doc.add(protocol)
    
    initialize_subprotocol = generate_initialize_subprotocol(doc)
    MPE_subprotocol_defn = generate_MPE_subprotocol(doc)

    initialization = protocol.primitive_step(
        initialize_subprotocol
    )

    MPE_subprotocol = protocol.primitive_step( #use this to call out the sub protocol
        MPE_subprotocol_defn
    )

    plan_mapping = serialize_sample_format(
            xr.DataArray(
                [
                    [
                        [[(20.0 if source_aliquot == target_aliquot else 0.0) for target_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]]]
                        for source_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
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
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("MPE_container").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan = labop.SampleMap(
        sources=[initialization.output_pin("PLASMID_container")],
        targets=[initialization.output_pin("MPE_container")],
        values=plan_mapping,
    )

    #transfer plasmid to MPE PLATE
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("PLASMID_container"),
        destination=initialization.output_pin("MPE_container"),
        plan=plan,
        amount=sbol3.Measure(10, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

    plan_mapping1 = serialize_sample_format(
            xr.DataArray(
                [
                    [
                        [[(20.0 if source_aliquot == target_aliquot else 0.0) for target_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]]]
                        for source_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
                    ]
                ],
                dims=(
                    f"source_{Strings.CONTAINER}",
                    f"source_{Strings.LOCATION}",
                    f"target_{Strings.CONTAINER}",
                    f"target_{Strings.LOCATION}",
                ),
                coords={
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("Ethanol_container").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_container").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan1 = labop.SampleMap(
        sources=[initialization.output_pin("Ethanol_container")],
        targets=[initialization.output_pin("MPE_container")],
        values=plan_mapping1,
    )

    #transfer ethanol to MPE PLATE for first ethanol wash
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("Ethanol_container"),
        destination=initialization.output_pin("MPE_container"),
        plan=plan1,
        amount=sbol3.Measure(200, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan2 = labop.SampleMap(
        sources=[initialization.output_pin("Ethanol_container")],
        targets=[initialization.output_pin("MPE_container")],
        values=plan_mapping1,
    )

    #second ethanol wash ethanol transfer 
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("Ethanol_container"),
        destination=initialization.output_pin("MPE_container"),
        plan=plan2,
        amount=sbol3.Measure(200, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

    plan_mapping3 = serialize_sample_format(
            xr.DataArray(
                [
                    [
                        [[(20.0 if source_aliquot == target_aliquot else 0.0) for target_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]]]
                        for source_aliquot in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
                    ]
                ],
                dims=(
                    f"source_{Strings.CONTAINER}",
                    f"source_{Strings.LOCATION}",
                    f"target_{Strings.CONTAINER}",
                    f"target_{Strings.LOCATION}",
                ),
                coords={
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("water_container").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_container").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan3= labop.SampleMap(
        sources=[initialization.output_pin("water_container")],
        targets=[initialization.output_pin("MPE_container")],
        values=plan_mapping3,
    )

    #transfer water to MPE plate for plasmid retrieving
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=[initialization.output_pin("water_container")],
        destination=[initialization.output_pin("MPE_container")],
        plan=plan3,
        amount=sbol3.Measure(20, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

    #move filter plate located in the MPE to heater shaker incubator using robotic gripper

    #shake samples to restore purified PLASMID and manually retrive final product from heater shaker
    incubate = protocol.primitive_step(
    "Incubate",
    location= initialization.output_pin("shaking_incubator"),
    duration=sbol3.Measure(3, OM.minute),
    temperature=sbol3.Measure(30, OM.degree_Celsius),
    shakingFrequency=sbol3.Measure(250, OM.hertz),
    ) 
    
    protocol.to_dot().render(os.path.join(OUT_DIR, f"{filename}-protocol-graph"))

    protocol_file = os.path.join(OUT_DIR, f"{filename}-protocol.nt")
    with open(protocol_file, "w") as f:
        print(f"Saving protocol [{protocol_file}].")
        f.write(doc.write_string(sbol3.SORTED_NTRIPLES).strip())



    ee = labop.ExecutionEngine(
        out_dir=OUT_DIR,
        failsafe=False,
        specializations=[PylabrobotSpecialization(filename=os.path.join(OUT_DIR, f"{filename}-pylabrobot.py"))],
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