import asyncio
import pylabrobot

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import STAR

from pylabrobot.resources.hamilton import STARLetDeck

backend = STAR()
lh = LiquidHandler(backend=backend, deck=STARLetDeck())

await lh.setup()

from pylabrobot.resources import (
    TIP_CAR_480_A00,
    PLT_CAR_L5AC_A00,
    Cos_96_DW_1mL,
    HTF_L
)

tip_car = TIP_CAR_480_A00(name='tip carrier')
tip_car[0] = HTF_L(name='tips_01')

lh.deck.assign_child_resource(tip_car, rails=3)

lh.deck.assign_child_resource(plt_car, rails=15)

tiprack = lh.get_resource("tips_01")
await lh.pick_up_tips(tiprack["A1:C1"])

plate = lh.get_resource("plate_01")
await lh.aspirate(plate["A1:C1"], vols=[100.0, 50.0, 200.0])

await lh.dispense(plate["D1:F1"], vols=[100.0, 50.0, 200.0])

await lh.drop_tips(tiprack["A1:C1"])

await lh.stop()


