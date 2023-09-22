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
    
    instrument = sbol3.Agent('Hamilton_STARlet')

    # create the materials to be provisioned
    PCR = sbol3.Component(
        "ddH2O", "https://identifiers.org/pubchem.substance:24901740"
    )
    PCR.name = "PCR samples TO BE PURIFIEd"

    Ethanol = sbol3.Component(
        "Ethanol_70",
        "https://nanocym.com/wp-content/uploads/2018/07/NanoCym-All-Datasheets-.pdf",
    )
    Ethanol.name = "Ethanol 70%, ideal for PCR PUTIFICATION"
    
    water = sbol3.Component(
        "MLQ_water", "https://identifiers.org/pubchem.substance:24901740"
    )
    water.name = "MLQ water for PCR retrieving"

    doc.add(PCR)
    doc.add(Ethanol)
    doc.add(water)
    doc.add(instrument)

    
    PROTOCOL_NAME = "initialize_PCR_PURIFICATION_PROTOCOL"
    PROTOCOL_LONG_NAME="initialize_PCR_PURIFICATION_PROTOCOL"
    protocol = labop.Protocol(PROTOCOL_NAME)
    protocol.name = PROTOCOL_LONG_NAME
    protocol.version = "1.2"
    protocol.description = """
 protocol to initialize transfer PCR and ethanol to a MPE container for ethanol washes
    """

    doc.add(protocol)



    Ethanol_container = protocol.primitive_step(
        "LoadContainerOnInstrument",
        specification=labop.ContainerSpec(
            "Ethanol_container",
            name="Ethanol container",
            queryString="cont:Corning Costar 1 mL deep well plate with 96 wells",
            prefixMap={
                "cont": "https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/resources/corning_costar/plates.py"
            },
        ),
        slots="(x=200, y=100, z=100)", instrument = instrument

    )

    load_Tiprack_on_deck = protocol.primitive_step(
        "LoadRackOnInstrument",
        rack=labop.ContainerSpec("tiprack", queryString="cont:HTF_L"),
        coordinates="(x=100, y=100, z=100)",
    )

    PCR_plate = protocol.primitive_step(
        "LoadContainerOnInstrument",
        specification=labop.ContainerSpec(
            "PCR_plate",
            name="PCR_plate",
            queryString="cont:Corning 96 Well Plate 360 uL Flat",
            prefixMap={
                "cont": "https://sift.net/container-ontology/container-ontology#Corning96WellPlate360uLFlat"
            },
        ),
        slots="(x=200, y=100, z=100)", instrument = instrument
    )

    water_container = protocol.primitive_step(
        "LoadContainerOnInstrument",
        specification=labop.ContainerSpec(
            "water_container",
            name="water container",
            queryString="cont:Corning 96 Well Plate 360 uL Flat",
            prefixMap={
                "cont": "https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/resources/corning_costar/plates.py"
            },
        ),
        slots="(x=400, y=100, z=100)", instrument = instrument
    )

    MPE_plate = protocol.primitive_step(
        "LoadContainerOnInstrument",
        specification=labop.ContainerSpec(
            "MPE_plate",
            name="MPE_plate",
            queryString="cont:Corning Costar filter plate with 96 wells",
            prefixMap={
                "cont": "https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/resources/corning_costar/plates.py"
            },
        ),
        slots="(x=400, y=100, z=100)", instrument = instrument
    )

    provision = protocol.primitive_step(
        "Provision",
        resource=PCR,
        destination=PCR_plate.output_pin("samples"),
        amount=sbol3.Measure(30, OM.microliter),
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
        "PCR_plate",
        "http://bioprotocols.org/labop#SampleArray",
        source=PCR_plate.output_pin("samples"),
    )

    output2 = protocol.designate_output(
        "MPE_plate",
        "http://bioprotocols.org/labop#SampleArray",
        source=MPE_plate.output_pin("samples"),
    )

    output3 = protocol.designate_output(
        "Ethanol_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=Ethanol_container.output_pin("samples"),
    )

    output4 = protocol.designate_output(
        "water_container",
        "http://bioprotocols.org/labop#SampleArray",
        source=water_container.output_pin("samples")

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

    output5 = protocol.designate_output(
        "shaking_incubator",
        "http://bioprotocols.org/labop#SampleArray",
        source=shaking_incubator.output_pin("samples"))

    return protocol

#here the PCR samples would already be inside the MPE2 and the pressure pump would be activated
def generate_MPE_subprotocol(doc: sbol3.Document):
    import labop
    subprotocol = labop.Protocol("Activate_Air_pump")


    doc.add(subprotocol)
    return subprotocol

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
    labop.import_library(r"C:\Users\Luiza\GSOC-2023-LabOP\pylabrobot_convert\plate_handling.ttl")
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
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("PCR_plate").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                    f"source_{Strings.CONTAINER}": [initialization.output_pin("MPE_plate").name],
                    f"source_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan = labop.SampleMap(
        sources=[initialization.output_pin("PCR_plate")],
        targets=[initialization.output_pin("MPE_plate")],
        values=plan_mapping,
    )

    #transfer PCR to MPE PLATE
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("PCR_plate"),
        destination=initialization.output_pin("MPE_plate"),
        plan=plan,
        amount=sbol3.Measure(10, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

#############################################
#call out MPE SUBPROTOCOL

    Activate_Air_pump = protocol.primitive_step( 
        MPE_subprotocol_defn
    )
    
#######################################

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
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_plate").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan1 = labop.SampleMap(
        sources=[initialization.output_pin("Ethanol_container")],
        targets=[initialization.output_pin("MPE_plate")],
        values=plan_mapping1,
    )

    #transfer ethanol to MPE PLATE for first ethanol wash
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("Ethanol_container"),
        destination=initialization.output_pin("MPE_plate"),
        plan=plan1,
        amount=sbol3.Measure(200, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

#############################################
#call out MPE SUBPROTOCOL

    Activate_Air_pump = protocol.primitive_step( 
        MPE_subprotocol_defn
    )



    # The SampleMap specifies the sources and targets, along with the mappings.
    plan2 = labop.SampleMap(
        sources=[initialization.output_pin("Ethanol_container")],
        targets=[initialization.output_pin("MPE_plate")],
        values=plan_mapping1,
    )

    #second ethanol wash ethanol transfer 
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=initialization.output_pin("Ethanol_container"),
        destination=initialization.output_pin("MPE_plate"),
        plan=plan2,
        amount=sbol3.Measure(200, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

#############################################
#call out MPE SUBPROTOCOL

    Activate_Air_pump = protocol.primitive_step( 
        MPE_subprotocol_defn
    )


################################################

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
                    f"target_{Strings.CONTAINER}": [initialization.output_pin("MPE_plate").name],
                    f"target_{Strings.LOCATION}": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
                },
            )
        )

    # The SampleMap specifies the sources and targets, along with the mappings.
    plan3= labop.SampleMap(
        sources=[initialization.output_pin("water_container")],
        targets=[initialization.output_pin("MPE_plate")],
        values=plan_mapping3,
    )

    #transfer water to MPE plate for PCR retrieving
    transfer_by_map = protocol.primitive_step(
        "TransferByMap",
        source=[initialization.output_pin("water_container")],
        destination=[initialization.output_pin("MPE_plate")],
        plan=plan3,
        amount=sbol3.Measure(20, tyto.OM.milliliter),
        temperature=sbol3.Measure(30, tyto.OM.degree_Celsius),
    )

#############################################
#call out MPE SUBPROTOCOL

    Activate_Air_pump = protocol.primitive_step( 
        MPE_subprotocol_defn
    )


################################################



    #move filter plate located in the MPE to heater shaker incubator using robotic gripper

    #shake samples to restore purified PCR and manually retrive final product from heater shaker
    incubate = protocol.primitive_step(
    "Incubate",
    location= initialization.output_pin("shaking_incubator"),
    duration=sbol3.Measure(3, OM.minute),
    temperature=sbol3.Measure(30, OM.degree_Celsius),
    shakingFrequency=sbol3.Measure(250, OM.hertz),
    ) 
    
    #protocol.to_dot().render(os.path.join(OUT_DIR, f"{filename}-protocol-graph"))

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