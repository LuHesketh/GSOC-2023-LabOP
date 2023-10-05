import asyncio

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends.chatterbox_backend import ChatterBoxBackend
from pylabrobot.resources import Cos_96_EZWash, Cos_96_PCR, HTF_L, Coordinate, STARLetDeck

backend =ChatterBoxBackend()
lh = LiquidHandler(backend=backend, deck=STARLetDeck())
deck=STARLetDeck()

async def __init__():
  await lh.setup()

#assign the tiprack
tip_rack = HTF_L(name="tip rack")
lh.deck.assign_child_resource(tip_rack, location=Coordinate(x=50, y=100, z=100))

#assign the PCR plate
PLASMID_plate = Cos_96_EZWash(name="PLASMID_plate")
lh.deck.assign_child_resource(PLASMID_plate, location=Coordinate(x=200, y=100, z=100))

#assign the MPE plate
MPE_plate = Cos_96_EZWash(name="MPE_plate")
lh.deck.assign_child_resource(MPE_plate, location=Coordinate(x=400, y=100, z=100))


#execute the liquid transfering
async def liquid_handling_sequence():
  await lh.pick_up_tips(tip_rack["A1","A2","A3"])
  await lh.aspirate(PLASMID_plate["A1","A2","A3"], vols=20, flow_rates=100, end_delay=0.5, offsets=Coordinate(1, 2, 3))
  await lh.dispense(MPE_plate["A1","A2","A3"], vols=20)
  await lh.return_tips()

asyncio .run(__init__())
asyncio .run(liquid_handling_sequence())

# to keep sequence running use  await asyncio.gather(liquid_handling_sequence(),backend.refill_pump())
