
import asyncio

from pylabrobot.liquid_handling import LiquidHandler, STAR
from pylabrobot.resources import Cos_96_EZWash, HTF_L, Coordinate, STARLetDeck

async def __init__():
  backend = STAR()
  lh = LiquidHandler(backend=backend, deck=STARLetDeck())
  await lh.setup()
  tip_rack = HTF_L(name="tip rack")

lh.deck.assign_child_resource(tip_rack, location=Coordinate(x=100, y=100, z=100))
plate = Cos_96_EZWash(name="plate")
lh.deck.assign_child_resource(plate, location=Coordinate(x=200, y=100, z=100))

async def liquid_handling_sequence():
    await lh.pick_up_tips(tip_rack["A1:A2"])
    await lh.aspirate(plate["A1:A2"], vols=100, flow_rates=100, end_delay=0.5,
offsets=Coordinate(1, 2, 3))
    await lh.dispense(plate["A1:A2"], vols=100)
    await lh.return_tips()

    await asyncio.gather(liquid_handling_sequence(),backend.refill_pump())



